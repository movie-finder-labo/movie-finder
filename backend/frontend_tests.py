#!/usr/bin/env python3
"""
Flask Frontend Test Runner
Tests critical frontend functionality
"""
import sys
import os
from flask import Flask

def test_flask_routes():
    """Test basic Flask route functionality"""
    print("Testing Flask Routes...")
    
    try:
        # Import your Flask app
        from main import app
        
        app.testing = True
        client = app.test_client()
        
        # Test homepage
        response = client.get('/')
        if response.status_code == 200 and b'MoviesNemt AI' in response.data:
            print("  PASS - Homepage loads correctly")
        else:
            print("  FAIL - Homepage loading")
            return False
        
        # Test static files
        response = client.get('/static/style.css')
        if response.status_code == 200:
            print("  PASS - CSS file accessible")
        else:
            print("  FAIL - CSS file missing")
            
        response = client.get('/static/app.js')
        if response.status_code == 200:
            print("  PASS - JavaScript file accessible")
        else:
            print("  FAIL - JavaScript file missing")
            
        return True
        
    except Exception as e:
        print(f"  FAIL - Flask setup error: {e}")
        return False

def test_javascript_functions():
    """Test JavaScript function availability"""
    print("Testing JavaScript Functions...")
    
    try:
        # Read the app.js file
        js_path = os.path.join('static', 'app.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Check for critical functions
        functions_to_check = [
            ('addMessage', 'Chat message function'),
            ('sendMessage', 'Message sending function'),
            ('getAIResponse', 'AI response function'),
            ('getBasicAIResponse', 'Fallback response function'),
            ('renderMovies', 'Movie rendering function'),
            ('calculateMatchScore', 'Recommendation scoring'),
            ('getRecommendedMovies', 'Movie recommendations'),
            ('getUserRating', 'Rating retrieval'),
            ('saveUserRating', 'Rating storage'),
            ('handleStarClick', 'Star rating handler')
        ]
        
        all_found = True
        for func_name, description in functions_to_check:
            if f'function {func_name}' in js_content or f'{func_name} = function' in js_content or f'{func_name}(' in js_content:
                print(f"  PASS - {description} found")
            else:
                print(f"  FAIL - {description} missing")
                all_found = False
        
        return all_found
        
    except FileNotFoundError:
        print("  FAIL - JavaScript file not found")
        return False
    except Exception as e:
        print(f"  FAIL - JavaScript test error: {e}")
        return False

def test_chat_functionality():
    """Test chat-related functionality"""
    print("Testing Chat Functionality...")
    
    try:
        js_path = os.path.join('static', 'app.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        checks = [
            ('userInput.value.trim()', 'Input validation'),
            ('addMessage(message, true)', 'User message handling'),
            ('addMessage(aiResponse', 'AI response handling'),
            ('typing-indicator', 'Typing indicator'),
            ('chatMessages.appendChild', 'Chat DOM updates')
        ]
        
        all_good = True
        for check, description in checks:
            if check in js_content:
                print(f"  PASS - {description} found")
            else:
                print(f"  FAIL - {description} missing")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"  FAIL - Chat functionality test error: {e}")
        return False

def test_ai_system():
    """Test AI response system"""
    print("Testing AI Response System...")
    
    try:
        js_path = os.path.join('static', 'app.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        checks = [
            ('getAIResponse', 'AI response function'),
            ('getBasicAIResponse', 'Fallback system'),
            ('fetch', 'API calls'),
            ('/chat/ask', 'Chat endpoint integration'),
            ('catch (error)', 'Error handling')
        ]
        
        all_good = True
        for check, description in checks:
            if check in js_content:
                print(f"  PASS - {description} found")
            else:
                print(f"  FAIL - {description} missing")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"  FAIL - AI system test error: {e}")
        return False

def test_recommendation_system():
    """Test movie recommendation functionality"""
    print("Testing Recommendation System...")
    
    try:
        js_path = os.path.join('static', 'app.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        checks = [
            ('calculateMatchScore', 'Match scoring'),
            ('userPreferences.genres', 'User preferences usage'),
            ('getRecommendedMovies', 'Recommendation logic'),
            ('renderMovies', 'Movie rendering'),
            ('moviesGrid.innerHTML', 'DOM updates')
        ]
        
        all_good = True
        for check, description in checks:
            if check in js_content:
                print(f"  PASS - {description} found")
            else:
                print(f"  FAIL - {description} missing")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"  FAIL - Recommendation system test error: {e}")
        return False

def test_rating_system():
    """Test movie rating functionality"""
    print("Testing Rating System...")
    
    try:
        js_path = os.path.join('static', 'app.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        checks = [
            ('getUserRating', 'Rating retrieval'),
            ('saveUserRating', 'Rating storage'),
            ('handleStarClick', 'Star interaction'),
            ('data-rating', 'Rating data attributes'),
            ('localStorage', 'Browser storage')
        ]
        
        all_good = True
        for check, description in checks:
            if check in js_content:
                print(f"  PASS - {description} found")
            else:
                print(f"  FAIL - {description} missing")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"  FAIL - Rating system test error: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting Frontend Test Suite")
    print("=" * 50)
    
    tests = [
        test_flask_routes,
        test_javascript_functions,
        test_chat_functionality,
        test_ai_system,
        test_recommendation_system,
        test_rating_system
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Empty line between test groups
        except Exception as e:
            print(f"Test {test.__name__} crashed: {e}")
            print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests completed successfully")
        return 0
    else:
        print("Some tests failed. Please check the implementation.")
        return 1

if __name__ == '__main__':
    # Make sure we're in the right directory
    if not os.path.exists('main.py'):
        print("Error: Please run this from your project root directory (where main.py is)")
        sys.exit(1)
    
    sys.exit(main())