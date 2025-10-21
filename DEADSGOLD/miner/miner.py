
import hashlib
import json
import time
import multiprocessing

from DEADSGOLD.blockchain.block import Block
from DEADSGOLD.blockchain.transaction import Transaction


def _proof_of_work_worker(start_nonce, end_nonce, block_index, block_previous_hash, block_timestamp, pending_transactions_data, difficulty):
    """
    Worker function for multiprocessing to find a valid nonce within a given range.
    """
    for nonce in range(start_nonce, end_nonce):
        block_data = {
            "index": block_index,
            "timestamp": block_timestamp,
            "transactions": pending_transactions_data,
            "previous_hash": block_previous_hash,
            "nonce": nonce,
        }
        block_string = json.dumps(block_data, sort_keys=True)
        computed_hash = hashlib.sha256(block_string.encode()).hexdigest()
        if computed_hash[:difficulty] == "0" * difficulty:
            print(f"Worker {multiprocessing.current_process().name} found nonce: {nonce}")
            return nonce
    return None


class Miner:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.use_gpu = False

    def mine(self, last_block, pending_transactions, difficulty):
        print(f"Mining a new block with difficulty {difficulty}...")
        return self.mine_cpu(last_block, pending_transactions, difficulty)

    def mine_cpu(self, last_block, pending_transactions, difficulty):
        num_cores = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(processes=num_cores)

        # Prepare data for workers (serialize objects)
        block_index = last_block.index + 1
        block_previous_hash = last_block.hash
        block_timestamp = time.time()
        pending_transactions_data = [tx.to_dict() for tx in pending_transactions]

        # Divide the nonce search space
        chunk_size = 1000000  # Each process will check 1 million nonces at a time
        manager = multiprocessing.Manager()
        found_nonce = manager.Value('i', -1) # Shared variable to store the found nonce

        results = []
        for i in range(num_cores):
            start_nonce = i * chunk_size
            end_nonce = (i + 1) * chunk_size
            results.append(pool.apply_async(_proof_of_work_worker, (
                start_nonce, end_nonce, block_index, block_previous_hash, block_timestamp, pending_transactions_data, difficulty
            )))

        # Continuously add more tasks if no nonce is found
        nonce_offset = num_cores * chunk_size
        while found_nonce.value == -1:
            for i, res in enumerate(results):
                if res.ready():
                    result = res.get()
                    if result is not None:
                        found_nonce.value = result
                        break
                    # If a process finished without finding a nonce, give it a new range
                    start_nonce = nonce_offset + i * chunk_size
                    end_nonce = nonce_offset + (i + 1) * chunk_size
                    results[i] = pool.apply_async(_proof_of_work_worker, (
                        start_nonce, end_nonce, block_index, block_previous_hash, block_timestamp, pending_transactions_data, difficulty
                    ))
            nonce_offset += num_cores * chunk_size
            if found_nonce.value == -1:
                time.sleep(0.1) # Small delay to prevent busy-waiting

        pool.terminate()
        pool.join()
        print(f"Mining complete. Found nonce: {found_nonce.value}")
        return found_nonce.value, block_timestamp

    def valid_proof_hash(self, last_block, pending_transactions, nonce, difficulty, timestamp) -> bool:
        block_data = {
            "index": last_block.index + 1,
            "timestamp": timestamp,
            "transactions": [tx.to_dict() for tx in pending_transactions],
            "previous_hash": last_block.hash,
            "nonce": nonce,
        }
        block_string = json.dumps(block_data, sort_keys=True)
        computed_hash = hashlib.sha256(block_string.encode()).hexdigest()
        return computed_hash[:difficulty] == "0" * difficulty

    # def mine_gpu(self):
    #     last_block = self.blockchain.last_block
    #     
    #     block_data = {
    #         "index": len(self.blockchain.chain),
    #         "timestamp": time(),
    #         "transactions": [t.__dict__ for t in self.blockchain.pending_transactions],
    #         "previous_hash": last_block.hash,
    #     }
    #     block_string = json.dumps(block_data, sort_keys=True)
    #     
    #     target_hash = "0" * self.blockchain.difficulty + "f" * (64 - self.blockchain.difficulty)
    #     target = bytes.fromhex(target_hash)
    # 
    #     result_nonce = np.zeros(1, dtype=np.uint32)
    #     result_nonce_gpu = cuda.mem_alloc(result_nonce.nbytes)
    #     cuda.memcpy_htod(result_nonce_gpu, result_nonce)
    # 
    #     block_data_gpu = cuda.mem_alloc(len(block_string))
    #     cuda.memcpy_htod(block_data_gpu, block_string.encode('utf-8'))
    # 
    #     target_gpu = cuda.mem_alloc(len(target))
    #     cuda.memcpy_htod(target_gpu, target)
    # 
    #     # Define grid and block dimensions
    #     threads_per_block = 256
    #     blocks_per_grid = (pycuda.autoinit.device.get_attribute(cuda.device_attribute.MULTIPROCESSOR_COUNT) * 16)
    # 
    #     self.find_nonce(
    #         block_data_gpu,
    #         np.int32(len(block_string)),
    #         target_gpu,
    #         result_nonce_gpu,
    #         block=(threads_per_block, 1, 1),
    #         grid=(blocks_per_grid, 1)
    #     )
    # 
    #     cuda.memcpy_dtoh(result_nonce, result_nonce_gpu)
    #     return result_nonce[0]
