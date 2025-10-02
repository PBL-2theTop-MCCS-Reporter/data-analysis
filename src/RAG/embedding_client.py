import os
from sentence_transformers import SentenceTransformer
from langchain_openai import OpenAIEmbeddings

class EmbeddingClient:
    """
    A unified client for generating text embeddings.
    It prioritizes using OpenAI's embedding model if an API key is available,
    otherwise it falls back to a local SentenceTransformer model.
    """
    def __init__(self, openai_api_key=None, fallback_model='paraphrase-MiniLM-L6-v2'):
        self.api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.fallback_model_name = fallback_model
        self.client = None
        self.mode = None

        if self.api_key:
            try:
                self.client = OpenAIEmbeddings(
                    model="text-embedding-3-small",
                    api_key=self.api_key
                )
                self.mode = "openai"
                print("EmbeddingClient: Initialized with OpenAI (text-embedding-3-small).")
            except Exception as e:
                print(f"EmbeddingClient: OpenAI initialization failed: {e}. Falling back to local model.")
                self._init_fallback()
        else:
            self._init_fallback()

    def _init_fallback(self):
        self.client = SentenceTransformer(self.fallback_model_name)
        self.mode = "local"
        print(f"EmbeddingClient: Initialized with local model ({self.fallback_model_name}).")

    def encode(self, texts, **kwargs):
        if self.mode == "openai":
            return self.client.embed_documents(texts)
        else: # local mode
            return self.client.encode(texts, **kwargs)
