from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Annotated, Any
import operator

class ExtractionResult(BaseModel):
    patient_name: Optional[str] = None
    policy_number: Optional[str] = None
    total_amount: Optional[float] = None
    diagnosis: Optional[str] = None
    hospital_name: Optional[str] = None
    date_of_admission: Optional[str] = None

class DocumentState(BaseModel):
    pdf_path: str
    pages: List[str]
    classifications: Dict[int, str] = {}
    extracted_data: Annotated[List[Any], operator.add] = [] 
    final_result: Dict[str, Any] = {}