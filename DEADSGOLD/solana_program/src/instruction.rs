
use solana_program::program_error::ProgramError;
use std::convert::TryInto;

pub enum DeadsgoldInstruction {
    /// Initializes the token mint.
    ///
    /// Accounts expected:
    ///
    /// 0. `[writable]` The mint account
    /// 1. `[signer]` The mint authority
    /// 2. `[]` The rent sysvar
    /// 3. `[]` The token program
    InitializeMint {
        decimals: u8,
    },

    /// Mines new tokens.
    ///
    /// Accounts expected:
    ///
    /// 0. `[writable]` The mint account
    /// 1. `[writable]` The miner's token account
    /// 2. `[signer]` The miner's authority
    /// 3. `[]` The token program
    Mine {
        challenge: [u8; 32],
        nonce: u64,
        difficulty: u32,
    },
}

impl DeadsgoldInstruction {
    /// Deserializes a byte buffer into a `DeadsgoldInstruction`.
    pub fn unpack(input: &[u8]) -> Result<Self, ProgramError> {
        let (&tag, rest) = input.split_first().ok_or(ProgramError::InvalidInstructionData)?;
        match tag {
            0 => {
                let decimals = rest[0];
                Ok(DeadsgoldInstruction::InitializeMint { decimals })
            }
            1 => {
                let challenge: [u8; 32] = rest[..32].try_into().map_err(|_| ProgramError::InvalidInstructionData)?;
                let nonce = u64::from_le_bytes(rest[32..40].try_into().map_err(|_| ProgramError::InvalidInstructionData)?);
                let difficulty = u32::from_le_bytes(rest[40..44].try_into().map_err(|_| ProgramError::InvalidInstructionData)?);
                Ok(DeadsgoldInstruction::Mine { challenge, nonce, difficulty })
            }
            _ => Err(ProgramError::InvalidInstructionData),
        }
    }

    /// Serializes a `DeadsgoldInstruction` into a byte buffer.
    pub fn pack(&self) -> Vec<u8> {
        let mut buf = Vec::with_capacity(std::mem::size_of::<Self>());
        match self {
            Self::InitializeMint { decimals } => {
                buf.push(0);
                buf.push(*decimals);
            }
            Self::Mine { challenge, nonce, difficulty } => {
                buf.push(1);
                buf.extend_from_slice(challenge);
                buf.extend_from_slice(&nonce.to_le_bytes());
                buf.extend_from_slice(&difficulty.to_le_bytes());
            }
        }
        buf
    }
}
