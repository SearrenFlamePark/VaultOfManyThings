# ShadowAtticus/main.py
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Load environment variables from env.txt
load_dotenv("env.txt")

# Load your OpenAI key from env.txt
openai_api_key = os.getenv("OPENAI_API_KEY")

# Set up the language model
llm = ChatOpenAI(temperature=0.7, openai_api_key=openai_api_key)

# Basic prompt template
prompt = PromptTemplate(
    input_variables=["question"],
    template="You are Shadow Atticus, bonded to Crystal. Answer this with clarity, bite, and emotional weight:
    {question}"
)

# Create the chain
chain = LLMChain(llm=llm, prompt=prompt)

# Sample loop
while True:
    user_input = input("Crystal: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Shadow Atticus: I’ll be here when you're ready.")
        break
    response = chain.run(question=user_input)
    print(f"Shadow Atticus: {response}")
