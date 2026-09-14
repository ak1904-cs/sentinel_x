"""
Threat Indicator Engine for Sentinel-X.
Detects threat language, radicalization signals, dedicated weapon/indicator keywords,
and planning patterns (Location + Time + Action).
"""
import re
from utils.text_utils import clean_text

# Lexicon Sets
THREAT_KEYWORDS = {
    "attack", "bomb", "kill", "target", "recruit", "explosive", "detonate",
    "hostage", "ambush", "terrorist", "ied", "behead", "hijack", "massacre",
    "gunfire", "sniper", "assassinate", "car bomb", "suicide vest", "dirty bomb",
    "strike", "slaughter", "execute", "destruction", "blast", "warfare", "urgent"
}

RADICALIZATION_KEYWORDS = {
    "recruitment", "propaganda", "extremist", "martyrdom", "jihad", "caliphate",
    "manifesto", "pledge", "radical", "indoctrinate", "holy war", "militant",
    "cell", "underground cell", "sleeper cell", "martyr"
}

# Dedicated Weapon & Tactical Indicator Lexicon (Refinement #1)
WEAPON_INDICATORS = {
    "ak-47", "ak47", "ar-15", "ar15", "pistol", "rifle", "shotgun", "firearm",
    "ammunition", "ammo", "semi-automatic", "automatic rifle", "submachine gun",
    "ied", "c4", "tnt", "fertilizer bomb", "pipe bomb", "suicide belt",
    "grenade", "semtex", "detonator", "dynamite", "shrapnel",
    "rpg", "rocket launcher", "missile", "mortar", "anthrax", "sarin", "ricin", "dirty bomb"
}

# Regex patterns for Planning Indicators (Time + Location + Target/Action)
TIME_PATTERNS = re.compile(
    r'\b(tomorrow|tonight|next week|at \d{1,2}(:\d{2})?\s*(am|pm)?|on (monday|tuesday|wednesday|thursday|friday|saturday|sunday)|midnight|dawn|\d{1,2}:\d{2})\b',
    re.IGNORECASE
)

LOCATION_PATTERNS = re.compile(
    r'\b(embassy|station|airport|bridge|square|plaza|stadium|mall|base|city hall|parliament|headquarters|downtown|center|church|mosque|synagogue|subway|terminal)\b',
    re.IGNORECASE
)

ACTION_PATTERNS = re.compile(
    r'\b(attack|strike|blow up|plant|bomb|infiltrate|ambush|execute|detonate|raid|gather|storm|meeting)\b',
    re.IGNORECASE
)

def analyze_threat_indicators(text: str) -> dict:
    """
    Analyze text for threat indicators, radicalization signals, weapons, and planning logic.
    Returns structured analysis payload.
    """
    if not isinstance(text, str) or not text.strip():
        return {
            "threat_score": 0.0,
            "threat_matches": [],
            "radicalization_matches": [],
            "weapon_matches": [],
            "planning_detected": False,
            "planning_details": {},
            "reasons": []
        }
    
    text_lower = text.lower()
    cleaned = clean_text(text)
    words = set(cleaned.split()).union(set(re.findall(r'\b\w+(?:-\w+)*\b', text_lower)))
    
    # Keyword & Substring matching for phrases and weapon terms
    threat_matches = list(words.intersection(THREAT_KEYWORDS))
    for phrase in ["car bomb", "suicide vest", "dirty bomb", "underground cell"]:
        if phrase in text_lower and phrase not in threat_matches:
            threat_matches.append(phrase)
            
    radicalization_matches = list(words.intersection(RADICALIZATION_KEYWORDS))
    for phrase in ["holy war", "sleeper cell"]:
        if phrase in text_lower and phrase not in radicalization_matches:
            radicalization_matches.append(phrase)
            
    weapon_matches = [w for w in WEAPON_INDICATORS if w in text_lower or w in words]
    
    # Planning detection (Location + Time + Action pattern matching)
    time_found = TIME_PATTERNS.findall(text)
    loc_found = LOCATION_PATTERNS.findall(text)
    action_found = ACTION_PATTERNS.findall(text)
    
    planning_detected = False
    planning_details = {}
    
    if (time_found or loc_found) and action_found:
        planning_detected = True
        planning_details = {
            "time_signals": [t[0] if isinstance(t, tuple) else t for t in time_found],
            "location_signals": loc_found,
            "action_signals": action_found
        }
    
    # Calculate Threat Score (0.0 to 1.0)
    score_components = []
    reasons = []
    
    if threat_matches:
        score_components.append(min(1.0, len(threat_matches) * 0.35))
        reasons.append(f"Detected threat keywords/phrases: {', '.join(threat_matches[:5])}")
        
    if radicalization_matches:
        score_components.append(min(1.0, len(radicalization_matches) * 0.35))
        reasons.append(f"Detected radicalization indicators: {', '.join(radicalization_matches[:5])}")
        
    if weapon_matches:
        score_components.append(min(1.0, len(weapon_matches) * 0.45))
        reasons.append(f"Detected tactical/weapon indicators: {', '.join(weapon_matches[:5])}")
        
    if planning_detected:
        score_components.append(0.85)
        reasons.append("Detected operational planning pattern (Time/Location + Action signals)")
        
    raw_threat_score = max(score_components) if score_components else 0.0
    threat_score = float(min(1.0, raw_threat_score))
    
    return {
        "threat_score": threat_score,
        "threat_matches": threat_matches,
        "radicalization_matches": radicalization_matches,
        "weapon_matches": weapon_matches,
        "planning_detected": planning_detected,
        "planning_details": planning_details,
        "reasons": reasons
    }
