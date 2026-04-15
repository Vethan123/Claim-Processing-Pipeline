from dotenv import load_dotenv
load_dotenv()
import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from app.graph import create_graph
from app.utils.pdf_processor import process_pdf_to_images


app = FastAPI(title="HealthPay AI Claim Processor")

claim_graph = create_graph()

@app.post("/api/process-claim")
async def process_health_claim(
    claim_id: str = Form(...),
    file: UploadFile = File(...)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_dir = f"temp_{claim_id}_{uuid.uuid4().hex[:8]}" 
    os.makedirs(temp_dir, exist_ok=True)
    
    pdf_path = os.path.join(temp_dir, file.filename)

    try:
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        image_paths = process_pdf_to_images(pdf_path, output_folder=temp_dir)
        
        initial_state = {
            "pdf_path": pdf_path,
            "pages": image_paths,
            "classifications": {},
            "extracted_data": [],
            "errors": []
        }
        
        final_state = claim_graph.invoke(initial_state)
        
        return {
            "status": "success",
            "claim_id": claim_id, # Return the same claim_id passed in
            "data": final_state.get("final_result") # Changed to final_result for the aggregated summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pass

@app.get("/health")
def health_check():
    return {"status": "active", "model": os.getenv("SEGREGATION_MODEL")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)