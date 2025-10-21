
from solders.keypair import Keypair

def generate_and_save_keypair():
    """Generates a new Solana keypair and saves it to a file."""
    keypair = Keypair()
    with open("program_keypair.json", "w") as f:
        f.write(keypair.to_json())
    print(f"Generated a new keypair and saved it to program_keypair.json")
    print(f"Program ID (Public Key): {keypair.pubkey()}")

if __name__ == "__main__":
    generate_and_save_keypair()
