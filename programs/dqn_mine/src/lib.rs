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

// 1. Define Instruction data
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub enum MineInstruction {
    Initialize { initial_difficulty: u64 },
    VerifyMine { proof: [u8; 32] },
}

// 2. Define State data
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct MineState {
    pub difficulty: u64,
    pub total_effort: u64,
    pub last_block_hash: [u8; 32],
    pub reward_pool: u64,
}

// 3. Define the entrypoint
entrypoint!(process_instruction);

// 4. Instruction processor
pub fn process_instruction(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let instruction = MineInstruction::try_from_slice(instruction_data)?;

    match instruction {
        MineInstruction::Initialize { initial_difficulty } => {
            msg!("Instruction: Initialize");
            initialize(accounts, initial_difficulty)
        }
        MineInstruction::VerifyMine { proof } => {
            msg!("Instruction: VerifyMine");
            verify_mine(accounts, proof)
        }
    }
}

// 5. Instruction logic
pub fn initialize(
    accounts: &[AccountInfo],
    initial_difficulty: u64,
) -> ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let mine_state_account = next_account_info(accounts_iter)?;

    let mut mine_state = MineState::try_from_slice(&mine_state_account.data.borrow())?;
    mine_state.difficulty = initial_difficulty;
    mine_state.total_effort = 0;
    mine_state.last_block_hash = [0; 32];
    mine_state.reward_pool = 1_000_000_000;
    mine_state.serialize(&mut &mut mine_state_account.data.borrow_mut()[..])?;

    Ok(())
}

pub fn verify_mine(
    accounts: &[AccountInfo],
    proof: [u8; 32],
) -> ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let mine_state_account = next_account_info(accounts_iter)?;
    let miner_account = next_account_info(accounts_iter)?;

    if !miner_account.is_signer {
        return Err(ProgramError::MissingRequiredSignature);
    }

    let mut mine_state = MineState::try_from_slice(&mine_state_account.data.borrow())?;

    let mut hasher = Sha256::new();
    hasher.update(miner_account.key.as_ref());
    hasher.update(&mine_state.last_block_hash);
    let result = hasher.finalize();

    if result[..] != proof[..] {
        return Err(ProgramError::InvalidArgument);
    }

    mine_state.total_effort += 1;
    mine_state.last_block_hash = proof;
    mine_state.reward_pool -= 1;
    mine_state.serialize(&mut &mut mine_state_account.data.borrow_mut()[..])?;

    Ok(())
}
