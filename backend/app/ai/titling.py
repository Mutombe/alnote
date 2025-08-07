from transformers import pipeline
from config import settings
import torch
from typing import Optional

class TitleGenerator:
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        self.model = pipeline(
            "text-generation", 
            model=settings.TITLE_GENERATION_MODEL,
            device=self.device
        )
    
    def generate_title(self, content: str) -> str:
        if len(content) < 50:
            return content[:30] + ('...' if len(content) > 30 else '')
        
        # Generate title using the first 200 characters
        prompt = f"Generate a concise title for the following text:\n{content[:200]}\nTitle:"
        
        try:
            result = self.model(
                prompt,
                max_length=30,
                num_return_sequences=1,
                truncation=True
            )
            title = result[0]['generated_text'].replace(prompt, '').strip()
            
            # Clean up any extra text
            title = title.split('\n')[0].split('.')[0]
            return title[:100]  # Limit title length
        except Exception as e:
            print(f"Title generation error: {e}")
            # Fallback to first meaningful sentence
            sentences = content.split('.')
            for sentence in sentences:
                if len(sentence.split()) > 3:  # More than 3 words
                    return sentence.strip()[:50] + ('...' if len(sentence) > 50 else '')
            return content[:30] + ('...' if len(content) > 30 else '')

# Global instance for reuse
title_generator = TitleGenerator()

def generate_title(content: str) -> str:
    return title_generator.generate_title(content)