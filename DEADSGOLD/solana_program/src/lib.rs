use solana_program::{
    account_info::{AccountInfo, next_account_info},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    pubkey::Pubkey,
};

// Declare and export the program's entrypoint
entrypoint!(process_instruction);

// Program entrypoint's implementation
pub fn process_instruction(
    program_id: &Pubkey, // Public key of the account the program was loaded into
    accounts: &[AccountInfo], // All accounts required to run the instruction
    instruction_data: &[u8], // Serialized instruction data
) -> ProgramResult {
    msg!("Deadsgold Solana Program Entrypoint");

    // Iterating accounts is safer than indexing
    let accounts_iter = &mut accounts.iter();

    // Get the account to say hello to
    let account = next_account_info(accounts_iter)?;

    // The account must be owned by the program in order to modify its data
    if account.owner != program_id {
        msg!("Account does not have the correct program_id");
        return Err(solana_program::program_error::ProgramError::IncorrectProgramId);
    }

    // Log the instruction data
    msg!("Instruction Data: {:?}", instruction_data);

    Ok(())
}