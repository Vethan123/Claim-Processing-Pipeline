import os
import json
import base64
import random
import PIL.Image
from groq import Groq
from dotenv import load_dotenv
from app.schema.models import ExtractionResult, DocumentState
import app.utils.prompts as prompts

load_dotenv()

def get_api_keys():
    raw_keys = os.getenv("API_KEYS", "[]")
    try:
        keys_list = json.loads(raw_keys)
        return [k.strip() for k in keys_list if k.strip()]
    except json.JSONDecodeError:
        return [k.strip() for k in raw_keys.replace("[", "").replace("]", "").replace('"', '').split(",") if k.strip()]

API_KEYS = get_api_keys()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_groq_extraction(prompt, image_path):
    print(f"DEBUG: Extracting from {image_path} using {os.getenv('EXTRACTION_MODEL')}")
    if not API_KEYS:
        print("Error: No Groq API keys found!")
        return None

    try:
        current_key = random.choice(API_KEYS)
        current_model = os.getenv("EXTRACTION_MODEL")
        
        client = Groq(api_key=current_key)
        base64_image = encode_image(image_path)

        messages_payload = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        response = client.chat.completions.create(
            model=current_model,
            messages=messages_payload,
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        
        return ExtractionResult(**data)
        
    except Exception as e:
        print(f"Groq Extraction failed for {image_path} using {current_model}: {str(e)}")
        return None


def id_agent(state: DocumentState):
    results = []
    targets = [p for i, p in enumerate(state.pages) if state.classifications.get(i) in ["id_agent", "id_extraction", "identity_document"]]
    
    for path in targets:
        res = call_groq_extraction(prompts.IDENTITY_EXTRACTION_PROMPT, path)
        if res: results.append(res)
        
    return {"extracted_data": results}

def discharge_agent(state: DocumentState):
    results = []
    targets = [p for i, p in enumerate(state.pages) if state.classifications.get(i) in ["discharge_agent", "discharge_extraction"]]
    
    for path in targets:
        res = call_groq_extraction(prompts.DISCHARGE_EXTRACTION_PROMPT, path)
        if res: results.append(res)
        
    return {"extracted_data": results}

def bill_agent(state: DocumentState):
    results = []
    targets = [p for i, p in enumerate(state.pages) if state.classifications.get(i) in ["bill_extraction", "bill_agent"]]
    
    print(f"DEBUG: Bill Agent found {len(targets)} pages to process.") # Critical Debug line
    
    for path in targets:
        res = call_groq_extraction(prompts.BILL_EXTRACTION_PROMPT, path)
        if res: results.append(res)
        
    return {"extracted_data": results}

def default_agent(state: DocumentState):
    results = []
    targets = [p for i, p in enumerate(state.pages) if state.classifications.get(i) in ["default_agent", "default_extraction"]]
    for path in targets:
        res = call_groq_extraction(prompts.DEFAULT_EXTRACTION_PROMPT, path)
        if res: results.append(res)
        
    return {"extracted_data": results}