from google import genai
import PIL.Image
import os
import app.utils.prompts as prompts

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def classify_pages(state):
    pages = state.pages
    classifications = {}
    
    prompt = prompts.SEGREGATION_PROMPT
    model = os.getenv("SEGREGATION_MODEL")
    for i, page_path in enumerate(pages):
        img = PIL.Image.open(page_path)
        response = client.models.generate_content(
            model= model,
            contents=[prompt, img]
        )
        # Clean the response text (remove whitespace/newlines)
        doc_type = response.text.strip().lower()
        classifications[i] = doc_type
        print(f"Page {i} classified as: {doc_type}")

    return {"classifications": classifications}