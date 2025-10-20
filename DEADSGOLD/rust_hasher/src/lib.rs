
use drillx::{equix, Hash, Solution};
use pyo3::prelude::*;
use std::sync::{Arc, RwLock};
use std::time::Instant;

#[pyfunction]
fn find_hash(challenge: [u8; 32], difficulty: u32) -> PyResult<(Vec<u8>, u64)> {
    let cores = num_cpus::get() as u64;
    let nonce_indices: Vec<u64> = (0..cores).map(|i| u64::MAX / cores * i).collect();

    let solution = find_hash_par(
        challenge,
        u64::MAX, // No cutoff time
        cores,
        difficulty,
        &nonce_indices,
        None,
    );

    Ok((solution.d.to_vec(), u64::from_le_bytes(solution.n)))
}

pub fn find_solution_rust(
    challenge: [u8; 32],
    cores: u64,
    min_difficulty: u32,
) -> Solution {
    let nonce_indices: Vec<u64> = (0..cores).map(|i| u64::MAX / cores * i).collect();
    find_hash_par(
        challenge,
        u64::MAX, // No cutoff time
        cores,
        min_difficulty,
        &nonce_indices,
        None,
    )
}

fn find_hash_par(
    challenge: [u8; 32],
    cutoff_time: u64,
    cores: u64,
    min_difficulty: u32,
    nonce_indices: &[u64],
    pool_channel: Option<tokio::sync::mpsc::UnboundedSender<Solution>>,
) -> Solution {
    let global_best_difficulty = Arc::new(RwLock::new(0u32));

    let core_ids = core_affinity::get_core_ids().expect("Failed to fetch core count");
    let core_ids = core_ids.into_iter().filter(|id| id.id < (cores as usize));
    let handles: Vec<_> = core_ids
        .map(|i| {
            let global_best_difficulty = Arc::clone(&global_best_difficulty);
            std::thread::spawn({
                let nonce = nonce_indices[i.id];
                let mut memory = equix::SolverMemory::new();
                let pool_channel = pool_channel.clone();
                move || {
                    core_affinity::set_for_current(i);

                    let timer = Instant::now();
                    let mut nonce = nonce;
                    let mut best_nonce = nonce;
                    let mut best_difficulty = 0;
                    let mut best_hash = Hash::default();
                    loop {
                        let hxs = drillx::hashes_with_memory(
                            &mut memory,
                            &challenge,
                            &nonce.to_le_bytes(),
                        );

                        for hx in hxs {
                            let difficulty = hx.difficulty();
                            if difficulty.gt(&best_difficulty) {
                                best_nonce = nonce;
                                best_difficulty = difficulty;
                                best_hash = hx;
                                if best_difficulty.gt(&*global_best_difficulty.read().unwrap()) {
                                    *global_best_difficulty.write().unwrap() = best_difficulty;

                                    if difficulty.ge(&min_difficulty) {
                                        if let Some(ref ch) = pool_channel {
                                            let digest = best_hash.d;
                                            let nonce = nonce.to_le_bytes();
                                            let solution = Solution {
                                                d: digest,
                                                n: nonce,
                                            };
                                            if let Err(err) = ch.send(solution) {
                                                println!("ERROR: {:?}", err);
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        if nonce % 100 == 0 {
                            let global_best_difficulty = *global_best_difficulty.read().unwrap();
                            if timer.elapsed().as_secs().ge(&cutoff_time) {
                                if global_best_difficulty.ge(&min_difficulty) {
                                    break;
                                }
                            }
                        }

                        nonce += 1;
                    }

                    (best_nonce, best_difficulty, best_hash)
                }
            })
        })
        .collect();

    let mut best_nonce: u64 = 0;
    let mut best_difficulty = 0;
    let mut best_hash = Hash::default();
    for h in handles {
        if let Ok((nonce, difficulty, hash)) = h.join() {
            if difficulty > best_difficulty {
                best_difficulty = difficulty;
                best_nonce = nonce;
                best_hash = hash;
            }
        }
    }

    Solution::new(best_hash.d, best_nonce.to_le_bytes())
}

#[pymodule]
fn rust_hasher(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(find_hash, m)?)?;
    Ok(())
}
