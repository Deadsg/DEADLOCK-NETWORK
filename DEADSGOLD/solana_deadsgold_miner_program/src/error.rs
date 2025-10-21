use thiserror::Error;
use solana_program::program_error::ProgramError;

#[derive(Error, Debug, Copy, Clone)]
pub enum DeadsgoldMinerError {
    #[error("Invalid instruction")]
    InvalidInstruction,
    #[error("Invalid proof")]
    InvalidProof,
    #[error("Challenge not met")]
    ChallengeNotMet,
    #[error("Account not initialized")]
    AccountNotInitialized,
    #[error("Incorrect program ID")]
    IncorrectProgramId,
    #[error("Invalid token mint")]
    InvalidTokenMint,
    #[error("Reward distribution failed")]
    RewardDistributionFailed,
}

impl From<DeadsgoldMinerError> for ProgramError {
    fn from(e: DeadsgoldMinerError) -> Self {
        ProgramError::Custom(e as u32)
    }
}
