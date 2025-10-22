
import time
import multiprocessing
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.system_program import ID as SYSTEM_PROGRAM_ID
from solana.rpc.api import Client
from solders.transaction import Transaction
from solders.instruction import Instruction, AccountMeta
from spl.token.constants import TOKEN_PROGRAM_ID
import hashlib

# TODO: Replace with the actual deployed program ID
PROGRAM_ID = Pubkey.from_string("8KWTy2J2ygMFoht4KbL2UNbAkYnt8rPsSW96TrUdxcda")
TOKEN_MINT = Pubkey.from_string("HPUj1r6RLnWuP63a6H2D2DgEGfUAL3Bw9woC7xBt3kLj")

# Seeds for PDA
CONFIG_SEED = b"config"
MINER_PROOF_SEED = b"miner_proof"
BUS_SEED = b"bus"

def get_config_pda():
    return Pubkey.find_program_address([CONFIG_SEED], PROGRAM_ID)

def get_miner_proof_pda(authority: Pubkey):
    return Pubkey.find_program_address([MINER_PROOF_SEED, bytes(authority)], PROGRAM_ID)

def get_bus_pda(bus_number: int):
    return Pubkey.find_program_address([BUS_SEED, bus_number.to_bytes(8, 'little')], PROGRAM_ID)

class Miner:
    def __init__(self, rpc_url="https://api.devnet.solana.com"):
        self.http_client = Client(rpc_url)
        self.payer = self._load_keypair()

    def _load_keypair(self):
        with open("miner_keypair.json", "r") as f:
            return Keypair.from_json(f.read())

    def _mine_worker(self, challenge: bytes, difficulty: int, start_nonce: int, end_nonce: int, result_queue):
        for nonce in range(start_nonce, end_nonce):
            hasher = hashlib.sha3_256()
            hasher.update(challenge)
            hasher.update(nonce.to_bytes(8, 'little'))
            hash_result = hasher.digest()

            leading_zeros = 0
            for byte in hash_result:
                if byte == 0:
                    leading_zeros += 8
                else:
                    leading_zeros += byte.leading_zeros()
                    break
            
            if leading_zeros >= difficulty:
                result_queue.put(nonce)
                return

    def mine(self):
        config_pda, _ = get_config_pda()

        try:
            config_account_info = self.http_client.get_account_info(config_pda)
            config_data = config_account_info.value.data
            challenge = config_data[32:64]
            difficulty = int.from_bytes(config_data[64:72], 'little')
        except Exception as e:
            print(f"Could not fetch config: {e}")
            return

        print(f"Challenge: {challenge.hex()}")
        print(f"Difficulty: {difficulty}")

        num_processes = multiprocessing.cpu_count()
        result_queue = multiprocessing.Queue()
        processes = []

        chunk_size = 1_000_000
        nonce_start = 0

        while result_queue.empty():
            for i in range(num_processes):
                start_nonce = nonce_start + i * chunk_size
                end_nonce = start_nonce + chunk_size
                p = multiprocessing.Process(target=self._mine_worker, args=(challenge, difficulty, start_nonce, end_nonce, result_queue))
                processes.append(p)
                p.start()
            
            nonce_start += num_processes * chunk_size

            while result_queue.empty():
                time.sleep(0.1)
                if not any(p.is_alive() for p in processes):
                    break

            for p in processes:
                if p.is_alive():
                    p.terminate()
            
            processes = []

        nonce = result_queue.get()
        print(f"Found nonce: {nonce}")

        miner_proof_pda, _ = get_miner_proof_pda(self.payer.pubkey())
        bus_pda, _ = get_bus_pda(0)
        
        miner_token_account = Pubkey.find_program_address(
            [bytes(self.payer.pubkey()), bytes(TOKEN_PROGRAM_ID), bytes(TOKEN_MINT)],
            Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
        )[0]

        accounts = [
            AccountMeta(pubkey=miner_proof_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=self.payer.pubkey(), is_signer=True, is_writable=False),
            AccountMeta(pubkey=config_pda, is_signer=False, is_writable=False),
            AccountMeta(pubkey=bus_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=miner_token_account, is_signer=False, is_writable=True),
            AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=TOKEN_MINT, is_signer=False, is_writable=False),
        ]

        instruction_data = b'\x02' + nonce.to_bytes(8, 'little')
        
        instruction = Instruction(
            program_id=PROGRAM_ID,
            accounts=accounts,
            data=instruction_data
        )

        transaction = Transaction().add(instruction)
        
        try:
            result = self.http_client.send_transaction(transaction, self.payer)
            print(f"Transaction successful: {result.value}")
        except Exception as e:
            print(f"Transaction failed: {e}")

if __name__ == "__main__":
    miner = Miner()
    miner.mine()
