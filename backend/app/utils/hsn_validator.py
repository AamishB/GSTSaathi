"""
HSN (Harmonized System of Nomenclature) code validator.
Validates HSN code format and length based on turnover slab.
"""
from typing import Dict, Optional


def validate_hsn_format(hsn_code: str) -> tuple:
    """
    Validate HSN code format (4-8 digits).
    
    Args:
        hsn_code: HSN code string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not hsn_code:
        return True, ""  # HSN is optional in some cases
    
    hsn_code = str(hsn_code).strip()
    
    # Check if all characters are digits
    if not hsn_code.isdigit():
        return False, "HSN code must contain only digits"
    
    # Check length (4-8 digits)
    if len(hsn_code) < 4 or len(hsn_code) > 8:
        return False, f"HSN code must be 4-8 digits, got {len(hsn_code)}"
    
    return True, ""


def validate_hsn_for_turnover(hsn_code: Optional[str], turnover_slab: str) -> Dict:
    """
    Validate HSN code based on turnover slab requirements.
    
    Rules:
    - Turnover ≤ ₹1.5Cr: HSN optional
    - Turnover ₹1.5Cr - ₹5Cr: 4-digit HSN mandatory
    - Turnover > ₹5Cr: 6-digit HSN mandatory
    - Import/Export: 8-digit HSN mandatory
    
    Args:
        hsn_code: HSN code string (can be None)
        turnover_slab: One of 'below_1.5cr', '1.5cr_to_5cr', 'above_5cr'
        
    Returns:
        Dictionary with validation result and details
    """
    result = {
        "valid": False,
        "hsn_code": hsn_code,
        "errors": [],
        "required_length": None,
        "is_optional": False,
    }
    
    # Determine HSN requirements based on turnover slab
    if turnover_slab == "below_1.5cr":
        result["is_optional"] = True
        result["required_length"] = 4
    elif turnover_slab == "1.5cr_to_5cr":
        result["is_optional"] = False
        result["required_length"] = 4
    elif turnover_slab == "above_5cr":
        result["is_optional"] = False
        result["required_length"] = 6
    else:
        result["errors"].append(f"Invalid turnover slab: {turnover_slab}")
        return result
    
    # If HSN is optional and not provided, it's valid
    if result["is_optional"] and not hsn_code:
        result["valid"] = True
        return result
    
    # If HSN is mandatory and not provided, it's invalid
    if not result["is_optional"] and not hsn_code:
        result["errors"].append(f"HSN code is mandatory for turnover slab '{turnover_slab}'")
        return result
    
    # Validate HSN format
    is_valid_format, error_msg = validate_hsn_format(hsn_code)
    if not is_valid_format:
        result["errors"].append(error_msg)
        return result
    
    # Validate HSN length based on turnover
    hsn_length = len(hsn_code)
    if hsn_length < result["required_length"]:
        result["errors"].append(
            f"HSN code must be at least {result['required_length']} digits for turnover slab '{turnover_slab}', "
            f"got {hsn_length}"
        )
        return result
    
    result["valid"] = True
    return result


def get_hsn_chapter(hsn_code: str) -> Optional[str]:
    """
    Get the HSN chapter (first 2 digits) from HSN code.
    
    Args:
        hsn_code: HSN code string
        
    Returns:
        2-digit chapter code or None if invalid
    """
    if not hsn_code or len(hsn_code) < 2:
        return None
    
    if not hsn_code[:2].isdigit():
        return None
    
    return hsn_code[:2]


def get_hsn_description(hsn_code: str) -> str:
    """
    Get HSN description based on chapter.
    Note: This is a simplified version. Full implementation would need a complete HSN database.
    
    Args:
        hsn_code: HSN code string
        
    Returns:
        Chapter description or "Unknown"
    """
    chapter = get_hsn_chapter(hsn_code)
    
    hsn_chapters = {
        "01": "Live animals",
        "02": "Meat and edible meat offal",
        "03": "Fish, crustaceans, molluscs",
        "04": "Dairy produce, birds' eggs, natural honey",
        "05": "Animal products not elsewhere specified",
        "06": "Live trees and other plants",
        "07": "Edible vegetables and certain roots and tubers",
        "08": "Edible fruit and nuts",
        "09": "Coffee, tea, maté and spices",
        "10": "Cereals",
        "11": "Products of the milling industry",
        "12": "Oil seeds and oleaginous fruits",
        "13": "Lac, gums, resins and other vegetable saps",
        "14": "Vegetable plaiting materials",
        "15": "Animal or vegetable fats and oils",
        "16": "Preparations of meat, fish or crustaceans",
        "17": "Sugars and sugar confectionery",
        "18": "Cocoa and cocoa preparations",
        "19": "Preparations of cereals, flour, starch or milk",
        "20": "Preparations of vegetables, fruit, nuts",
        "21": "Miscellaneous edible preparations",
        "22": "Beverages, spirits and vinegar",
        "23": "Residues and waste from the food industries",
        "24": "Tobacco and manufactured tobacco substitutes",
        "25": "Salt, sulphur, earths and stone",
        "26": "Metallic ores, slag and ash",
        "27": "Mineral fuels, mineral oils and products",
        "28": "Inorganic chemicals",
        "29": "Organic chemicals",
        "30": "Pharmaceutical products",
        "31": "Fertilisers",
        "32": "Tanning or dyeing extracts",
        "33": "Essential oils and resinoids",
        "34": "Soap, organic surface-active agents",
        "35": "Albuminoidal substances, modified starches",
        "36": "Explosives, pyrotechnic products",
        "37": "Photographic or cinematographic goods",
        "38": "Miscellaneous chemical products",
        "39": "Plastics and articles thereof",
        "40": "Rubber and articles thereof",
        "41": "Raw hides and skins",
        "42": "Articles of leather",
        "43": "Furskins and artificial fur",
        "44": "Wood and articles of wood",
        "45": "Cork and articles of cork",
        "46": "Manufactures of straw, of esparto",
        "47": "Pulp of wood or other fibrous cellulosic material",
        "48": "Paper and paperboard",
        "49": "Printed books, newspapers, pictures",
        "50": "Silk",
        "51": "Wool, fine or coarse animal hair",
        "52": "Cotton",
        "53": "Other vegetable textile fibres",
        "54": "Man-made filaments",
        "55": "Man-made staple fibres",
        "56": "Wadding, felt and nonwovens",
        "57": "Carpets and other textile floor coverings",
        "58": "Special woven fabrics",
        "59": "Impregnated, coated, covered or laminated textile fabrics",
        "60": "Knitted or crocheted fabrics",
        "61": "Articles of apparel and clothing accessories, knitted",
        "62": "Articles of apparel and clothing accessories, not knitted",
        "63": "Other made up textile articles",
        "64": "Footwear, gaiters and the like",
        "65": "Headgear and parts thereof",
        "66": "Umbrellas, sun umbrellas, walking sticks",
        "67": "Prepared feathers and down",
        "68": "Articles of stone, plaster, cement, asbestos",
        "69": "Ceramic products",
        "70": "Glass and glassware",
        "71": "Natural or cultured pearls, precious or semi-precious stones",
        "72": "Iron and steel",
        "73": "Articles of iron or steel",
        "74": "Copper and articles thereof",
        "75": "Nickel and articles thereof",
        "76": "Aluminium and articles thereof",
        "77": "Magnesium, beryllium and articles thereof",
        "78": "Lead and articles thereof",
        "79": "Zinc and articles thereof",
        "80": "Tin and articles thereof",
        "81": "Other base metals, cermets",
        "82": "Tools, implements, cutlery, spoons and forks",
        "83": "Miscellaneous articles of base metal",
        "84": "Nuclear reactors, boilers, machinery and mechanical appliances",
        "85": "Electrical machinery and equipment",
        "86": "Railway or tramway locomotives, rolling-stock",
        "87": "Vehicles other than railway or tramway rolling-stock",
        "88": "Aircraft, spacecraft, and parts thereof",
        "89": "Ships, boats and floating structures",
        "90": "Optical, photographic, measuring, checking, precision, medical instruments",
        "91": "Clocks and watches and parts thereof",
        "92": "Musical instruments",
        "93": "Arms and ammunition",
        "94": "Furniture, bedding, mattresses",
        "95": "Toys, games and sports requisites",
        "96": "Miscellaneous manufactured articles",
        "97": "Works of art, collectors' pieces and antiques",
        "98": "Special classification provisions",
        "99": "Services",
    }
    
    return hsn_chapters.get(chapter, "Unknown")
