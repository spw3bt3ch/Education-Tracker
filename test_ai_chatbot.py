#!/usr/bin/env python3
"""
Test script for AI Chatbot functionality
This script tests the AI chatbot API endpoint to ensure it's working correctly.
"""

import requests
import json
import sys

def test_ai_chatbot():
    """Test the AI chatbot API endpoint"""
    
    # Test data - specific lesson content request
    test_data = {
        "message": "Give me a complete lesson note on Solar System for Basic 4",
        "context": "Current lesson being created:\n- Title: The Solar System\n- Subject: Basic Science\n- Week: Week 5\n- Term: First Term\n- Grade Level: Basic 4"
    }
    
    # API endpoint (adjust URL as needed)
    url = "http://localhost:5000/api/teacher/ai-chatbot"
    
    # Headers
    headers = {
        'Content-Type': 'application/json'
    }
    
    print("🤖 Testing AI Chatbot API...")
    print(f"📡 Endpoint: {url}")
    print(f"💬 Test Message: {test_data['message']}")
    print("-" * 50)
    
    try:
        # Make the request
        response = requests.post(url, headers=headers, json=test_data, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ API Response: SUCCESS")
                print(f"🤖 AI Response: {data.get('response', 'No response')}")
                print(f"⏰ Timestamp: {data.get('timestamp', 'N/A')}")
            elif data.get('status') and data.get('result'):
                print("✅ API Response: SUCCESS (Alternative Format)")
                print(f"🤖 AI Response: {data.get('result', ['No response'])[0] if data.get('result') else 'No response'}")
            else:
                print("❌ API Response: FAILED")
                print(f"🚨 Error: {data.get('error', 'Unknown error')}")
                print(f"📄 Full Response: {data}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"🚨 Error Details: {error_data}")
            except:
                print(f"🚨 Raw Response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to the server")
        print("💡 Make sure the Flask app is running on http://localhost:5000")
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def test_rapidapi_connection():
    """Test direct connection to RapidAPI ChatGPT service"""
    
    print("\n🔗 Testing RapidAPI Connection...")
    print("-" * 50)
    
    try:
        import http.client
        import json
        
        conn = http.client.HTTPSConnection("chatgpt-42.p.rapidapi.com")
        
        payload = json.dumps({
            "text": "Hello, this is a test message from the school management system."
        })
        
        headers = {
            'x-rapidapi-key': "4a0b790c5bmsh98c0a644346796ap130d54jsn28771f86e2fb",
            'x-rapidapi-host': "chatgpt-42.p.rapidapi.com",
            'Content-Type': "application/json"
        }
        
        conn.request("POST", "/aitohuman", payload, headers)
        res = conn.getresponse()
        data = res.read()
        
        print(f"📊 RapidAPI Status: {res.status}")
        
        if res.status == 200:
            print("✅ RapidAPI Connection: SUCCESS")
            print(f"🤖 Response: {data.decode('utf-8')}")
        else:
            print(f"❌ RapidAPI Error: {res.status}")
            print(f"🚨 Response: {data.decode('utf-8')}")
            
    except Exception as e:
        print(f"❌ RapidAPI Connection Error: {e}")

if __name__ == "__main__":
    print("🚀 AI Chatbot Test Suite")
    print("=" * 50)
    
    # Test RapidAPI connection first
    test_rapidapi_connection()
    
    # Test the Flask API endpoint
    test_ai_chatbot()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
    print("\n💡 To test the full functionality:")
    print("1. Start your Flask app: python app.py")
    print("2. Login as a teacher")
    print("3. Go to Create Lesson page")
    print("4. Click the AI Assistant button (robot icon)")
    print("5. Try asking questions about lesson planning!")
