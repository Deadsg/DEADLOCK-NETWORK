use solana_program::{pubkey::Pubkey, program_error::ProgramError};
use borsh::{BorshSerialize, BorshDeserialize};
use bytemuck::{Pod, Zeroable};

#[repr(C)]
#[derive(Clone, Copy, Debug, PartialEq, Pod, Zeroable, BorshSerialize, BorshDeserialize)]
pub struct Config {
    pub admin: Pubkey,
    pub challenge: [u8; 32],
    pub difficulty: u64,
    pub reward_amount: u64,
    pub last_reset_at: i64,
    pub token_mint: Pubkey,
}

impl Config {
    pub const LEN: usize = 32 + 32 + 8 + 8 + 8 + 32; // Pubkey + [u8; 32] + u64 + u64 + i64 + Pubkey

    pub fn new(
        admin: Pubkey,
        challenge: [u8; 32],
        difficulty: u64,
        reward_amount: u64,
        token_mint: Pubkey,
    ) -> Self {
        Self {
            admin,
            challenge,
            difficulty,
            reward_amount,
            last_reset_at: 0,
            token_mint,
        }
    }
}

#[repr(C)]
#[derive(Clone, Copy, Debug, PartialEq, Pod, Zeroable, BorshSerialize, BorshDeserialize)]
pub struct MinerProof {
    pub authority: Pubkey,
    pub last_hash_at: i64,
    pub rewards_pending: u64,
}

impl MinerProof {
    pub const LEN: usize = 32 + 8 + 8; // Pubkey + i64 + u64

    pub fn new(authority: Pubkey) -> Self {
        Self {
            authority,
            last_hash_at: 0,
            rewards_pending: 0,
        }
    }
}

// Program Derived Address (PDA) seeds
pub const CONFIG_SEED: &[u8] = b"config";
pub const MINER_PROOF_SEED: &[u8] = b"miner_proof";
pub const BUS_SEED: &[u8] = b"bus";

// Helper to get PDA for config account
pub fn get_config_pda() -> (Pubkey, u8) {
    Pubkey::find_program_address(&[CONFIG_SEED], &crate::id())
}

// Helper to get PDA for miner proof account
pub fn get_miner_proof_pda(authority: &Pubkey) -> (Pubkey, u8) {
    Pubkey::find_program_address(&[MINER_PROOF_SEED, authority.as_ref()], &crate::id())
}

// Helper to get PDA for bus account
pub fn get_bus_pda(bus_id: u64) -> (Pubkey, u8) {
    Pubkey::find_program_address(&[BUS_SEED, &bus_id.to_le_bytes()], &crate::id())
}
