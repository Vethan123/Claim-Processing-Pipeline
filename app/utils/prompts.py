SEGREGATION_PROMPT = """
ACT AS: A medical document classification expert.
TASK: Identify the document type for the provided image page.

CLASSIFICATION RULES:
1. claim_forms: Official insurance claim application forms.
2. cheque_or_bank_details: Images of cancelled cheques, passbooks, or bank statements.
3. identity_document: Government IDs (Aadhaar, PAN, Passport) or Insurance TPA cards.
4. itemized_bill: Detailed break-up of costs/charges with individual line items.
5. discharge_summary: Hospital document summarizing treatment, diagnosis, and stay details.
6. prescription: Doctor's handwritten or printed advice for medicines.
7. investigation_report: Lab results, X-rays, Blood tests, or Scans.
8. cash_receipt: Small slips or receipts confirming a specific payment made.
9. other: Any page that does not fit the above (e.g., blank pages, cover letters).

OUTPUT FORMAT:
- Return ONLY the category name from the list above.
- No markdown, no bolding, no explanation.
- Example Output: itemized_bill
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