"""
SafeBite — Allergy Detection Engine


"""

from typing import List, Tuple


# Keyword map: allergy name → list of ingredient keywords to search for
ALLERGY_KEYWORDS: dict[str, List[str]] = {
    "peanuts":    ["peanut", "groundnut", "arachis"],
    "dairy":      ["milk", "dairy", "lactose", "whey", "casein", "butter", "cream", "cheese", "yogurt"],
    "gluten":     ["wheat", "gluten", "barley", "rye", "spelt", "semolina", "flour"],
    "seafood":    ["fish", "shrimp", "prawn", "shellfish", "crab", "lobster", "oyster", "squid", "clam", "mussel", "anchovy", "salmon", "tuna", "cod", "halibut"],
    "tree nuts":  ["almond", "cashew", "walnut", "pecan", "pistachio", "hazelnut", "macadamia", "brazil nut", "pine nut"],
    "eggs":       ["egg", "albumin", "ovalbumin", "mayonnaise"],
    "soy":        ["soy", "soya", "tofu", "edamame", "miso", "tempeh"],
    "sesame":     ["sesame", "tahini", "til"],
    "mustard":    ["mustard"],
    "celery":     ["celery", "celeriac"],
    "lupin":      ["lupin", "lupine"],
    "molluscs":   ["mollusc", "mollusk", "squid", "octopus", "snail"],
    "sulphites":  ["sulphite", "sulfite", "sulphur dioxide", "so2"],
}


def _keywords_for(allergy_name: str) -> List[str]:
    key = allergy_name.strip().lower()
    # exact lookup
    if key in ALLERGY_KEYWORDS:
        return ALLERGY_KEYWORDS[key]
    # partial match
    for k, v in ALLERGY_KEYWORDS.items():
        if k in key or key in k:
            return v
    # fallback: use the name itself
    return [key]


def analyze_product(
    ingredients: str,
    user_allergies: List[str],
    severity_level: str | None = None,
) -> Tuple[str, str | None, List[str]]:
    """
    Returns (result, danger_info, allergens_found)
    result = "SAFE" | "NOT_SAFE"
    """
    if not ingredients:
        return ("SAFE", None, [])

    ingredients_lower = ingredients.lower()
    found: List[str] = []

    for allergy_name in user_allergies:
        keywords = _keywords_for(allergy_name)
        for kw in keywords:
            if kw in ingredients_lower:
                found.append(allergy_name.title())
                break

    if found:
        severity_tag = f" [{severity_level.upper()} risk]" if severity_level else ""
        danger_info = (
            f"Contains: {', '.join(found)}{severity_tag}. "
            f"This product is NOT safe for your allergy profile."
        )
        return ("NOT_SAFE", danger_info, found)

    return ("SAFE", None, [])
