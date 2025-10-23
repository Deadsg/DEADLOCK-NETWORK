use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program_error::ProgramError,
    pubkey::Pubkey,
    sysvar::{clock::Clock, Sysvar},
};
use borsh::{BorshDeserialize, BorshSerialize};
use sha2::{Digest, Sha256};

// Declare and export the program's entrypoint
entrypoint!(process_instruction);

// Define the program's instructions
#[derive(BorshSerialize, BorshDeserialize, Debug, PartialEq)]
pub enum DeadsgoldInstruction {
    /// Mined a new block
    ///
    /// Accounts:
    /// 0. `[signer]` The miner's wallet
    /// 1. `[writable]` The program's state account (PDA)
    ///
    /// Data:
    /// - nonce: u64
    /// - hash: [u8; 32]
    Mine { nonce: u64, hash: [u8; 32] },

    /// Initialize the program's state
    ///
    /// Accounts:
    /// 0. `[signer]` The initializer's wallet
    /// 1. `[writable]` The program's state account (PDA)
    ///
    /// Data:
    /// - target_block_time: u64
    /// - kappa_h: u64
    /// - kappa_s: u64
    /// - alpha_d: u64
    /// - rho: u64
    /// - initial_difficulty: u64
    Initialize {
        target_block_time: u64,
        kappa_h: u64,
        kappa_s: u64,
        alpha_d: u64,
        rho: u64,
        initial_difficulty: u64,
    },
}

pub const SCALING_FACTOR: u64 = 1_000_000;

// Define the program's state
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct ProgramState {
    pub mined_count: u64,
    pub difficulty: u64, // Current difficulty (D_t)
    pub target_block_time: u64, // T* (target block time in seconds)
    pub observed_block_times: [u64; 100], // T_obs (window for observed block time, W=100)
    pub observed_block_time_ptr: u8, // Pointer for circular buffer
    pub kappa_h: u64, // κ_h (hash power coefficient, scaled)
    pub kappa_s: u64, // κ_s (stake coefficient, scaled)
    pub alpha_d: u64, // α_d (difficulty smoothing exponent, scaled)
    pub rho: u64, // ρ (blocks_per_time_unit, scaled)
    pub last_block_timestamp: i64, // Timestamp of the last mined block
}

impl Default for ProgramState {
    fn default() -> Self {
        Self {
            mined_count: 0,
            difficulty: 0,
            target_block_time: 0,
            observed_block_times: [0; 100],
            observed_block_time_ptr: 0,
            kappa_h: 0,
            kappa_s: 0,
            alpha_d: 0,
            rho: 0,
            last_block_timestamp: 0,
        }
    }
}

// Program entrypoint's implementation
pub fn process_instruction(
    program_id: &Pubkey, // Public key of the account the program was loaded into
    accounts: &[AccountInfo], // All accounts required to run the instruction
    instruction_data: &[u8], // Serialized instruction data
) -> ProgramResult {
    msg!("Deadsgold Solana Program Entrypoint");

    let instruction = DeadsgoldInstruction::try_from_slice(instruction_data)
        .map_err(|_| ProgramError::InvalidInstructionData)?;

    match instruction {
        DeadsgoldInstruction::Initialize {
            target_block_time,
            kappa_h,
            kappa_s,
            alpha_d,
            rho,
            initial_difficulty,
        } => {
            msg!("Instruction: Initialize");

            let accounts_iter = &mut accounts.iter();
            let initializer_account = next_account_info(accounts_iter)?;
            let program_state_account = next_account_info(accounts_iter)?;

            // Ensure the initializer is a signer
            if !initializer_account.is_signer {
                return Err(ProgramError::MissingRequiredSignature);
            }

            // Ensure the program state account is writable and owned by the program
            if !program_state_account.is_writable || program_state_account.owner != program_id {
                return Err(ProgramError::IncorrectProgramId);
            }

            // Check if the program state account is already initialized
            let mut program_state = ProgramState::try_from_slice(&program_state_account.data.borrow())
                .unwrap_or_default();

            if program_state.mined_count != 0 || program_state.difficulty != 0 {
                msg!("Program state already initialized.");
                return Err(ProgramError::Custom(2)); // Custom error for already initialized
            }

            // Initialize program state
            program_state.mined_count = 0;
            program_state.difficulty = initial_difficulty;
            program_state.target_block_time = target_block_time;
            program_state.kappa_h = kappa_h;
            program_state.kappa_s = kappa_s;
            program_state.alpha_d = alpha_d;
            program_state.rho = rho;
            program_state.last_block_timestamp = 0; // Will be updated on first mine

            // Serialize and save the updated state
            program_state.serialize(&mut &mut program_state_account.data.borrow_mut()[..])?;
        }
        DeadsgoldInstruction::Mine { nonce, hash } => {
            msg!("Instruction: Mine");
            msg!("Nonce: {}", nonce);
            msg!("Hash: {:?}", hash);

            let accounts_iter = &mut accounts.iter();
            let miner_account = next_account_info(accounts_iter)?;
            let program_state_account = next_account_info(accounts_iter)?;
            let clock_account = next_account_info(accounts_iter)?;

            // Ensure the miner is a signer
            if !miner_account.is_signer {
                return Err(ProgramError::MissingRequiredSignature);
            }

            // Ensure the program state account is writable and owned by the program
            if !program_state_account.is_writable || program_state_account.owner != program_id {
                return Err(ProgramError::IncorrectProgramId);
            }

            // Ensure clock account is the correct sysvar
            if clock_account.key != &solana_program::sysvar::clock::ID {
                return Err(ProgramError::InvalidAccountData);
            }

            // Deserialize program state
            let mut program_state = ProgramState::try_from_slice(&program_state_account.data.borrow())
                .unwrap_or_default();

            // --- Proof-of-Work Verification ---
            let mut hasher = Sha256::new();
            hasher.update(miner_account.key.to_bytes());
            hasher.update(&nonce.to_le_bytes());
            let calculated_hash = hasher.finalize();

            // Compare with submitted hash
            if calculated_hash.as_ref() != hash {
                msg!("Submitted hash does not match calculated hash.");
                return Err(ProgramError::InvalidInstructionData);
            }

            // Check difficulty
            let target_difficulty_bytes = program_state.difficulty as usize;
            let mut meets_difficulty = true;
            for i in 0..target_difficulty_bytes {
                if hash[i] != 0 {
                    meets_difficulty = false;
                    break;
                }
            }

            if !meets_difficulty {
                msg!("Hash does not meet difficulty target.");
                return Err(ProgramError::Custom(1)); // Custom error for not meeting difficulty
            }

            // --- Difficulty Adjustment ---
            let clock = Clock::from_account_info(clock_account)?;
            let current_timestamp = clock.unix_timestamp;

            if program_state.last_block_timestamp != 0 {
                let delta_t = (current_timestamp - program_state.last_block_timestamp) as u64;

                // Update circular buffer for observed block times
                let ptr = program_state.observed_block_time_ptr as usize;
                program_state.observed_block_times[ptr] = delta_t;
                program_state.observed_block_time_ptr = ((ptr as u8 + 1) % (program_state.observed_block_times.len() as u8));

                // Calculate T_obs
                let total_observed_time: u64 = program_state.observed_block_times.iter().sum();
                let t_obs = total_observed_time / program_state.observed_block_times.len() as u64;

                // Apply difficulty adjustment: D_{t+1} = D_t * (T* / T_obs)^alpha_d
                // Using fixed-point arithmetic
                let target_block_time_scaled = program_state.target_block_time * SCALING_FACTOR;
                let t_obs_scaled = t_obs * SCALING_FACTOR;

                if t_obs_scaled == 0 {
                    // Avoid division by zero
                    msg!("T_obs is zero, skipping difficulty adjustment.");
                } else {
                    // (T* / T_obs)
                    let ratio = target_block_time_scaled / t_obs_scaled;

                    // (T* / T_obs)^alpha_d
                    // This requires a power function for fixed-point numbers, which is complex.
                    // For simplicity, we'll use a linear adjustment for now.
                    // D_{t+1} = D_t * (1 + (T* - T_obs) / T_obs * alpha_d)
                    let diff = if program_state.target_block_time > t_obs {
                        program_state.target_block_time - t_obs
                    } else {
                        t_obs - program_state.target_block_time
                    };

                    let adjustment = (diff * program_state.alpha_d) / (t_obs * SCALING_FACTOR);

                    if program_state.target_block_time > t_obs {
                        program_state.difficulty = program_state.difficulty + adjustment;
                    } else {
                        program_state.difficulty = program_state.difficulty.saturating_sub(adjustment);
                    }
                }
            }

            // Update last block timestamp
            program_state.last_block_timestamp = current_timestamp;

            // If verification passes, update the mined count
            program_state.mined_count += 1;
            msg!("Mined count updated to: {}", program_state.mined_count);
            msg!("New difficulty: {}", program_state.difficulty);

            // Serialize and save the updated state
            program_state.serialize(&mut &mut program_state_account.data.borrow_mut()[..])?;
        }
    }

    Ok(())
}
