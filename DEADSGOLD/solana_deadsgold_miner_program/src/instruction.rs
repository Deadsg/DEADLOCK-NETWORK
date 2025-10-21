use solana_program::program_error::ProgramError;
use std::convert::TryInto;

pub enum DeadsgoldMinerInstruction {
    /// Initializes the mining program with a new challenge and difficulty.
    ///
    /// Accounts expected:
    /// 0. `[writable]` Config account
    /// 1. `[signer]` Admin account
    Initialize {
        challenge: [u8; 32],
        difficulty: u64,
        reward_amount: u64,
        token_mint: [u8; 32],
    },

    /// Opens a miner proof account for a new miner.
    ///
    /// Accounts expected:
    /// 0. `[writable]` Miner proof account (PDA)
    /// 1. `[signer]` Miner authority
    /// 2. `[]` System program
    Open,

    /// Submits a mining solution.
    ///
    /// Accounts expected:
    /// 0. `[writable]` Miner proof account (PDA)
    /// 1. `[signer]` Miner authority
    /// 2. `[writable]` Config account
    /// 3. `[writable]` Bus account (for rewards)
    /// 4. `[writable]` Miner token account
    /// 5. `[]` Token program
    /// 6. `[]` Token mint account
    Mine {
        nonce: u64,
        hash: [u8; 32],
    },

    /// Resets the mining challenge and difficulty.
    ///
    /// Accounts expected:
    /// 0. `[writable]` Config account
    /// 1. `[signer]` Admin account
    Reset {
        challenge: [u8; 32],
        difficulty: u64,
    },

    /// Claims accumulated rewards.
    ///
    /// Accounts expected:
    /// 0. `[writable]` Miner proof account (PDA)
    /// 1. `[signer]` Miner authority
    /// 2. `[writable]` Miner token account
    /// 3. `[writable]` Bus account (for rewards)
    /// 4. `[]` Token program
    /// 5. `[]` Token mint account
    Claim,
}

impl DeadsgoldMinerInstruction {
    pub fn unpack(input: &[u8]) -> Result<Self, ProgramError> {
        let (tag, rest) = input.split_first().ok_or(ProgramError::InvalidInstructionData)?;
        Ok(match tag {
            0 => {
                let challenge: [u8; 32] = rest[0..32].try_into().unwrap();
                let difficulty = u64::from_le_bytes(rest[32..40].try_into().unwrap());
                let reward_amount = u64::from_le_bytes(rest[40..48].try_into().unwrap());
                let token_mint: [u8; 32] = rest[48..80].try_into().unwrap();
                Self::Initialize { challenge, difficulty, reward_amount, token_mint }
            }
            1 => Self::Open,
            2 => {
                let nonce = u64::from_le_bytes(rest[0..8].try_into().unwrap());
                let hash: [u8; 32] = rest[8..40].try_into().unwrap();
                Self::Mine { nonce, hash }
            }
            3 => {
                let challenge: [u8; 32] = rest[0..32].try_into().unwrap();
                let difficulty = u64::from_le_bytes(rest[32..40].try_into().unwrap());
                Self::Reset { challenge, difficulty }
            }
            4 => Self::Claim,
            _ => return Err(ProgramError::InvalidInstructionData),
        })
    }

    pub fn pack(&self) -> Vec<u8> {
        let mut buf = Vec::with_capacity(std::mem::size_of::<Self>());
        match self {
            Self::Initialize { challenge, difficulty, reward_amount, token_mint } => {
                buf.push(0);
                buf.extend_from_slice(challenge);
                buf.extend_from_slice(&difficulty.to_le_bytes());
                buf.extend_from_slice(&reward_amount.to_le_bytes());
                buf.extend_from_slice(token_mint);
            }
            Self::Open => buf.push(1),
            Self::Mine { nonce, hash } => {
                buf.push(2);
                buf.extend_from_slice(&nonce.to_le_bytes());
                buf.extend_from_slice(hash);
            }
            Self::Reset { challenge, difficulty } => {
                buf.push(3);
                buf.extend_from_slice(challenge);
                buf.extend_from_slice(&difficulty.to_le_bytes());
            }
            Self::Claim => buf.push(4),
        }
        buf
    }
}
