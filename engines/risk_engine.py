"""
Configurable Explainable Risk Engine for Sentinel-X.
Combines threat indicators, context ML classification, spaCy entity signals, and operational planning logic.
Weights are configurable in config/settings.py.
"""
from config.settings import RISK_WEIGHTS, RISK_THRESHOLDS
from engines.threat_engine import analyze_threat_indicators
from engines.nlp_engine import get_nlp_engine
from engines.entity_engine import get_entity_engine

def calculate_explainable_risk(text: str) -> dict:
    """
    Calculate an explainable risk score (0 - 100) and risk category for input text.
    
    Formula:
    Risk Score = (
        Threat Indicators * W_threat +
        Context Classification * W_context +
        Entity Signals * W_entity +
        Planning Indicators * W_planning
    ) * 100
    
    Returns structured dict with overall score, category, breakdown, and human-readable reasons.
    """
    if not isinstance(text, str) or not text.strip():
        return {
            "risk_score": 0.0,
            "risk_category": "Low",
            "components": {},
            "reasons": ["No text payload provided for risk analysis."],
            "threat_details": {},
            "entity_details": {}
        }
    
    # 1. Threat & Planning Indicators Analysis
    threat_analysis = analyze_threat_indicators(text)
    threat_score = threat_analysis["threat_score"]
    planning_score = 0.9 if threat_analysis["planning_detected"] else 0.0
    
    # 2. Context Classification Probability (Hate / Threat ML model signal)
    nlp_engine = get_nlp_engine()
    context_prob = nlp_engine.predict_hate_probability(text)
    
    # 3. Entity Signal Analysis
    entity_engine = get_entity_engine()
    entity_analysis = entity_engine.extract_entities(text)
    entity_score = entity_analysis["entity_signal_score"]
    
    # 4. Configurable Engineering Weighted Sum (Refinement #2)
    w_threat = RISK_WEIGHTS.get('THREAT_INDICATORS', 0.30)
    w_context = RISK_WEIGHTS.get('CONTEXT_CLASSIFICATION', 0.30)
    w_entity = RISK_WEIGHTS.get('ENTITY_SIGNALS', 0.20)
    w_planning = RISK_WEIGHTS.get('PLANNING_INDICATORS', 0.20)
    
    total_weight = w_threat + w_context + w_entity + w_planning
    if total_weight <= 0:
        total_weight = 1.0
        
    raw_weighted_score = (
        (threat_score * w_threat) +
        (context_prob * w_context) +
        (entity_score * w_entity) +
        (planning_score * w_planning)
    ) / total_weight
    
    # Scale to 0-100
    risk_score = round(float(raw_weighted_score * 100), 1)
    
    # Categorization
    high_threshold = RISK_THRESHOLDS.get('HIGH', 70.0)
    mod_threshold = RISK_THRESHOLDS.get('MODERATE', 40.0)
    
    if risk_score >= high_threshold:
        risk_category = "High"
    elif risk_score >= mod_threshold:
        risk_category = "Moderate"
    else:
        risk_category = "Low"
        
    # Build Transparent Reasons Breakdown
    reasons = []
    if threat_analysis["threat_matches"]:
        reasons.append(f"Threat keywords detected: {', '.join(threat_analysis['threat_matches'][:4])}")
    if threat_analysis["radicalization_matches"]:
        reasons.append(f"Radicalization indicators detected: {', '.join(threat_analysis['radicalization_matches'][:4])}")
    if threat_analysis["weapon_matches"]:
        reasons.append(f"Tactical/weapon indicators detected: {', '.join(threat_analysis['weapon_matches'][:4])}")
    if threat_analysis["planning_detected"]:
        reasons.append("Operational planning pattern identified (Time/Location + Action signals)")
    if context_prob >= 0.5:
        reasons.append(f"High ML toxicity/hate signal probability ({context_prob:.2f})")
    if entity_analysis["high_risk_entities"]:
        reasons.append(f"High-risk entities referenced: {', '.join(entity_analysis['high_risk_entities'])}")
    if not reasons:
        reasons.append("No significant threat indicators, high-risk entities, or planning patterns detected.")
        
    return {
        "risk_score": risk_score,
        "risk_category": risk_category,
        "components": {
            "threat_indicator_score": round(threat_score * 100, 1),
            "context_classifier_score": round(context_prob * 100, 1),
            "entity_signal_score": round(entity_score * 100, 1),
            "planning_score": round(planning_score * 100, 1)
        },
        "reasons": reasons,
        "threat_details": threat_analysis,
        "entity_details": entity_analysis
    }
