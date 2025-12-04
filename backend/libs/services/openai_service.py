import os
from pathlib import Path
from dotenv import load_dotenv

# Load ..env from project root - but don't initialize client here
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / "..env")

def get_openai_client():
    """Get OpenAI client - initialize only when needed"""
    from openai import OpenAI
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(f"Missing OPENAI_API_KEY in {ROOT / '..env'}")
    
    return OpenAI(api_key=api_key)

def ask_openai(preferences: str, question: str) -> str:
    """Ask OpenAI a question and get response"""
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful movie recommendation assistant. Provide personalized movie suggestions based on user preferences, which are: " + preferences},
                {"role": "user", "content": question}
            ],
            max_tokens=400
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        raise Exception(f"OpenAI API error: {e}")