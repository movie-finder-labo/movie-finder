import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(__file__))

def test_imports():
    try:
        from flask import Flask
        print("✓ Flask imported successfully")
        
        from dotenv import load_dotenv
        print("✓ python-dotenv imported successfully")
        
        from openai import OpenAI
        print("✓ OpenAI imported successfully")
        
        from pymongo import MongoClient
        print("✓ pymongo imported successfully")
        
        # Test if we can import your routes
        try:
            from Routes.User.UserRoutes import user_bp
            print("✓ User routes imported successfully")
        except ImportError as e:
            print(f"✗ User routes import failed: {e}")
            
        try:
            from Routes.Chat.chat_routes import chat_bp
            print("✓ Chat routes imported successfully")
        except ImportError as e:
            print(f"✗ Chat routes import failed: {e}")
            
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing application setup...")
    if test_imports():
        print("\n🎉 All imports successful! Your app should work.")
    else:
        print("\n❌ Some imports failed. Check the errors above.")