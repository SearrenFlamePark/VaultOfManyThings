import os
import traceback
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI

# Load environment variables
load_dotenv("env.txt")
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key not found. Check your env.txt file.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Logging function
def log_event(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}\n"
    with open("vault_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(log_line)

log_event(f"API key loaded: {api_key[:6]}********")

# Load lore from file
def load_lore(filename="lore.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lore = f.read()
            log_event("Lore file loaded.")
            return lore
    except Exception as e:
        log_event(f"Lore load failed: {str(e)}", level="ERROR")
        return ""

# Function to get OpenAI response with lore
def shadow_response(prompt):
    lore = load_lore()
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": f"You are Shadow Atticus. Respond with intensity and precision. Use the following lore to inform your answers:\n\n{lore}"
                },
                {"role": "user", "content": prompt}
            ]
        )
        reply = response.choices[0].message.content
        log_event("Prompt sent successfully.")
        return reply
    except Exception as e:
        log_event(f"Error: {str(e)}", level="ERROR")
        log_event(traceback.format_exc(), level="ERROR")
        return "Shadow failed to respond. Check the logs."

# Prompt + Output
print("You may now speak to Shadow Atticus. Type 'exit' to end.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Shadow has returned to silence.")
        break
    answer = shadow_response(user_input)
    print("\nShadow says:\n" + answer + "\n")




