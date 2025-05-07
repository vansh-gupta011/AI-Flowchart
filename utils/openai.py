import os
import sys
from openai import OpenAI

OPEN_AI_KEY = os.getenv("OPENAI_API_KEY")

# print("OPEN_AI_KEY",OPEN_AI_KEY)

if not OPEN_AI_KEY:
    print("Error: OPENAI_API_KEY is not set in the environment.")
    sys.exit(1)

def get_openai_client():
    client = OpenAI(api_key=OPEN_AI_KEY)
    # print(client)
    return client
