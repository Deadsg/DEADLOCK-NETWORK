use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint::ProgramResult,
    msg,
    program::invoke_signed,
    program_error::ProgramError,
    pubkey::Pubkey,
    system_program,
    sysvar::{rent::Rent, Sysvar},
};
use spl_token::instruction as token_instruction;
use sha3::{Digest, Keccak256};

use crate::{
    error::DeadsgoldMinerError,
    instruction::DeadsgoldMinerInstruction,
    state::{Config, MinerProof, CONFIG_SEED, MINER_PROOF_SEED, BUS_SEED, get_config_pda, get_miner_proof_pda, get_bus_pda},
};
use borsh::{BorshDeserialize, BorshSerialize};

pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let instruction = DeadsgoldMinerInstruction::unpack(instruction_data)?;

    match instruction {
        DeadsgoldMinerInstruction::Initialize { challenge, difficulty, reward_amount, token_mint } => {
            msg!("Instruction: Initialize");
            initialize(program_id, accounts, challenge, difficulty, reward_amount, token_mint)
        }
        DeadsgoldMinerInstruction::Open => {
            msg!("Instruction: Open");
            open(program_id, accounts)
        }
        DeadsgoldMinerInstruction::Mine { nonce } => {
            msg!("Instruction: Mine");
            mine(program_id, accounts, nonce)
        }
        DeadsgoldMinerInstruction::Reset { challenge, difficulty } => {
            msg!("Instruction: Reset");
            reset(program_id, accounts, challenge, difficulty)
        }
        DeadsgoldMinerInstruction::Claim => {
            msg!("Instruction: Claim");
            claim(program_id, accounts)
        }
    }
}

fn initialize(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    challenge: [u8; 32],
    difficulty: u64,
    reward_amount: u64,
    token_mint: [u8; 32],
) -> ProgramResult {
    let accounts_iter = &mut accounts.iter();

    let config_account = next_account_info(accounts_iter)?;
    let admin_account = next_account_info(accounts_iter)?;
    let system_program_account = next_account_info(accounts_iter)?;

    if config_account.owner != program_id && config_account.owner != &system_program::id() {
        return Err(ProgramError::IllegalOwner);
    }
    if !admin_account.is_signer {
        return Err(ProgramError::MissingRequiredSignature);
    }

    let (config_pda, config_bump) = get_config_pda(program_id);
    if config_pda != *config_account.key {
        return Err(DeadsgoldMinerError::InvalidInstruction.into());
    }

    let rent = &Rent::from_account_info(next_account_info(accounts_iter)?)?;

    // Create config account if it doesn't exist
    if config_account.data_len() == 0 {
        let space = Config::LEN;
        let lamports = rent.minimum_balance(space);

        invoke_signed(
            &solana_program::system_instruction::create_account(
                admin_account.key,
                config_account.key,
                lamports,
                space as u64,
                program_id,
            ),
            &[
                admin_account.clone(),
                config_account.clone(),
                system_program_account.clone(),
            ],
            &[&[CONFIG_SEED, &[config_bump]]],
        )?;
    }

    let mut config_data = Config::try_from_slice(&config_account.data.borrow())?;
    if config_data.admin != Pubkey::default() {
        return Err(DeadsgoldMinerError::AccountNotInitialized.into());
    }

    config_data.admin = *admin_account.key;
    config_data.challenge = challenge;
    config_data.difficulty = difficulty;
    config_data.reward_amount = reward_amount;
    config_data.token_mint = Pubkey::new_from_array(token_mint);
    config_data.last_reset_at = solana_program::clock::Clock::get()?.unix_timestamp;
    config_data.serialize(&mut &mut config_account.data.borrow_mut()[..])?;

    Ok(())
}

fn open(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let accounts_iter = &mut accounts.iter();

    let miner_proof_account = next_account_info(accounts_iter)?;
    let miner_authority = next_account_info(accounts_iter)?;
    let system_program_account = next_account_info(accounts_iter)?;

    if miner_proof_account.owner != program_id && miner_proof_account.owner != &system_program::id() {
        return Err(ProgramError::IllegalOwner);
    }
    if !miner_authority.is_signer {
        return Err(ProgramError::MissingRequiredSignature);
    }

    let (miner_proof_pda, miner_proof_bump) = get_miner_proof_pda(miner_authority.key, program_id);
    if miner_proof_pda != *miner_proof_account.key {
        return Err(DeadsgoldMinerError::InvalidInstruction.into());
    }

    let rent = &Rent::from_account_info(next_account_info(accounts_iter)?)?;

    // Create miner proof account if it doesn't exist
    if miner_proof_account.data_len() == 0 {
        let space = MinerProof::LEN;
        let lamports = rent.minimum_balance(space);

        invoke_signed(
            &solana_program::system_instruction::create_account(
                miner_authority.key,
                miner_proof_account.key,
                lamports,
                space as u64,
                program_id,
            ),
            &[
                miner_authority.clone(),
                miner_proof_account.clone(),
                system_program_account.clone(),
            ],
            &[&[MINER_PROOF_SEED, miner_authority.key.as_ref(), &[miner_proof_bump]]],
        )?;
    }

    let mut miner_proof_data = MinerProof::try_from_slice(&miner_proof_account.data.borrow())?;
    if miner_proof_data.authority != Pubkey::default() {
        return Err(DeadsgoldMinerError::AccountNotInitialized.into());
    }

    miner_proof_data.authority = *miner_authority.key;
    miner_proof_data.serialize(&mut &mut miner_proof_account.data.borrow_mut()[..])?;

    Ok(())
}

fn mine(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    nonce: u64,
) -> ProgramResult {
    let accounts_iter = &mut accounts.iter();

    let miner_proof_account = next_account_info(accounts_iter)?;
    let miner_authority = next_account_info(accounts_iter)?;
    let config_account = next_account_info(accounts_iter)?;
    let bus_account = next_account_info(accounts_iter)?;
    let miner_token_account = next_account_info(accounts_iter)?;
    let token_program = next_account_info(accounts_iter)?;
    let token_mint_account = next_account_info(accounts_iter)?;

    if !miner_authority.is_signer {
        return Err(ProgramError::MissingRequiredSignature);
    }

    let (miner_proof_pda, _) = get_miner_proof_pda(miner_authority.key, program_id);
    if miner_proof_pda != *miner_proof_account.key {
        return Err(DeadsgoldMinerError::InvalidInstruction.into());
    }

    let config_data = Config::try_from_slice(&config_account.data.borrow())?;
    let mut miner_proof_data = MinerProof::try_from_slice(&miner_proof_account.data.borrow())?;

    if config_data.token_mint != *token_mint_account.key {
        return Err(DeadsgoldMinerError::InvalidTokenMint.into());
    }

    let mut hasher = Keccak256::new();
    hasher.update(&config_data.challenge);
    hasher.update(&nonce.to_le_bytes());
    let computed_hash = hasher.finalize();

    let mut leading_zeros = 0;
    for byte in computed_hash.as_slice().iter() {
        if *byte == 0 {
            leading_zeros += 8;
        } else {
            leading_zeros += byte.leading_zeros();
            break;
        }
    }

    if u64::from(leading_zeros) < config_data.difficulty {
        return Err(DeadsgoldMinerError::ChallengeNotMet.into());
    }

    // Transfer rewards
    let (bus_pda, bus_bump) = get_bus_pda(0, program_id); // Assuming bus 0 for now
    let authority_seeds = &[BUS_SEED, &0u64.to_le_bytes(), &[bus_bump]];
    let signer_seeds = &[&authority_seeds[..]];

    let transfer_instruction = token_instruction::transfer(
        token_program.key,
        bus_account.key,
        miner_token_account.key,
        &bus_pda,
        &[],
        config_data.reward_amount,
    )?;

    invoke_signed(
        &transfer_instruction,
        &[
            bus_account.clone(),
            miner_token_account.clone(),
            bus_account.clone(), // Source owner
            token_program.clone(),
        ],
        signer_seeds,
    )?;

    miner_proof_data.last_hash_at = solana_program::clock::Clock::get()?.unix_timestamp;
    miner_proof_data.rewards_pending = miner_proof_data.rewards_pending.saturating_add(config_data.reward_amount);
    miner_proof_data.serialize(&mut &mut miner_proof_account.data.borrow_mut()[..])?;

    Ok(())
}

fn reset(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    challenge: [u8; 32],
    difficulty: u64,
) -> ProgramResult {
    let accounts_iter = &mut accounts.iter();

    let config_account = next_account_info(accounts_iter)?;
    let admin_account = next_account_info(accounts_iter)?;

    if !admin_account.is_signer {
        return Err(ProgramError::MissingRequiredSignature);
    }

    let (config_pda, _) = get_config_pda(program_id);
    if config_pda != *config_account.key {
        return Err(DeadsgoldMinerError::InvalidInstruction.into());
    }

    let mut config_data = Config::try_from_slice(&config_account.data.borrow())?;
    if config_data.admin != *admin_account.key {
        return Err(ProgramError::MissingRequiredSignature);
    }

    config_data.challenge = challenge;
    config_data.difficulty = difficulty;
    config_data.last_reset_at = solana_program::clock::Clock::get()?.unix_timestamp;
    config_data.serialize(&mut &mut config_account.data.borrow_mut()[..])?;

    Ok(())
}

fn claim(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let accounts_iter = &mut accounts.iter();

    let miner_proof_account = next_account_info(accounts_iter)?;
    let miner_authority = next_account_info(accounts_iter)?;
    let miner_token_account = next_account_info(accounts_iter)?;
    let bus_account = next_account_info(accounts_iter)?;
    let token_program = next_account_info(accounts_iter)?;
    let _token_mint_account = next_account_info(accounts_iter)?;

    if !miner_authority.is_signer {
        return Err(ProgramError::MissingRequiredSignature);
    }

    let (miner_proof_pda, _) = get_miner_proof_pda(miner_authority.key, program_id);
    if miner_proof_pda != *miner_proof_account.key {
        return Err(DeadsgoldMinerError::InvalidInstruction.into());
    }

    let mut miner_proof_data = MinerProof::try_from_slice(&miner_proof_account.data.borrow())?;

    if miner_proof_data.rewards_pending == 0 {
        msg!("No rewards to claim");
        return Ok(());
    }

    let (bus_pda, bus_bump) = get_bus_pda(0, program_id); // Assuming bus 0 for now
    let authority_seeds = &[BUS_SEED, &0u64.to_le_bytes(), &[bus_bump]];
    let signer_seeds = &[&authority_seeds[..]];

    let transfer_instruction = token_instruction::transfer(
        token_program.key,
        bus_account.key,
        miner_token_account.key,
        &bus_pda,
        &[],
        miner_proof_data.rewards_pending,
    )?;

    invoke_signed(
        &transfer_instruction,
        &[
            bus_account.clone(),
            miner_token_account.clone(),
            bus_account.clone(), // Source owner
            token_program.clone(),
        ],
        signer_seeds,
    )?;

    miner_proof_data.rewards_pending = 0;
    miner_proof_data.serialize(&mut &mut miner_proof_account.data.borrow_mut()[..])?;

    Ok(())
}