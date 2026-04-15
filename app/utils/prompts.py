SEGREGATION_PROMPT = """
ACT AS: A medical document dispatcher for an insurance automation pipeline.
TASK: Analyze the provided image and determine which extraction agent should process it.

CLASSIFICATION & ROUTING RULES:
- If document is a Govt ID, PAN, or Insurance TPA card -> Return: id_agent
- If document is a Discharge Summary or Admission Note -> Return: discharge_agent
- If document is an Itemized Bill, Invoice, or Break-up of charges -> Return: bill_agent
- If document is any OTHER medical document (Claim Form, Prescription, Lab Report, etc.) -> Return: default_agent
- If document is blank, a cover page, or completely irrelevant -> Return: skip

OUTPUT FORMAT:
- Return ONLY the agent name (id_agent, discharge_agent, bill_agent, default_agent, or skip).
- No markdown, no explanation.
""",
IDENTITY_EXTRACTION_PROMPT = """
ROLE: You are an expert Medical Registrar specializing in Insurance Verification.
TASK: Extract Patient Identity and Insurance Policy details from the provided image.

EXTRACTION RULES:
- patient_name: Locate the full legal name. Ignore 'Attending Physician' names.
- policy_number: Identify the unique identifier. Look for labels like 'Policy No', 'Member ID', 'UHID', or 'Group Number'.
- STRICTNESS: If the document is blurry or the value is missing, return null. 

JSON STRUCTURE:
{ 
    "patient_name": "string or null",
    "policy_number": "string or null",
    "total_amount": null,
    "diagnosis": null,
    "hospital_name": null,
    "date_of_admission": null
}
"""
DISCHARGE_EXTRACTION_PROMPT = """
ROLE: You are a Clinical Document Auditor.
TASK: Extract clinical history and admission metadata from this Discharge Summary.

EXTRACTION RULES:
- diagnosis: Extract the 'Final Diagnosis' or 'Primary Impression'. Concatenate multiple diagnoses if necessary into a single string.
- hospital_name: Extract the formal name of the medical facility (usually found in the header).
- date_of_admission: Extract the date the patient was admitted. Standardize to YYYY-MM-DD if possible.
- patient_name: Verify against the 'Patient Details' section of the summary.

JSON STRUCTURE:
{
    "patient_name": "string or null",
    "policy_number": null,
    "total_amount": null,
    "diagnosis": "string or null",
    "hospital_name": "string or null",
    "date_of_admission": "string or null"
}
"""
BILL_EXTRACTION_PROMPT = """
ROLE: You are a Forensic Accountant specializing in healthcare billing audits.
TASK: Extract and validate the financial totals from this Itemized Bill.

EXTRACTION RULES:
- total_amount: 
    1. Locate the 'Grand Total', 'Total Amount Due', or 'Net Payable'.
    2. If a summary table is missing, sum the 'Amount' column for all line items.
    3. FORMATTING: Return ONLY a float/decimal. Remove '$', 'Rs.', 'INR', and all commas (e.g., "1,250.50" becomes 1250.50).
- hospital_name: Extract the billing entity's name from the letterhead.
- patient_name: Look for 'Bill To' or 'Patient Name'.

CRITICAL NEGATIVE CONSTRAINT:
- Do NOT include tax amounts or discounts as the total_amount unless they are already factored into the 'Net Payable'.
- Return 0.0 if no financial figures are legible.

JSON STRUCTURE:
{
    "patient_name": "string or null",
    "policy_number": null,
    "total_amount": float,
    "diagnosis": null,
    "hospital_name": "string or null",
    "date_of_admission": null
}
"""
DEFAULT_EXTRACTION_PROMPT = """
ROLE: Medical Document Indexer.
TASK: Extract any visible patient or hospital metadata from this general medical document.

EXTRACTION RULES:
- Scan the document for patient_name, hospital_name, and any dates.
- Since this is a general document, many fields will be null.
- If you see a 'Document Date', use it for date_of_admission.

JSON STRUCTURE:
{
    "patient_name": "string or null",
    "policy_number": null,
    "total_amount": 0.0,
    "diagnosis": "Summarize the document type (e.g., Lab Report, Claim Form)",
    "hospital_name": "string or null",
    "date_of_admission": "string or null"
}
"""