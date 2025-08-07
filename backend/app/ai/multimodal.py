from transformers import pipeline
from PIL import Image
import requests
from io import BytesIO
import torch

class MultimodalProcessor:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = pipeline(
            "image-to-text",
            model="Salesforce/blip-image-captioning-base",
            device=self.device
        )
    
    def describe_image(self, image_path: str) -> str:
        """Generate description for an image"""
        try:
            result = self.model(image_path)
            return result[0]['generated_text']
        except Exception as e:
            print(f"Image description error: {e}")
            return "An image"
    
    def extract_text_from_image(self, image_path: str) -> str:
        """OCR text extraction from image"""
        # This would use a proper OCR library like Tesseract in production
        # Simplified implementation
        return "Extracted text would appear here"

def get_web_content(url: str) -> str:
    """Get and process web content"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text[:5000]  # Limit content size
        return ""
    except Exception as e:
        print(f"Web content error: {e}")
        return ""