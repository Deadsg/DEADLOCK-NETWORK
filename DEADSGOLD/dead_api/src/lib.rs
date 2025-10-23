use solana_program::declare_id;

declare_id!("G97jm3Unn37GPVvdFKvngzCoRUsxjrQ2X1xuj7BMYZHe");

pub mod consts {
    use solana_program::pubkey::Pubkey;

    pub const MINT_ADDRESS: Pubkey = solana_program::pubkey!("BtyvvfnFiC599j5gcswiE13JDUGpySKZJ81BSd3cmzQG");

    pub const CONFIG_ADDRESS: Pubkey =
        solana_program::pubkey!("74QdHwq2TXwytApm8ci28yraYw33yzsQuKcLy5HWRncX");

    pub const BUS_COUNT: usize = 8;
    pub const BUS_ADDRESSES: [Pubkey; BUS_COUNT] = [
        solana_program::pubkey!("FPMNb1RjRnKxJCG7rBixKE3MFqm4PATU4HFfPyHDXHa4"),
        solana_program::pubkey!("Hg4WCisj85rm2qhLyvbyn7EJf4trnemSAS1H6j3mF42b"),
        solana_program::pubkey!("Bvk2A6nQdXvZL4jcYEJ9B4TWdgw4eJ65Wj6xysbbUA5G"),
        solana_program::pubkey!("BmAWhqx7Twcp5qTV7rYRgWbJMqQTrnfwwvfjyE25wRps"),
        solana_program::pubkey!("ERgsJdWW5iYW35mPhD6ponDYVoc8f6i9W5bwJzrtanPw"),
        solana_program::pubkey!("GhBgzvBvALg5yw81iLfmYEHovYETMEA2pNWdMbmtkjdZ"),
        solana_program::pubkey!("31eauRq8G3hvZCSTJ3cDLrp3cu87tF7Tb4XRteH4GJjp"),
        solana_program::pubkey!("DtA5rATgXeK4diuczphzXWcDxdeJYS6W9ijyucTBvk65"),
    ];

    pub const PROOF: &[u8] = b"proof";
    pub const TREASURY: &[u8] = b"treasury";
    pub const CONFIG: &[u8] = b"config";
    pub const BUS: &[u8] = b"bus";

    pub const COAL_EPOCH_DURATION: i64 = 60 * 60 * 24;
    pub const WOOD_EPOCH_DURATION: i64 = 60 * 60 * 24;
}

pub mod instruction {
    use solana_program::instruction::{AccountMeta, Instruction};
    use solana_program::pubkey::Pubkey;
    use solana_program::system_program;
    use spl_token::ID as SPL_TOKEN_ID;

    use crate::{consts::*, ID};

        pub enum DeadInstruction {
            Mine { hash: [u8; 32], nonce: [u8; 8] },
            Auth,
        }
    
        impl DeadInstruction {
            pub fn to_instruction(&self, signer: Pubkey, beneficiary: Pubkey, bus: Pubkey) -> Instruction {
                let accounts = vec![
                    AccountMeta::new_readonly(signer, true),
                    AccountMeta::new_readonly(beneficiary, false),
                    AccountMeta::new(bus, false),
                    AccountMeta::new_readonly(MINT_ADDRESS, false),
                    AccountMeta::new_readonly(SPL_TOKEN_ID, false),
                    AccountMeta::new_readonly(system_program::ID, false),
                ];
    
                let data = match self {
                    DeadInstruction::Mine { hash, nonce } => {
                        let mut data = vec![];
                        data.push(0); // Discriminant for Mine instruction
                        data.extend_from_slice(hash);
                        data.extend_from_slice(nonce);
                        data
                    },
                    DeadInstruction::Auth => {
                        let mut data = vec![];
                        data.push(1); // Discriminant for Auth instruction
                        data
                    }
                };
    
                Instruction {
                    program_id: ID,
                    accounts,
                    data,
                }
            }
        }
    
        pub fn mine(signer: Pubkey, beneficiary: Pubkey, bus: Pubkey, hash: [u8; 32], nonce: [u8; 8]) -> Instruction {
            DeadInstruction::Mine { hash, nonce }.to_instruction(signer, beneficiary, bus)
        }
    
        pub fn auth(signer: Pubkey, beneficiary: Pubkey, bus: Pubkey) -> Instruction {
            DeadInstruction::Auth.to_instruction(signer, beneficiary, bus)
        }}

pub mod state;

