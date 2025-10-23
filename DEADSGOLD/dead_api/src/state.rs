use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::pubkey::Pubkey;

#[derive(BorshSerialize, BorshDeserialize, Clone, Debug, PartialEq)]
pub struct Bus {
    pub id: u64,
    pub rewards: u64,
    pub claimed: u64,
    pub top_miners: [Pubkey; 8],
    pub top_rewards: [u64; 8],
}

#[derive(BorshSerialize, BorshDeserialize, Clone, Debug, PartialEq)]
pub struct Config {
    pub authority: Pubkey,
    pub mint: Pubkey,
    pub last_reset_at: i64,
    pub min_difficulty: u64,
    pub base_reward_rate: u64,
    pub top_balance: u64,
}

#[derive(BorshSerialize, BorshDeserialize, Clone, Debug, PartialEq)]
pub struct Proof {
    pub authority: Pubkey,
    pub miner: Pubkey,
    pub balance: u64,
    pub last_hash: [u8; 32],
    pub last_hash_at: i64,
    pub last_stake_at: i64,
    pub total_hashes: u64,
    pub total_rewards: u64,
    pub challenge: [u8; 32],
}

#[derive(BorshSerialize, BorshDeserialize, Clone, Debug, PartialEq)]
pub struct Tool {
    pub authority: Pubkey,
    pub asset: Pubkey,
    pub durability: u64,
    pub multiplier: u64,
}