use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program_error::ProgramError,
    pubkey::Pubkey,
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
}

// Define the program's state
#[derive(BorshSerialize, BorshDeserialize, Debug, Default)]
pub struct ProgramState {
    pub mined_count: u64,
    pub difficulty: u64, // Example difficulty target
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
        DeadsgoldInstruction::Mine { nonce, hash } => {
            msg!("Instruction: Mine");
            msg!("Nonce: {}", nonce);
            msg!("Hash: {:?}", hash);

            let accounts_iter = &mut accounts.iter();
            let miner_account = next_account_info(accounts_iter)?;
            let program_state_account = next_account_info(accounts_iter)?;

            // Ensure the miner is a signer
            if !miner_account.is_signer {
                return Err(ProgramError::MissingRequiredSignature);
            }

            // Ensure the program state account is writable and owned by the program
            if !program_state_account.is_writable || program_state_account.owner != program_id {
                return Err(ProgramError::IncorrectProgramId);
            }

            // Deserialize program state
            let mut program_state = ProgramState::try_from_slice(&program_state_account.data.borrow())
                .unwrap_or_default();

            // --- Simple Proof-of-Work Verification ---
            // For demonstration, let's assume a simple hash check against a difficulty.
            // In a real mining scenario, this would be more complex.
            let mut hasher = Sha256::new();
            hasher.update(miner_account.key.to_bytes());
            hasher.update(&nonce.to_le_bytes());
            let calculated_hash = hasher.finalize();

            // Compare with submitted hash
            if calculated_hash.as_ref() != hash {
                msg!("Submitted hash does not match calculated hash.");
                return Err(ProgramError::InvalidInstructionData);
            }

            // Check difficulty (example: first few bytes of hash must be zero)
            // This is a very basic example. Real PoW is more involved.
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

            // If verification passes, update the mined count
            program_state.mined_count += 1;
            msg!("Mined count updated to: {}", program_state.mined_count);

            // Serialize and save the updated state
            program_state.serialize(&mut &mut program_state_account.data.borrow_mut()[..])?;
        }
    }

    Ok(())
}
