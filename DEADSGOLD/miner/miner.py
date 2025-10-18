
import hashlib
import json
from time import time
import pycuda.autoinit
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import numpy as np

from blockchain.block import Block

# CUDA kernel for SHA256 hashing
cuda_kernel = """
#include <stdio.h>
#include <string.h>

__device__ void sha256_transform(unsigned int *state, const unsigned char *block) {
    unsigned int w[64];
    for (int i = 0; i < 16; ++i) {
        w[i] = (block[i * 4] << 24) | (block[i * 4 + 1] << 16) | (block[i * 4 + 2] << 8) | block[i * 4 + 3];
    }
    for (int i = 16; i < 64; ++i) {
        unsigned int s0 = (w[i - 15] >> 7 | w[i - 15] << 25) ^ (w[i - 15] >> 18 | w[i - 15] << 14) ^ (w[i - 15] >> 3);
        unsigned int s1 = (w[i - 2] >> 17 | w[i - 2] << 15) ^ (w[i - 2] >> 19 | w[i - 2] << 13) ^ (w[i - 2] >> 10);
        w[i] = w[i - 16] + s0 + w[i - 7] + s1;
    }

    unsigned int a = state[0];
    unsigned int b = state[1];
    unsigned int c = state[2];
    unsigned int d = state[3];
    unsigned int e = state[4];
    unsigned int f = state[5];
    unsigned int g = state[6];
    unsigned int h = state[7];

    for (int i = 0; i < 64; ++i) {
        unsigned int S1 = (e >> 6 | e << 26) ^ (e >> 11 | e << 21) ^ (e >> 25 | e << 7);
        unsigned int ch = (e & f) ^ (~e & g);
        unsigned int temp1 = h + S1 + ch + 0x428a2f98 + w[i];
        unsigned int S0 = (a >> 2 | a << 30) ^ (a >> 13 | a << 19) ^ (a >> 22 | a << 10);
        unsigned int maj = (a & b) ^ (a & c) ^ (b & c);
        unsigned int temp2 = S0 + maj;

        h = g;
        g = f;
        f = e;
        e = d + temp1;
        d = c;
        c = b;
        b = a;
        a = temp1 + temp2;
    }

    state[0] += a;
    state[1] += b;
    state[2] += c;
    state[3] += d;
    state[4] += e;
    state[5] += f;
    state[6] += g;
    state[7] += h;
}

__global__ void find_nonce(const char* block_data, int block_len, const char* target, unsigned int* result_nonce) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    unsigned int nonce = idx;

    while (*result_nonce == 0) {
        char temp_data[256];
        memcpy(temp_data, block_data, block_len);
        sprintf(temp_data + block_len, "%d", nonce);
        int message_len = strlen(temp_data);

        unsigned int state[8] = {
            0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
            0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
        };

        unsigned char padded_block[64];
        int num_blocks = (message_len + 8) / 64 + 1;
        for (int i = 0; i < num_blocks; ++i) {
            int block_start = i * 64;
            int block_end = block_start + 64;
            if (block_end > message_len) {
                memset(padded_block, 0, 64);
                memcpy(padded_block, temp_data + block_start, message_len - block_start);
                padded_block[message_len - block_start] = 0x80;
                if (block_end - message_len < 8) {
                    sha256_transform(state, padded_block);
                    memset(padded_block, 0, 64);
                }
                unsigned long long bit_len = message_len * 8;
                padded_block[56] = bit_len >> 56;
                padded_block[57] = bit_len >> 48;
                padded_block[58] = bit_len >> 40;
                padded_block[59] = bit_len >> 32;
                padded_block[60] = bit_len >> 24;
                padded_block[61] = bit_len >> 16;
                padded_block[62] = bit_len >> 8;
                padded_block[63] = bit_len;
            } else {
                memcpy(padded_block, temp_data + block_start, 64);
            }
            sha256_transform(state, padded_block);
        }

        unsigned char hash[32];
        for (int i = 0; i < 8; ++i) {
            hash[i * 4] = state[i] >> 24;
            hash[i * 4 + 1] = state[i] >> 16;
            hash[i * 4 + 2] = state[i] >> 8;
            hash[i * 4 + 3] = state[i];
        }

        bool match = true;
        for (int i = 0; i < 32; ++i) {
            if (hash[i] > target[i]) {
                match = false;
                break;
            }
            if (hash[i] < target[i]) {
                break;
            }
        }

        if (match) {
            atomicExch(result_nonce, nonce);
        }
        nonce += gridDim.x * blockDim.x;
    }
}
"""

class Miner:
    def __init__(self, blockchain, use_gpu=False):
        self.blockchain = blockchain
        self.use_gpu = use_gpu
        if self.use_gpu:
            self.mod = SourceModule(cuda_kernel)
            self.find_nonce = self.mod.get_function("find_nonce")

    def mine(self):
        if self.use_gpu:
            return self.mine_gpu()
        else:
            return self.mine_cpu()

    def mine_cpu(self):
        return self.blockchain.proof_of_work()

    def mine_gpu(self):
        last_block = self.blockchain.last_block
        
        block_data = {
            "index": len(self.blockchain.chain),
            "timestamp": time(),
            "transactions": [t.__dict__ for t in self.blockchain.pending_transactions],
            "previous_hash": last_block.hash,
        }
        block_string = json.dumps(block_data, sort_keys=True)
        
        target_hash = "0" * self.blockchain.difficulty + "f" * (64 - self.blockchain.difficulty)
        target = bytes.fromhex(target_hash)

        result_nonce = np.zeros(1, dtype=np.uint32)
        result_nonce_gpu = cuda.mem_alloc(result_nonce.nbytes)
        cuda.memcpy_htod(result_nonce_gpu, result_nonce)

        block_data_gpu = cuda.mem_alloc(len(block_string))
        cuda.memcpy_htod(block_data_gpu, block_string.encode('utf-8'))

        target_gpu = cuda.mem_alloc(len(target))
        cuda.memcpy_htod(target_gpu, target)

        # Define grid and block dimensions
        threads_per_block = 256
        blocks_per_grid = (pycuda.autoinit.device.get_attribute(cuda.device_attribute.MULTIPROCESSOR_COUNT) * 16)

        self.find_nonce(
            block_data_gpu,
            np.int32(len(block_string)),
            target_gpu,
            result_nonce_gpu,
            block=(threads_per_block, 1, 1),
            grid=(blocks_per_grid, 1)
        )

        cuda.memcpy_dtoh(result_nonce, result_nonce_gpu)
        return result_nonce[0]
