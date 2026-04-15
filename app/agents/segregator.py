import os
import json
import base64
import random
from groq import Groq
from dotenv import load_dotenv
import app.utils.prompts as prompts

load_dotenv()

def get_api_keys():
    raw_keys = os.getenv("API_KEYS", "[]")
    try:
        keys_list = json.loads(raw_keys)
        return [k.strip() for k in keys_list if k.strip()]
    except:
        return [k.strip() for k in raw_keys.replace("[", "").replace("]", "").replace('"', '').split(",") if k.strip()]

API_KEYS = get_api_keys()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8').strip()

def classify_pages(state):
    pages = state.pages
    classifications = {}
    
    model_name = os.getenv("SEGREGATION_MODEL")
    
    for i, page_path in enumerate(pages):
        try:
            current_key = random.choice(API_KEYS)
            client = Groq(api_key=current_key)
            
            base64_image = encode_image(page_path)
            messages_payload = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": str(prompts.SEGREGATION_PROMPT)
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
                model=model_name,
                messages=messages_payload,
                temperature=0.0,
            )
            doc_type = response.choices[0].message.content.strip().lower()
            doc_type = "".join(filter(lambda x: x.isalnum() or x == '_', doc_type.split()[0]))
            
            classifications[i] = doc_type
            print(f"Page {i} routed to: {doc_type}")
            
        except Exception as e:
            print(f"Segregator failed on page {i}: {str(e)}")
            classifications[i] = "default_extraction"

    return {"classifications": classifications}