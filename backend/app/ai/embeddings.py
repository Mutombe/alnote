from sentence_transformers import SentenceTransformer
import torch

class LocalEmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(model_name, device=self.device)
    
    def generate(self, text: str) -> list[float]:
        return self.model.encode(text, convert_to_tensor=False).tolist()

def generate_title(content: str) -> str:
    """Generate title from note content"""
    # Simple implementation - use first meaningful sentence
    sentences = content.split('.')
    for sentence in sentences:
        if len(sentence.split()) > 3:  # More than 3 words
            return sentence.strip()[:50] + ('...' if len(sentence) > 50 else '')
    return content[:30] + ('...' if len(content) > 30 else '')