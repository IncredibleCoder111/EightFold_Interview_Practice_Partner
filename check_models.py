import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env file")
else:
    print(f"✅ Key found: {api_key[:5]}...")
    genai.configure(api_key=api_key)
    
    print("\n🔍 Scanning for available models...")
    try:
        available = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # We only want the part after "models/"
                clean_name = m.name.replace("models/", "")
                available.append(clean_name)
                print(f"   • {clean_name}")
        
        if not available:
            print("\n⚠️ No models found. You might need to enable the 'Generative Language API' in Google Cloud Console.")
        else:
            print("\n✅ SUCCESS! Use one of these names in your main.py:")
            print(f'   model="{available[0]}"')
            
    except Exception as e:
        print(f"\n❌ Error listing models: {e}")