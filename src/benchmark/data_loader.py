"""
Data loader for test cases from JSON.

Provides utilities to load, validate, and manage test cases from JSON files.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


def load_test_cases(json_file: str) -> List[Dict[str, Any]]:
    """
    Load test cases from JSON file.
    
    Args:
        json_file: Path to JSON file
    
    Returns:
        List of test case dictionaries
    
    Raises:
        FileNotFoundError: If JSON file not found
        json.JSONDecodeError: If JSON is invalid
    """
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"JSON file not found: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if "test_cases" not in data:
        raise ValueError("JSON must contain 'test_cases' key")
    
    return data["test_cases"]


def validate_test_case(case: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate a test case structure.
    
    Args:
        case: Test case dictionary
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    required = ["id", "name", "type", "equations", "variables", "parameters", 
                "parameter_ranges", "expected_solutions"]
    for field in required:
        if field not in case:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return False, errors
    
    # Validate equations
    if not isinstance(case["equations"], list) or len(case["equations"]) == 0:
        errors.append("'equations' must be non-empty list")
    
    # Validate variables
    if not isinstance(case["variables"], list) or len(case["variables"]) == 0:
        errors.append("'variables' must be non-empty list")
    
    # Validate parameters
    if not isinstance(case["parameters"], list):
        errors.append("'parameters' must be list (can be empty)")
    
    # Validate parameter_ranges
    if not isinstance(case["parameter_ranges"], dict):
        errors.append("'parameter_ranges' must be dict")
    
    # All parameters should have ranges
    for param in case["parameters"]:
        if param not in case["parameter_ranges"]:
            errors.append(f"Parameter '{param}' missing in parameter_ranges")
        else:
            rng = case["parameter_ranges"][param]
            if not isinstance(rng, list) or len(rng) != 3:
                errors.append(f"Range for '{param}' must be [min, max, num_points]")
    
    # Validate expected_solutions
    if not isinstance(case["expected_solutions"], list) or len(case["expected_solutions"]) == 0:
        errors.append("'expected_solutions' must be non-empty list")
    
    return len(errors) == 0, errors


def get_test_case_by_id(test_cases: List[Dict[str, Any]], case_id: int) -> Optional[Dict[str, Any]]:
    """
    Get test case by ID.
    
    Args:
        test_cases: List of test cases
        case_id: Numeric ID of case (1-indexed)
    
    Returns:
        Test case dict or None if not found
    """
    for case in test_cases:
        if case.get("id") == case_id:
            return case
    return None


def get_test_case_by_name(test_cases: List[Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
    """
    Get test case by name.
    
    Args:
        test_cases: List of test cases
        name: Name of case
    
    Returns:
        Test case dict or None if not found
    """
    for case in test_cases:
        if case.get("name") == name:
            return case
    return None


def filter_by_id_range(test_cases: List[Dict[str, Any]], min_id: int, max_id: int) -> List[Dict[str, Any]]:
    """
    Filter test cases by ID range.
    
    Args:
        test_cases: List of test cases
        min_id: Minimum ID (inclusive)
        max_id: Maximum ID (inclusive)
    
    Returns:
        Filtered list
    """
    return [c for c in test_cases if min_id <= c.get("id", 0) <= max_id]


def export_to_runner_format(case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert test case to format compatible with runner.py.
    
    Args:
        case: Test case from JSON
    
    Returns:
        Dict compatible with runner.run_single_case()
    """
    # Extract variables for results
    runner_case = {
        "id": case["id"],
        "name": case["name"],
        "equation": " AND ".join(case["equations"]),  # Placeholder, will be parsed separately
        "equations": case["equations"],  # For parse_system
        "variables": case["variables"],
        "parameters": case["parameters"],
        "parameter_ranges": {p: case["parameter_ranges"][p][:2] + (10,) 
                            for p in case["parameters"]},  # Convert to (min, max, num_points)
        "expected_roots": [],  # Will be filled by runner with expected_solutions
        "type": case.get("type"),
    }
    
    # Extract root expressions from expected_solutions
    # Build dict of expected roots per variable combination
    expected_roots_set = []
    for sol in case["expected_solutions"]:
        root_expr = ", ".join([f"{var}={sol.get(var, '?')}" 
                              for var in case["variables"]])
        expected_roots_set.append(root_expr)
    
    runner_case["expected_roots"] = expected_roots_set
    
    return runner_case


def get_statistics(test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get statistics about test cases.
    
    Args:
        test_cases: List of test cases
    
    Returns:
        Dict with statistics
    """
    total_equations = 0
    total_parameters = 0
    total_equations_per_case = []
    total_parameters_per_case = []
    
    for case in test_cases:
        total_equations += len(case.get("equations", []))
        total_parameters += len(case.get("parameters", []))
        total_equations_per_case.append(len(case.get("equations", [])))
        total_parameters_per_case.append(len(case.get("parameters", [])))
    
    return {
        "total_cases": len(test_cases),
        "total_equations": total_equations,
        "total_parameters": total_parameters,
        "avg_equations_per_case": total_equations / len(test_cases) if test_cases else 0,
        "avg_parameters_per_case": total_parameters / len(test_cases) if test_cases else 0,
        "total_equations": total_equations,
        "avg_equations_per_case": total_equations / len(test_cases) if test_cases else 0,
        "total_parameters": total_parameters,
        "avg_parameters_per_case": total_parameters / len(test_cases) if test_cases else 0,
    }


if __name__ == "__main__":
    # Example usage
    json_file = os.path.join(os.path.dirname(__file__), "data", "test_cases_sistemas.json")
    
    print("Loading test cases...")
    cases = load_test_cases(json_file)
    
    print(f"Loaded {len(cases)} cases\n")
    
    # Print statistics
    stats = get_statistics(cases)
    print("Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\nCases by category:")
    for cat in ["linear", "quadratic", "cubic", "special"]:
        filtered = filter_by_category(cases, cat)
        print(f"  {cat}: {len(filtered)}")
    
    print("\nCases by difficulty:")
    for diff in ["easy", "medium", "hard"]:
        filtered = filter_by_difficulty(cases, diff)
        print(f"  {diff}: {len(filtered)}")
    
    print("\nFirst 3 cases:")
    for i, case in enumerate(cases[:3], 1):
        print(f"  {i}. [{case['id']}] {case['name']} ({case['category']}/{case['difficulty']})")
        print(f"     Equations: {case['equations']}")
        print(f"     Variables: {case['variables']}")
        print(f"     Parameters: {case['parameters']}")
    
    print(f"Loaded {len(cases)} cases\n")
    
    # Print statistics
    stats = get_statistics(cases)
    print("Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\nCases by category:")
    for cat in ["linear", "quadratic", "cubic", "special"]:
        filtered = filter_by_category(cases, cat)
        print(f"  {cat}: {len(filtered)}")
    
    print("\nCases by difficulty:")
    for diff in ["easy", "medium", "hard"]:
        filtered = filter_by_difficulty(cases, diff)
        print(f"  {diff}: {len(filtered)}")
    
    print("\nFirst 3 cases:")
    for i, case in enumerate(cases[:3], 1):
        print(f"  {i}. [{case['id']}] {case['name']} ({case['category']}/{case['difficulty']})")
        print(f"     Equations: {case['equations']}")
        print(f"     Variables: {case['variables']}")
        print(f"     Parameters: {case['parameters']}")
