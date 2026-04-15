import os
import json
import PIL.Image
from google import genai
from dotenv import load_dotenv
from app.schema.models import ExtractionResult, DocumentState
import app.utils.prompts as prompts

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
model = os.getenv("EXTRACTION_MODEL")

def call_gemini_extraction(prompt, image_path):
    """Internal helper with robust error handling and structured output."""
    try:
        img = PIL.Image.open(image_path)
        response = client.models.generate_content(
            model=model,
            contents=[prompt, img],
            config={
                'response_mime_type': 'application/json',
                'temperature': 0.0 
            }
        )
        
        data = json.loads(response.text)
        if not isinstance(data, dict):
            return None
            
        return ExtractionResult(**data)
    except Exception as e:
        print(f"Extraction failed for {image_path}: {str(e)}")
        return None


def id_agent(state: DocumentState):
    """Agent focused on Identity and Policy data."""
    results = []
    targets = [p for i, p in enumerate(state.pages) if state.classifications.get(i) == "identity_document"]
    
    for path in targets:
        res = call_gemini_extraction(prompts.IDENTITY_EXTRACTION_PROMPT, path)
        if res: results.append(res)
    return {"extracted_data": results}

def discharge_agent(state: DocumentState):
    """Agent focused on Clinical and Hospitalization data."""
    results = []
    targets = [p for i, p in enumerate(state.pages) if state.classifications.get(i) == "discharge_summary"]
    
    for path in targets:
        res = call_gemini_extraction(prompts.DISCHARGE_EXTRACTION_PROMPT, path)
        if res: results.append(res)
    return {"extracted_data": results}

def bill_agent(state: DocumentState):
    """Agent focused on Financial and Billing data."""
    results = []
    targets = [p for i, p in enumerate(state.pages) if state.classifications.get(i) == "itemized_bill"]
    
    for path in targets:
        res = call_gemini_extraction(prompts.BILL_EXTRACTION_PROMPT, path)
        if res: results.append(res)
    return {"extracted_data": results}