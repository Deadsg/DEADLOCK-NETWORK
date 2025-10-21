pub mod error;
pub mod instruction;
pub mod state;
pub mod processor;

use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    pubkey::Pubkey,
};

// Declare and export the program's entrypoint
entrypoint!(process_instruction);

// Program entrypoint's implementation
pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    msg!("DEADSGOLD Miner Program entrypoint");
    processor::process_instruction(program_id, accounts, instruction_data)
}

// Define the program ID for easier access
solana_program::declare_id!("DEADSGOLDMinerProgram111111111111111111111111111");