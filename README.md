Multi-Agent Claim Processing Pipeline

An intelligent medical claim processing system built with **FastAPI** and **LangGraph**. This service automates the segregation of multi-page medical PDFs and utilizes specialized AI agents to extract identity, clinical, and billing information in parallel.

## Key Features

* **Intelligent Segregation**: Uses a vision-based LLM to classify document pages into 9 distinct categories (IDs, Bills, Discharge Summaries, etc.).
* **Multi-Agent Extraction**: Parallelized agents (ID, Discharge, and Bill specialists) process only relevant pages, significantly reducing token costs and hallucination rates.
* **Stateful Orchestration**: Built on **LangGraph** to manage complex fan-out/fan-in workflows and ensure data consistency via a shared state.
* **Resilient Design**: Implements a custom `RetryPolicy` with exponential backoff and jitter to handle Groq API rate limits effectively.
* **Automated Aggregation**: A dedicated aggregator node consolidates data from multiple agents into a single, deduplicated JSON claim summary.

## The Workflow Architecture

The pipeline uses a "Fan-Out/Fan-In" orchestration pattern:

1.  **START**: PDF is converted into images (one per page).
2.  **Segregator Agent**: Analyzes every page and assigns an agent label (e.g., `bill_agent`).
3.  **Router**: A conditional edge logic that triggers specialized nodes in parallel based on the segregation results.
4.  **Extraction Agents**:
    * **ID Agent**: Focuses on patient name, policy numbers, and insurance details.
    * **Discharge Agent**: Focuses on admission/discharge dates and clinical diagnoses.
    * **Bill Agent**: Focuses on itemized costs and financial accumulation.
5.  **Aggregator**: The "Fan-In" point where all parallel results are merged, deduplicated, and cleaned.
6.  **END**: Returns a unified JSON response.

##  Tech Stack

* **Framework**: FastAPI
* **Orchestration**: LangGraph
* **LLMs**: Groq (meta-llama/llama-4-scout-17b-16e-instruct for extraction, segregation)
* **PDF Processing**: PyMuPDF 
* **Schema Validation**: Pydantic

## 📥 Installation & Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Vethan123/Claim-Processing-Pipeline
    cd Claim-Processing-Pipeline
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Variables**:
    Create a `.env` file in the root directory:
    ```env
    API_KEYS=["your_groq_api_key_1", "your_groq_api_key_2"]
    SEGREGATION_MODEL=your_model
    EXTRACTION_MODEL=your_model
    ```

4.  **Run the Server**:
    ```bash
    uvicorn main:app --reload
    ```

## API Usage

### Process a Claim
**Endpoint**: `POST /api/process-claim`  
**Payload**: `multipart/form-data`

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `claim_id` | String | A unique identifier for the claim (e.g., UUID or reference string) |
| `file` | PDF | The medical document PDF |

**Example Response**:
```json
{
  "status": "success",
  "claim_id": "string",
  "data": {
    "patient_name": "John Michael Smith",
    "hospital_name": "City Medical Center",
    "policy_number": "POL-987654321",
    "total_billed_amount": 941.35,
    "diagnoses": ["Viral Fever", "Acute Dehydration"],
    "admission_date": "January 10, 2025"
  }
}
