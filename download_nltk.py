"""Download required NLTK data"""
import nltk

print("Downloading NLTK data...")
try:
    nltk.download('punkt', quiet=True)
    print("✅ NLTK data downloaded successfully")
except Exception as e:
    print(f"⚠️  NLTK download warning: {e}")
    print("   (This is usually fine - PorterStemmer doesn't require downloads)")
