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

system_role = {
    "role": "system",
    "content": """You are a helpful movie recommendation assistant.
    Based on your conversations you provide personalized movie suggestions based on user preferences and user ratings of movies.
    The user has rated movies between 1 and 5 stars, where 1 star means very disliked and up to 5 stars means very liked.
    Continue your conversation until you figure out what would be a good movie for the user to watch,
    then recommend it to the user."""
}

conversation_history: dict[str, list[str]] = {}

def get_conversation(username: str) -> list[dict[str, str]] | None:
    """ Retrieves a user's conversation with the AI, if any"""
    return conversation_history.get(username)

def save_conversation(username: str, history: list[dict[str, str]]):
    """ Inserts a new question into the conversation history. Returns the full history"""
    conversation_history[username] = history
    return history

def ask_openai(username: str, preferences: str, question: str) -> str:
    """Ask OpenAI a question and get response with conversation memory"""
    try:
        client = get_openai_client()
        
        history = get_conversation(username) or [{"role": "user", "content": preferences}]
        history.append({"role": "user", "content": question})
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages= [system_role] + history,
            max_tokens=400
        )

        answer = response.choices[0].message.content.strip()
        history.append({"role": "assistant", "content": answer})
        save_conversation(username, history)
        print(history)

        return answer

    except Exception as e:
        raise Exception(f"OpenAI API error: {e}")
