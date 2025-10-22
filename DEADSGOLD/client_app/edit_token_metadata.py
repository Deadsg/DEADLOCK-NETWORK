import json
import os

TOKEN_JSON_PATH = "DEADSGOLD/token.json"

def edit_token_metadata():
    print("Loading token information for editing...")
    try:
        with open(TOKEN_JSON_PATH, 'r') as f:
            token_info = json.load(f)
    except FileNotFoundError:
        print(f"Error: {TOKEN_JSON_PATH} not found. Please create it first.")
        return

    print("Current Token Metadata:")
    for key, value in token_info.items():
        print(f"  {key}: {value}")

    print("\n--- Edit Fields (leave blank to keep current value) ---")

    new_name = input(f"New Name (current: {token_info.get('name', 'N/A')}): ")
    if new_name:
        token_info["name"] = new_name

    new_symbol = input(f"New Symbol (current: {token_info.get('symbol', 'N/A')}): ")
    if new_symbol:
        token_info["symbol"] = new_symbol

    new_uri = input(f"New URI (current: {token_info.get('uri', 'N/A')}): ")
    if new_uri:
        token_info["uri"] = new_uri

    new_description = input(f"New Description (current: {token_info.get('description', 'N/A')}): ")
    if new_description:
        token_info["description"] = new_description

    new_image = input(f"New Image URL (current: {token_info.get('image', 'N/A')}): ")
    if new_image:
        token_info["image"] = new_image

    # For creators, it's more complex to edit interactively. For simplicity, we'll just show it.
    print("\nCreators field is complex to edit interactively. Current value:")
    print(f"  Creators: {token_info.get('creators', 'N/A')}")

    print("\nSaving updated token.json...")
    with open(TOKEN_JSON_PATH, 'w') as f:
        json.dump(token_info, f, indent=4)
    print(f"Successfully updated {TOKEN_JSON_PATH}.")

    print("\n--- On-chain Metaplex Metadata Update ---")
    print("Updating on-chain Metaplex metadata (like URI, creators) is a separate step.")
    print("It typically requires:")
    print("1. Uploading the updated metadata JSON to a decentralized storage (e.g., Arweave, IPFS).")
    print("2. Using a Metaplex SDK (often in JavaScript/TypeScript) or manually constructing transactions to update the metadata account on Solana.")
    print("The Python solana/spl-token libraries do not directly provide high-level functions for Metaplex metadata updates.")

if __name__ == '__main__':
    edit_token_metadata()
