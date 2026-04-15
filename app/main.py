from dotenv import load_dotenv
load_dotenv()
import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from app.graph import create_graph
from app.utils.pdf_processor import process_pdf_to_images


app = FastAPI(title="HealthPay AI Claim Processor")

# Compile the LangGraph workflow
claim_graph = create_graph()

@app.post("/process-claim")
async def process_health_claim(file: UploadFile = File(...)):
    # 1. Validation: Ensure it's a PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # 2. Setup temporary workspace
    job_id = str(uuid.uuid4())
    temp_dir = f"temp_{job_id}"
    os.makedirs(temp_dir, exist_ok=True)
    
    pdf_path = os.path.join(temp_dir, file.filename)

    try:
        # 3. Save the uploaded file to disk
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 4. Convert PDF pages to images for Gemini
        # (This uses the PyMuPDF logic we wrote earlier)
        image_paths = process_pdf_to_images(pdf_path, output_folder=temp_dir)

        # 5. Initialize LangGraph State
        # We pass the image paths so the AI can "see" the document
        initial_state = {
            "pdf_path": pdf_path,
            "pages": image_paths,
            "classifications": {},
            "extracted_data": [],
            "errors": []
        }

        # 6. Execute the Workflow
        # This will run: Classify -> (Conditional Edge) -> Extract -> Aggregate
        final_state = claim_graph.invoke(initial_state)

        # 7. Return the final structured JSON
        return {
            "status": "success",
            "job_id": job_id,
            "data": final_state.get("extracted_data")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 8. Cleanup (Optional: uncomment to delete temp files after processing)
        # shutil.rmtree(temp_dir)
        pass

@app.get("/health")
def health_check():
    return {"status": "active", "model": "gemini-3.1-flash-lite-preview"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)