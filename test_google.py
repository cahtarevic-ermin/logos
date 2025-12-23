import google.generativeai as genai
from app.config import get_settings

settings = get_settings()
genai.configure(api_key=settings.google_api_key)

# List available models
print("Available models:")
for model in genai.list_models():
    print(f"  - {model.name}")
