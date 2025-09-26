script: |
  def main(case_info):
    from datetime import datetime, timezone
    
    # Use UTC timestamp in YYYY-MM-DD_HH-MM-SS format for better readability
    utc_now = datetime.now(timezone.utc)
    utc_timestamp = utc_now.strftime("%Y-%m-%d_%H-%M-%S")
    case_number = case_info.get("case_number", "UNKNOWN")
    
    forensic_dir = f"/tmp/case_{case_number}_chrome_history_collection_{utc_timestamp}"
    
    return {
        "forensic_dir": forensic_dir,
        "utc_timestamp": utc_timestamp,
        "case_number": case_number,
        "case_id": f"CASE_{case_number}_CHROME_{utc_timestamp}"
    }
inputs:
  case_info: ${{ ACTIONS.create_case.result }}
