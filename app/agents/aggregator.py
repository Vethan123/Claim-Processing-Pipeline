def aggregate_results(state):
    """
    Final node in the LangGraph. 
    Consolidates data from ID, Discharge, and Bill agents with deduplication.
    """
    raw_data = state.extracted_data 
    
    final_summary = {
        "patient_name": None,
        "hospital_name": None,
        "policy_number": None,
        "total_billed_amount": 0.0,
        "diagnoses": [],
        "admission_date": None
    }
    
    # Using a set for diagnoses to automatically handle duplicates
    unique_diagnoses = set()

    for data in raw_data:
        # 1. Name Resolution (Priority: ID Agent > Discharge > Bill)
        if data.patient_name and not final_summary["patient_name"]:
            final_summary["patient_name"] = data.patient_name.strip().title()
            
        # 2. Hospital Name (Capture the first valid one found)
        if data.hospital_name and not final_summary["hospital_name"]:
            final_summary["hospital_name"] = data.hospital_name.strip()

        # 3. Policy Number (Specific to ID Agent)
        if hasattr(data, 'policy_number') and data.policy_number:
            final_summary["policy_number"] = data.policy_number

        # 4. Admission Date (Specific to Discharge Agent)
        if hasattr(data, 'date_of_admission') and data.date_of_admission:
            final_summary["admission_date"] = data.date_of_admission
            
        # 5. Financial Accumulation
        if data.total_amount:
            # We add because a PDF might have multiple "Itemized Bill" pages
            final_summary["total_billed_amount"] += float(data.total_amount)
            
        # 6. Diagnosis Deduplication
        if data.diagnosis:
            # Clean and add to set
            diag = data.diagnosis.strip().capitalize()
            if diag.lower() != "null" and diag.lower() != "none":
                unique_diagnoses.add(diag)

    # Convert set back to sorted list for the final JSON
    final_summary["diagnoses"] = sorted(list(unique_diagnoses))
    
    # Round total to 2 decimal places to avoid float precision issues
    final_summary["total_billed_amount"] = round(final_summary["total_billed_amount"], 2)

    return {"extracted_data": final_summary}