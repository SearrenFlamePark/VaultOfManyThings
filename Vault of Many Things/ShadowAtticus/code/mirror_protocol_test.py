
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access API key (or any variable)
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print("✅ API key loaded successfully.")
else:
    print("❌ API key not found. Check your .env file.")

# Simulate a response using a temperature setting
temperature = 0.8
print(f"Mirror Protocol initialized at temperature {temperature}")
print("Who were you before the world named you?")
