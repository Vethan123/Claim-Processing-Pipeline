import fitz
import os

def process_pdf_to_images(pdf_path, output_folder="pdf_to_images"):
    # Ensure the directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    doc = fitz.open(pdf_path)
    image_paths = []
    
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_path = os.path.join(output_folder, f"page_{i}.png")
        pix.save(img_path)
        image_paths.append(img_path)
    
    doc.close()
    return image_paths