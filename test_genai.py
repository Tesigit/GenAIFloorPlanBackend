import os
import warnings
import google.generativeai as genai
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
load_dotenv()

key = os.getenv("GEMINI_API_KEY")
print(f"Key loaded: {'Yes' if key else 'No'}")
try:
    print(f"GenAI Version: {genai.__version__}")
except:
    print("GenAI Version: unknown")

if not key:
    print("No API Key!")
    exit(1)

genai.configure(api_key=key)

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Generating...")
    response = model.generate_content("Hello")
    print(f"Response: {response.text.strip()}")
except Exception as e:
    print(f"Error: {e}")
