import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_gemini_api():
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        print(f"API Key found: {'Yes' if api_key else 'No'}")
        
        if not api_key:
            print("❌ GEMINI_API_KEY not found in .env file")
            return False
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": "Hello, this is a test message. Please respond."
                }]
            }]
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                text = data['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ Gemini API working! Response: {text[:50]}...")
                return True
        
        print(f"❌ Gemini API error: {response.status_code} - {response.text}")
        return False
        
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return False

if __name__ == "__main__":
    test_gemini_api()