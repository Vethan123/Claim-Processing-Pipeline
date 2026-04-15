from app.schema.models import DocumentState

def aggregate_results(state: DocumentState):
    """
    Final node in the LangGraph. 
    Consolidates data from all agents with safe dictionary/object access.
    """
    raw_data = state.extracted_data 
    
    print(f"DEBUG: Aggregator received {len(raw_data)} extraction results.")

    final_summary = {
        "patient_name": None,
        "hospital_name": None,
        "policy_number": None,
        "total_billed_amount": 0.0,
        "diagnoses": [],
        "admission_date": None
    }
    
    unique_diagnoses = set()

    for data in raw_data:
        def get_val(obj, key):
            if isinstance(obj, dict):
                return obj.get(key)
            return getattr(obj, key, None)

        p_name = get_val(data, "patient_name")
        if p_name and not final_summary["patient_name"]:
            name = str(p_name).strip().title()
            if len(name) > 2:
                final_summary["patient_name"] = name
            
        h_name = get_val(data, "hospital_name")
        if h_name and not final_summary["hospital_name"]:
            final_summary["hospital_name"] = str(h_name).strip()

        pol = get_val(data, "policy_number")
        if pol:
            if not final_summary["policy_number"] or len(str(pol)) > 5:
                final_summary["policy_number"] = pol

        adm_date = get_val(data, "date_of_admission")
        if adm_date and not final_summary["admission_date"]:
            final_summary["admission_date"] = adm_date
            
        amt = get_val(data, "total_amount")
        if amt:
            try:
                final_summary["total_billed_amount"] += float(amt)
            except (ValueError, TypeError):
                pass
            
        diag = get_val(data, "diagnosis")
        if diag:
            items = str(diag).split(',')
            for item in items:
                clean_diag = item.strip().capitalize()
                if clean_diag.lower() not in ["null", "none", "n/a", "unknown", ""]:
                    unique_diagnoses.add(clean_diag)

    final_summary["diagnoses"] = sorted(list(unique_diagnoses))
    final_summary["total_billed_amount"] = round(final_summary["total_billed_amount"], 2)

    if not final_summary["patient_name"]:
        final_summary["patient_name"] = "Information Not Found"

    return {"final_result": final_summary}