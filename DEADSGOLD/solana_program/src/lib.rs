
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program_error::ProgramError,
    pubkey::Pubkey,
    system_program,
};
use spl_token::state::Mint;
use rust_hasher::{find_solution_rust, Solution};

mod instruction;

// Declare and export the program's entrypoint
entrypoint!(process_instruction);

// Program entrypoint
pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    msg!("Deadsgold Solana Program Entrypoint");

    let instruction = instruction::DeadsgoldInstruction::unpack(instruction_data)?;

    match instruction {
        instruction::DeadsgoldInstruction::InitializeMint { decimals } => {
            msg!("Instruction: InitializeMint");
            initialize_mint(program_id, accounts, decimals)?;
        }
        instruction::DeadsgoldInstruction::Mine { challenge, nonce, difficulty } => {
            msg!("Instruction: Mine");
            mine(program_id, accounts, challenge, nonce, difficulty)?;
        }
    }

    Ok(())
}

fn initialize_mint(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    decimals: u8,
) -> ProgramResult {
    let accounts_iter = &mut accounts.iter();

    let mint_account = next_account_info(accounts_iter)?;
    let mint_authority = next_account_info(accounts_iter)?;
    let rent_sysvar = next_account_info(accounts_iter)?;
    let token_program = next_account_info(accounts_iter)?;

    // Check if the mint account is owned by the token program
    if *token_program.key != spl_token::id() {
        return Err(ProgramError::IncorrectProgramId);
    }

    // Initialize the mint
    spl_token::instruction::initialize_mint(
        token_program.key,
        mint_account.key,
        mint_authority.key,
        Option::None, // Freeze authority
        decimals,
    )?;

    msg!("Mint initialized successfully!");

    Ok(())
}

fn mine(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    challenge: [u8; 32],
    nonce: u64,
    difficulty: u32,
) -> ProgramResult {
    let accounts_iter = &mut accounts.iter();

    let mint_account = next_account_info(accounts_iter)?;
    let miner_token_account = next_account_info(accounts_iter)?;
    let miner_authority = next_account_info(accounts_iter)?;
    let token_program = next_account_info(accounts_iter)?;

    // Verify the solution using rust_hasher
    let solution = find_solution_rust(challenge, 1, difficulty);
    let solution_nonce = u64::from_le_bytes(solution.n);

    if solution_nonce != nonce {
        return Err(ProgramError::InvalidInstructionData);
    }

    // Mint tokens to the miner
    let amount = 1_000_000_000; // 1 token with 9 decimals
    spl_token::instruction::mint_to(
        token_program.key,
        mint_account.key,
        miner_token_account.key,
        miner_authority.key,
        &[],
        amount,
    )?;

    msg!("Mined 1 token successfully!");

    Ok(())
}
