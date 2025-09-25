#!/usr/bin/env python3
"""
Debug script to test AI responses and see what's happening
"""

import requests
import json

def test_debug_endpoint():
    """Test the debug endpoint to see raw AI responses"""
    
    url = "http://localhost:5000/api/debug/ai-test"
    
    test_data = {
        "message": "Give me a complete lesson note on Solar System for Basic 4"
    }
    
    print("🔍 Testing AI Debug Endpoint...")
    print(f"📡 URL: {url}")
    print(f"💬 Test Message: {test_data['message']}")
    print("-" * 60)
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Debug Response Received")
            print(f"🔧 API Status: {data.get('status')}")
            print(f"📝 Test Prompt: {data.get('test_prompt', 'N/A')}")
            print(f"🤖 Raw AI Response: {data.get('raw_response', 'No response')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_main_chatbot():
    """Test the main chatbot endpoint"""
    
    url = "http://localhost:5000/api/teacher/ai-chatbot"
    
    test_data = {
        "message": "Give me a complete lesson note on Solar System for Basic 4",
        "context": "Current lesson: Basic Science, Basic 4, Solar System"
    }
    
    print("\n🔍 Testing Main Chatbot Endpoint...")
    print(f"📡 URL: {url}")
    print(f"💬 Test Message: {test_data['message']}")
    print("-" * 60)
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Main Chatbot Response:")
                print(f"🤖 AI Response: {data.get('response', 'No response')}")
            else:
                print("❌ Main Chatbot Failed")
                print(f"🚨 Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 AI Response Debug Tool")
    print("=" * 60)
    
    # Test debug endpoint first
    test_debug_endpoint()
    
    # Test main chatbot
    test_main_chatbot()
    
    print("\n" + "=" * 60)
    print("🏁 Debug completed!")
    print("\n💡 Check the Flask console for debug logs when testing the chatbot.")
