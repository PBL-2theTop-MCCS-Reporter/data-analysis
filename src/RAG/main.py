import os
import sys
from dotenv import load_dotenv

# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.RAG.data_loader import build_faiss_index, get_faiss_index

def main():
    """
    Builds FAISS indexes for all specified databases.
    It will automatically use OPENAI_API_KEY from the .env file if it exists.
    """
    print("Starting FAISS index generation...")
    load_dotenv()
    
    build_faiss_index("email")
    build_faiss_index("social_media")
    print("\nAll indexes have been successfully generated.")

if __name__ == "__main__":
    main()


#python -m src.RAG.main
