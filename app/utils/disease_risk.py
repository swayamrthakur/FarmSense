def calculate_disease_risk(crop: str, temperature: float, humidity: float, rainfall: float) -> dict:
    """
    Calculate disease risk based on weather conditions.
    Rules sourced from agricultural research on common Indian crops.
    """
    risk_rules = {
        "rice": {
            "blast": humidity > 85 and 20 < temperature < 30,
            "blight": humidity > 80 and temperature > 28
        },
        "wheat": {
            "rust": humidity > 70 and 15 < temperature < 25,
            "smut": humidity > 75 and temperature < 20
        },
        "maize": {
            "blight": humidity > 80 and temperature > 30,
            "rust": humidity > 75 and 20 < temperature < 30
        },
        "cotton": {
            "boll_rot": humidity > 85 and temperature > 30,
            "wilt": rainfall < 5 and temperature > 35
        },
        "mango": {
            "anthracnose": humidity > 90 and temperature > 25,
            "powdery_mildew": humidity < 70 and 15 < temperature < 25
        }
    }

    crop_lower = crop.lower()
    diseases = risk_rules.get(crop_lower, {})
    active_diseases = [disease for disease, is_risky in diseases.items() if is_risky]

    if not diseases:
        # Crop not in our rules yet — give a general weather-based score
        if humidity > 85 and temperature > 30:
            risk_level = "High"
            risk_score = 75
        elif humidity > 70 or temperature > 28:
            risk_level = "Medium"
            risk_score = 40
        else:
            risk_level = "Low"
            risk_score = 15
    else:
        risk_score = round(len(active_diseases) / len(diseases) * 100)
        if risk_score >= 60:
            risk_level = "High"
        elif risk_score >= 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "active_diseases": active_diseases,
        "total_rules_checked": len(diseases)
    }