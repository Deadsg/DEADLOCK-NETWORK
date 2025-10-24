import json
import os

def update_token_metadata(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    with open(file_path, 'r') as f:
        metadata = json.load(f)

    print("Current Token Metadata:")
    print(json.dumps(metadata, indent=2))

    while True:
        print("\nSelect a field to update (or 'done' to finish):")
        print("1. Name")
        print("2. Symbol")
        print("3. Description")
        print("4. Image")
        print("5. Attributes")
        print("6. View Current Metadata")
        print("7. Save and Exit")

        choice = input("Enter your choice: ").strip().lower()

        if choice == '1' or choice == 'name':
            new_name = input(f"Enter new name (current: {metadata.get('name')}): ").strip()
            if new_name:
                metadata['name'] = new_name
        elif choice == '2' or choice == 'symbol':
            new_symbol = input(f"Enter new symbol (current: {metadata.get('symbol')}): ").strip()
            if new_symbol:
                metadata['symbol'] = new_symbol
        elif choice == '3' or choice == 'description':
            new_description = input(f"Enter new description (current: {metadata.get('description')}): ").strip()
            if new_description:
                metadata['description'] = new_description
        elif choice == '4' or choice == 'image':
            new_image = input(f"Enter new image URL (current: {metadata.get('image')}): ").strip()
            if new_image:
                metadata['image'] = new_image
        elif choice == '5' or choice == 'attributes':
            if 'attributes' not in metadata or not isinstance(metadata['attributes'], list):
                metadata['attributes'] = []
            
            print("\n--- Managing Attributes ---")
            for i, attr in enumerate(metadata['attributes']):
                print(f"{i+1}. Trait Type: {attr.get('trait_type')}, Value: {attr.get('value')}")
            
            attr_choice = input("Enter 'add', 'edit <number>', 'remove <number>', or 'back': ").strip().lower().split(maxsplit=1)
            
            if attr_choice[0] == 'add':
                trait_type = input("Enter new trait type: ").strip()
                value = input("Enter new trait value: ").strip()
                if trait_type and value:
                    metadata['attributes'].append({"trait_type": trait_type, "value": value})
                    print("Attribute added.")
                else:
                    print("Trait type and value cannot be empty.")
            elif attr_choice[0] == 'edit' and len(attr_choice) > 1:
                try:
                    index = int(attr_choice[1]) - 1
                    if 0 <= index < len(metadata['attributes']):
                        current_attr = metadata['attributes'][index]
                        new_trait_type = input(f"Edit trait type (current: {current_attr.get('trait_type')}): ").strip()
                        new_value = input(f"Edit value (current: {current_attr.get('value')}): ").strip()
                        if new_trait_type:
                            metadata['attributes'][index]['trait_type'] = new_trait_type
                        if new_value:
                            metadata['attributes'][index]['value'] = new_value
                        print("Attribute updated.")
                    else:
                        print("Invalid attribute number.")
                except ValueError:
                    print("Invalid attribute number.")
            elif attr_choice[0] == 'remove' and len(attr_choice) > 1:
                try:
                    index = int(attr_choice[1]) - 1
                    if 0 <= index < len(metadata['attributes']):
                        removed_attr = metadata['attributes'].pop(index)
                        print(f"Removed attribute: {removed_attr.get('trait_type')}: {removed_attr.get('value')}")
                    else:
                        print("Invalid attribute number.")
                except ValueError:
                    print("Invalid attribute number.")
            elif attr_choice[0] == 'back':
                pass
            else:
                print("Invalid attribute command.")

        elif choice == '6' or choice == 'view':
            print("\nCurrent Token Metadata:")
            print(json.dumps(metadata, indent=2))
        elif choice == '7' or choice == 'save' or choice == 'done':
            with open(file_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            print(f"Metadata updated and saved to {file_path}")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    token_json_path = "C:/Users/deads/OneDrive/Documents/AGI/DEADLOCK-NETWORK/DEADSGOLD/token.json"
    update_token_metadata(token_json_path)
