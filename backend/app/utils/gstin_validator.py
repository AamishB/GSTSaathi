"""
GSTIN (Goods and Services Tax Identification Number) validator.
Implements format validation and Luhn mod 36 checksum verification.
"""
import re
from typing import Dict, Tuple


# Valid state codes for GSTIN (01-38)
VALID_STATE_CODES = {
    '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
    '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
    '21', '22', '23', '24', '25', '26', '27', '28', '29', '30',
    '31', '32', '33', '34', '35', '36', '37', '38'
}

# PAN format regex: 5 alpha, 4 numeric, 1 alpha
PAN_PATTERN = re.compile(r'^[A-Z]{5}\d{4}[A-Z]$')


def validate_gstin_format(gstin: str) -> Tuple[bool, str]:
    """
    Validate GSTIN format without checksum.
    
    Args:
        gstin: GSTIN string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not gstin:
        return False, "GSTIN is required"
    
    gstin = gstin.upper().strip()
    
    # Check length
    if len(gstin) != 15:
        return False, f"GSTIN must be exactly 15 characters, got {len(gstin)}"
    
    # Check first 2 characters are digits (state code)
    if not gstin[:2].isdigit():
        return False, "First 2 characters must be digits (state code)"
    
    # Validate state code
    if gstin[:2] not in VALID_STATE_CODES:
        return False, f"Invalid state code: {gstin[:2]}"
    
    # Check next 10 characters match PAN format
    pan_part = gstin[2:12]
    if not PAN_PATTERN.match(pan_part):
        return False, f"Invalid PAN format in GSTIN: {pan_part}"
    
    # Check 13th character is alphanumeric (entity number)
    if not gstin[12].isalnum():
        return False, "13th character must be alphanumeric"
    
    # Check 14th character is 'Z'
    if gstin[13] != 'Z':
        return False, f"14th character must be 'Z', got '{gstin[13]}'"
    
    # Check 15th character is alphanumeric (check digit)
    if not gstin[14].isalnum():
        return False, "15th character must be alphanumeric"
    
    return True, ""


def luhn_mod36_checksum(gstin: str) -> bool:
    """
    Verify GSTIN checksum using Luhn mod 36 algorithm.
    
    The checksum is calculated on the first 14 characters,
    and the result should match the 15th character.
    
    Args:
        gstin: 15-character GSTIN string
        
    Returns:
        True if checksum is valid, False otherwise
    """
    if len(gstin) != 15:
        return False
    
    gstin = gstin.upper().strip()
    
    # Mapping for mod 36: 0-9, A-Z
    char_to_value = {}
    for i in range(10):
        char_to_value[str(i)] = i
    for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        char_to_value[c] = 10 + i
    
    value_to_char = {v: k for k, v in char_to_value.items()}
    
    # Calculate checksum
    total = 0
    for i, char in enumerate(gstin[:14]):
        if char not in char_to_value:
            return False
        value = char_to_value[char]
        # Multiply by 2 if position is even (0-indexed)
        if i % 2 == 0:
            value *= 2
            # If result > 35, add digits (same as subtracting 35 for mod 36)
            if value > 35:
                value = (value % 36) + 1
        total = (total + value) % 36
    
    # Calculate check digit
    check_digit_value = (36 - total) % 36
    expected_check_digit = value_to_char[check_digit_value]
    
    return gstin[14] == expected_check_digit


def validate_gstin(gstin: str) -> Dict:
    """
    Complete GSTIN validation including format and checksum.
    
    Args:
        gstin: GSTIN string to validate
        
    Returns:
        Dictionary with validation result and details
    """
    result = {
        "valid": False,
        "gstin": gstin.upper().strip() if gstin else "",
        "errors": [],
        "state_code": None,
        "pan": None,
    }
    
    if not gstin:
        result["errors"].append("GSTIN is required")
        return result
    
    gstin = gstin.upper().strip()
    result["gstin"] = gstin
    
    # Format validation
    is_valid_format, error_msg = validate_gstin_format(gstin)
    if not is_valid_format:
        result["errors"].append(error_msg)
        return result
    
    # Extract components
    result["state_code"] = gstin[:2]
    result["pan"] = gstin[2:12]
    
    # Checksum validation
    if not luhn_mod36_checksum(gstin):
        result["errors"].append("Invalid GSTIN checksum")
        return result
    
    result["valid"] = True
    return result


def is_valid_gstin(gstin: str) -> bool:
    """
    Quick boolean check for GSTIN validity.
    
    Args:
        gstin: GSTIN string to validate
        
    Returns:
        True if valid, False otherwise
    """
    result = validate_gstin(gstin)
    return result["valid"]
