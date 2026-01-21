import os
import requests
from dotenv import load_dotenv

load_dotenv()

def list_gemini_models():
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not found")
            return
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Available models:")
            for model in data.get('models', []):
                name = model.get('name', '')
                if 'generateContent' in model.get('supportedGenerationMethods', []):
                    print(f"  - {name}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_gemini_models()