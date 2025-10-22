use std::{sync::Arc, thread::sleep, time::Duration};

use borsh::BorshSerialize;
use colored::Colorize;
use drillx::{
    equix,
    Hash,
    Solution,
};
use solana_program::pubkey::Pubkey;
use solana_sdk::{
    compute_budget::ComputeBudgetInstruction,
    instruction::{AccountMeta, Instruction},
    signature::Signer,
    transaction::Transaction,
};
use crate::{
    args::DeadsgoldMineArgs,
    Miner,
};

// Import the instruction enum from our deployed program
use deadsgold_solana_program::DeadsgoldInstruction;

const DEADSGOLD_PROGRAM_ID: &str = "4inSouwXMDGvErbtrpgnBesCKi8yK2BKBT2L3v82wka";

impl Miner {
    pub async fn deadsgold_mine(&self, args: DeadsgoldMineArgs) {
        // Get verbose flag
        let verbose = args.verbose;

        // Generate addresses
        let signer = self.signer();
        let program_id = Pubkey::new_from_array(DEADSGOLD_PROGRAM_ID.parse::<Pubkey>().unwrap().to_bytes());

        // Derive PDA for program state account
        let (program_state_pda, _bump_seed) = Pubkey::find_program_address(
            &[b"program_state"],
            &program_id,
        );

        // Start mining loop
        loop {
            // --- Off-chain Hash Finding (Simplified) ---
            // In a real scenario, this would involve more complex PoW.
            let mut nonce: u64 = 0;
            let mut best_hash = Hash::default();
            let mut best_difficulty = 0;

            // Simulate finding a hash
            // This is a placeholder for actual mining logic
            for i in 0..1_000_000 {
                let mut hasher = sha2::Sha256::new();
                hasher.update(signer.pubkey().to_bytes());
                hasher.update(&i.to_le_bytes());
                let current_hash = hasher.finalize();

                // Simple difficulty check (e.g., first byte is zero)
                if current_hash[0] == 0 {
                    best_hash = Hash::new(current_hash.into());
                    best_difficulty = 1; // Placeholder
                    nonce = i;
                    break;
                }
                nonce = i;
            }

            if best_difficulty == 0 {
                println!("No hash found meeting minimum difficulty in this iteration. Retrying...");
                sleep(Duration::from_secs(1));
                continue;
            }

            println!("Found hash with nonce: {}, difficulty: {}", nonce, best_difficulty);

            // --- Construct and Send Mine Instruction ---
            let instruction_data = DeadsgoldInstruction::Mine {
                nonce,
                hash: best_hash.d,
            }.try_to_vec().unwrap();

            let instruction = Instruction {
                program_id,
                accounts: vec![
                    AccountMeta::new(signer.pubkey(), true), // Miner account (signer)
                    AccountMeta::new(program_state_pda, false), // Program state account (writable)
                ],
                data: instruction_data,
            };

            let mut transaction = Transaction::new_with_payer(
                &[instruction],
                Some(&signer.pubkey()),
            );

            // Set compute unit limit and price
            let cu_limit_ix = ComputeBudgetInstruction::set_compute_unit_limit(200_000);
            let cu_price_ix = ComputeBudgetInstruction::set_compute_unit_price(self.priority_fee.unwrap_or(100_000));
            transaction.instructions.insert(0, cu_limit_ix);
            transaction.instructions.insert(1, cu_price_ix);

            let (recent_blockhash, last_valid_block_height) = self.rpc_client
                .get_latest_blockhash_with_commitment(solana_sdk::commitment_config::CommitmentConfig::confirmed())
                .await
                .unwrap();
            transaction.sign(&[&signer], recent_blockhash);

            match self.rpc_client.send_and_confirm_transaction_with_spinner_and_commitment(
                &transaction,
                solana_sdk::commitment_config::CommitmentConfig::confirmed(),
            ).await {
                Ok(signature) => {
                    println!("Transaction successful: {}", signature);
                    // Optionally fetch and display updated program state
                    // self.fetch_program_state(program_state_pda).await;
                },
                Err(e) => {
                    println!("Transaction failed: {:?}", e);
                }
            }

            sleep(Duration::from_secs(args.buffer_time));
        }
    }

    // async fn fetch_program_state(&self, pda: Pubkey) {
    //     match self.rpc_client.get_account(&pda).await {
    //         Ok(account) => {
    //             let program_state = deadsgold_solana_program::ProgramState::try_from_slice(&account.data).unwrap();
    //             println!("Current Mined Count: {}", program_state.mined_count);
    //         },
    //         Err(e) => {
    //             println!("Failed to fetch program state: {:?}", e);
    //         }
    //     }
    // }
}
