script: |
  def main(cases, lookup_results):
    # Add debugging
    print(f"Processing {len(cases) if cases else 0} cases")
    print(f"Lookup results: {lookup_results}")
    
    # Handle null inputs
    if not cases or not lookup_results:
        print("Missing input data")
        return []
    
    # Ensure equal lengths
    if len(cases) != len(lookup_results):
        print(f"Length mismatch: {len(cases)} cases vs {len(lookup_results)} lookups")
        return []
    
    new_cases = []
    for i, (case, lookup_result) in enumerate(zip(cases, lookup_results)):
        # If lookup_result is null, it means case doesn't exist in table = NEW case
        if lookup_result is None:
            new_cases.append(case)
            print(f"✓ New case found: {case.get('id', 'unknown')}")
        else:
            print(f"✗ Existing case skipped: {case.get('id', 'unknown')}")
    
    print(f"Returning {len(new_cases)} new cases")
    return new_cases
inputs:
  cases: ${{ ACTIONS.get_secops_cases.result.data.results }}
  lookup_results: ${{ ACTIONS.check_if_caseid_exists.result }}
