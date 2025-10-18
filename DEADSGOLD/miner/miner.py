
import hashlib
import json
from time import time
# import pycuda.autoinit
# import pycuda.driver as cuda
# from pycuda.compiler import SourceModule
# import numpy as np

from blockchain.block import Block



class Miner:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.use_gpu = False

    def mine(self):
        return self.mine_cpu()

    def mine_cpu(self):
        return self.blockchain.proof_of_work()

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
