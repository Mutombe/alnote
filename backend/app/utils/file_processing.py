import os
from pathlib import Path
from fastapi import UploadFile
import filetype  # Replacement for magic
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.image import partition_image
from PIL import Image
import io

async def save_upload_file(file: UploadFile, user_id: str) -> str:
    """Save uploaded file to user-specific directory"""
    user_dir = Path(f"media/{user_id}")
    user_dir.mkdir(parents=True, exist_ok=True)
    
    file_location = user_dir / file.filename
    with file_location.open("wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return str(file_location)

def extract_text_from_file(file_path: str) -> str:
    """Extract text from various file types using filetype"""
    kind = filetype.guess(file_path)
    
    if not kind:
        # Fallback to file extension if MIME detection fails
        if file_path.lower().endswith('.pdf'):
            # Use fast strategy to avoid HEIF dependency
            elements = partition_pdf(filename=file_path, strategy="fast")
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            elements = partition_image(filename=file_path)
        else:
            with open(file_path, "r", encoding='utf-8', errors='ignore') as f:
                return f.read()
        return "\n\n".join([str(el) for el in elements])
    
    file_type = kind.mime
    
    if file_type == "application/pdf":
        # Use fast strategy to avoid HEIF dependency
        elements = partition_pdf(filename=file_path, strategy="fast")
    elif "image" in file_type:
        elements = partition_image(filename=file_path)
    else:
        with open(file_path, "r", encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    return "\n\n".join([str(el) for el in elements])

def process_image(image_path: str) -> dict:
    """Process image and generate thumbnail"""
    img = Image.open(image_path)
    
    # Create thumbnail
    thumb_path = f"{image_path}_thumb.jpg"
    img.thumbnail((300, 300))
    img.save(thumb_path)
    
    return {
        "width": img.width,
        "height": img.height,
        "thumbnail": thumb_path,
        "exif": img.getexif() if hasattr(img, 'getexif') else {}
    }

def sketch_to_image(sketch_data: dict) -> str:
    """Convert sketch data to image file"""
    img = Image.new('RGB', (sketch_data['width'], sketch_data['height']), 'white')
    pixels = img.load()
    
    for stroke in sketch_data['strokes']:
        for i in range(len(stroke['points'])-1):
            x1, y1 = stroke['points'][i]
            x2, y2 = stroke['points'][i+1]
            # Simple line drawing implementation
            pixels[int(x1), int(y1)] = (0, 0, 0)
    
    sketch_path = f"sketches/{sketch_data['id']}.png"
    img.save(sketch_path)
    return sketch_path