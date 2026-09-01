def generate_gap_explanation(
    skill_name: str, 
    alignment: str, 
    demand_priority: str, 
    demand_count: int, 
    coverage_status: str, 
    coverage_count: int,
    is_role_context: bool = False,
    role_name: str = None
) -> str:
    """Generates a deterministic explanation for a curriculum gap."""
    
    demand_desc = f"high ({demand_count} postings)" if demand_priority == 'HIGH' else \
                  f"moderate ({demand_count} postings)" if demand_priority == 'MEDIUM' else \
                  f"low ({demand_count} postings)"
                  
    if is_role_context and role_name:
        demand_desc = f"high ({demand_count} postings for {role_name})" if demand_priority == 'HIGH' else \
                      f"moderate ({demand_count} postings for {role_name})" if demand_priority == 'MEDIUM' else \
                      f"low ({demand_count} postings for {role_name})"
    
    coverage_desc = f"strong ({coverage_count} courses)" if coverage_status == 'HIGH' else \
                    f"limited ({coverage_count} courses)" if coverage_status == 'LOW' else \
                    "no evidence of"
    
    alignment_str = alignment.replace('_', ' ').lower()
    
    if alignment == 'ALIGNED':
        return f"{skill_name} is classified as {alignment_str} because observed industry demand is {demand_desc} and the indexed curriculum contains {coverage_desc} coverage."
    elif alignment == 'PARTIALLY_ALIGNED':
        return f"{skill_name} is classified as {alignment_str} because observed industry demand is {demand_desc} while the indexed curriculum only contains {coverage_desc} coverage."
    elif alignment in ('UNDER_COVERED', 'NOT_COVERED'):
        return f"{skill_name} is classified as {alignment_str} because observed industry demand is {demand_desc} while the indexed AICTE curriculum contains {coverage_desc} coverage."
    else:
        return f"{skill_name} has an {alignment_str} alignment due to {demand_desc} demand and {coverage_desc} coverage in the indexed curriculum."
