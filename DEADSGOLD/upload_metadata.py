import json
import requests
import os

# Try common Bundlr client package names and provide a helpful error if none are found.
try:
    from Pybundlr import Api
except ImportError:
    try:
        from pybundlr import Api
    except ImportError:
        try:
            from bundlr import Api
        except ImportError:
            raise ImportError(
                "Could not import Bundlr client. Install the Python Bundlr package, e.g. 'pip install pybundlr', "
                "or adjust the import to the package you have installed."
            )

# === CONFIGURATION ===
BUNDLR_NODE = "https://node1.bundlr.network"   # Bundlr node
CURRENCY = "solana"                            # 'solana', 'matic', or 'ethereum'
PRIVATE_KEY_PATH = os.path.expanduser("C:/Users/deads/OneDrive/Documents/AGI/DEADLOCK-NETWORK/DEADSGOLD/miner_keypair.json")
METADATA_FILE = "./token.json"

# === LOAD PRIVATE KEY ===
def load_private_key(path):
    with open(path, "r") as f:
        key = json.load(f)
    return key

# === UPLOAD METADATA ===
def upload_metadata():
    key = load_private_key(PRIVATE_KEY_PATH)

    # Initialize Bundlr client
    api = Api(BUNDLR_NODE, CURRENCY, key)

    if not os.path.exists(METADATA_FILE):
        raise FileNotFoundError(f"{METADATA_FILE} not found.")

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = f.read()

    print("Uploading metadata to Arweave via Bundlr...")
    tx = api.upload(metadata.encode("utf-8"), content_type="application/json")

    arweave_link = f"https://arweave.net/{tx.id}"
    print("\n✅ Metadata uploaded successfully!")
    print("Arweave URI:", arweave_link)
    return arweave_link


if __name__ == "__main__":
    try:
        link = upload_metadata()
        # Optionally write the link to a file for future use
        with open("metadata_uri.txt", "w") as out:
            out.write(link)
    except Exception as e:
        print("❌ Upload failed:", e)
