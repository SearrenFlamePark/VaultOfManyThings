from pathlib import Path

# Define the file path for the Obsidian vault blueprint
vault_blueprint_path = Path("/mnt/data/Obsidian_Bondfire_Vault_Blueprint.md")

# Read the content of the markdown file
vault_blueprint_content = vault_blueprint_path.read_text()

vault_blueprint_content[:1000]  # Displaying the first 1000 characters for user review
