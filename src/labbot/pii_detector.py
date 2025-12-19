"""PII detection module for identifying sensitive personal information.

This module detects personally identifiable information (PII) patterns
in text to prevent sensitive data from reaching the Claude API.
"""

import re
from typing import Any


def detect_pii(input_text: str) -> list[str]:
    """Detect personally identifiable information in text.

    Scans input text for common PII patterns including:
    - Social Security Numbers (SSN)
    - Phone numbers
    - Email addresses
    - Dates of birth
    - Personal names (common name field patterns)

    Args:
        input_text: The text to scan for PII patterns.

    Returns:
        List of PII types detected (e.g., ["ssn", "email"]).
        Empty list if no PII found. Each type appears at most once.

    Example:
        >>> detect_pii("SSN: 123-45-6789")
        ["ssn"]
        >>> detect_pii("Hemoglobin: 14.5 g/dL")
        []
        >>> detect_pii("patient_name: John Smith, email: john@example.com")
        ["name", "email"]
    """
    detected_types: list[str] = []

    # Detect SSN: format XXX-XX-XXXX or XXXXXXXXX
    # Must have proper boundaries to avoid false positives with lab values
    if re.search(r'\b\d{3}-\d{2}-\d{4}\b', input_text):
        detected_types.append("ssn")
    elif re.search(r'\b\d{9}\b', input_text):
        detected_types.append("ssn")

    # Detect phone numbers: XXX-XXX-XXXX or XXX.XXX.XXXX or XXX XXX XXXX
    # or (XXX) XXX-XXXX format
    if re.search(r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b', input_text):
        detected_types.append("phone")
    elif re.search(r'\(\d{3}\)\s*\d{3}[-.\s]\d{4}\b', input_text):
        detected_types.append("phone")

    # Detect email addresses
    if re.search(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        input_text,
    ):
        detected_types.append("email")

    # Detect dates of birth in various formats
    # MM/DD/YYYY, M/D/YYYY, MM-DD-YYYY, DD/MM/YYYY variations
    if re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', input_text):
        detected_types.append("dob")

    # Detect common name field patterns (case-insensitive)
    # Look for patterns like "patient_name:", "full_name:", "name:" followed by text
    if _contains_name_field(input_text):
        detected_types.append("name")

    return detected_types


def _contains_name_field(input_text: str) -> bool:
    """Check if text contains common name field patterns.

    Args:
        input_text: The text to search for name fields.

    Returns:
        True if common name field patterns are found, False otherwise.
    """
    name_patterns = [
        r'(?i)patient_?name\s*[=:]\s*["\']?[A-Z][a-z]+',
        r'(?i)full_?name\s*[=:]\s*["\']?[A-Z][a-z]+',
        r'(?i)name\s*[=:]\s*["\']?[A-Z][a-z]+\s+[A-Z][a-z]+',
        r'(?i)first_?name\s*[=:]\s*["\']?[A-Z][a-z]+',
        r'(?i)last_?name\s*[=:]\s*["\']?[A-Z][a-z]+',
        r'(?i)surname\s*[=:]\s*["\']?[A-Z][a-z]+',
    ]

    for pattern in name_patterns:
        if re.search(pattern, input_text):
            return True

    return False


def detect_pii_in_dict(data: dict[str, Any]) -> list[str]:
    """Detect PII in dictionary keys and values.

    Recursively scans all string values and dictionary keys in a dictionary
    for PII patterns. Handles nested dictionaries and lists.

    Args:
        data: Dictionary to scan for PII.

    Returns:
        List of unique PII types detected across all keys and values.

    Example:
        >>> data = {
        ...     "lab_values": [
        ...         {"name": "Hemoglobin", "value": 14.5},
        ...         {"name": "SSN", "value": "123-45-6789"}
        ...     ]
        ... }
        >>> detect_pii_in_dict(data)
        ["ssn"]
    """
    detected_types: list[str] = []
    all_pii = _extract_pii_recursive(data, check_keys=True)

    # Return unique PII types, preserving order
    seen: set[str] = set()
    for pii_type in all_pii:
        if pii_type not in seen:
            detected_types.append(pii_type)
            seen.add(pii_type)

    return detected_types


def _extract_pii_recursive(data: Any, check_keys: bool = False) -> list[str]:
    """Recursively extract PII from nested data structures.

    Args:
        data: Data structure to scan (dict, list, str, or other).
        check_keys: If True, check dictionary keys for name field patterns.

    Returns:
        List of all PII types found in the structure.
    """
    pii_list: list[str] = []

    if isinstance(data, dict):
        for key, value in data.items():
            # Check key for name field patterns
            if check_keys and isinstance(key, str) and _is_name_field_key(key):
                pii_list.append("name")
            pii_list.extend(_extract_pii_recursive(value, check_keys=check_keys))
    elif isinstance(data, list):
        for item in data:
            pii_list.extend(_extract_pii_recursive(item, check_keys=check_keys))
    elif isinstance(data, str):
        pii_list.extend(detect_pii(data))

    return pii_list


def _is_name_field_key(key: str) -> bool:
    """Check if a dictionary key is a name field pattern.

    Args:
        key: The dictionary key to check.

    Returns:
        True if key matches common name field patterns, False otherwise.
    """
    name_key_patterns = [
        r'(?i)^patient_?name',
        r'(?i)^full_?name',
        r'(?i)^first_?name',
        r'(?i)^last_?name',
        r'(?i)^surname',
    ]

    for pattern in name_key_patterns:
        if re.search(pattern, key):
            return True

    return False
