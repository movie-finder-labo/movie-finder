import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / "..env")

def get_openai_client():
    """Get OpenAI client - initialize only when needed"""
    from openai import OpenAI
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(f"Missing OPENAI_API_KEY in {ROOT / '..env'}")
    
    return OpenAI(api_key=api_key)

conversation_history = [
    {
        "role": "system",
        "content": """You are a helpful movie recommendation assistant.
        Based on your conversations you provide personalized movie suggestions based on user preferences.
        Continue your conversation until you figure out what would be a good movie for the user to watch,
        then recommend it to the user."""
    }
]


def ask_openai(question: str) -> str:
    """Ask OpenAI a question and get response with conversation memory"""
    try:
        client = get_openai_client()

        conversation_history.append({"role": "user", "content": question})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_history,
            max_tokens=400
        )

        answer = response.choices[0].message.content.strip()
        
        conversation_history.append({"role": "assistant", "content": answer})

        return answer

    except Exception as e:
        raise Exception(f"OpenAI API error: {e}")
