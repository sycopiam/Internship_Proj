import re
from typing import Dict, List, Tuple

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Network": [
        "wifi", "wi-fi", "internet", "network", "vpn", "connection",
        "router", "ethernet", "ip", "offline", "dns", "bandwidth", "signal", "connect"
    ],
    "Hardware": [
        "laptop", "desktop", "monitor", "screen", "keyboard", "mouse",
        "printer", "power", "battery", "hardware", "device", "ram",
        "disk", "cpu", "charger", "broken", "display", "headset", "cable", "pc"
    ],
    "Account": [
        "password", "login", "log in", "signin", "account", "unlock",
        "permission", "access", "reset", "locked", "2fa", "mfa",
        "auth", "credentials", "username", "forget", "forgot"
    ],
    "Email": [
        "outlook", "email", "e-mail", "inbox", "mail", "spam",
        "mailbox", "send", "receive", "attachment", "thunderbird", "gmail"
    ],
    "Software": [
        "app", "application", "software", "crash", "crashing", "freeze",
        "freezing", "slow", "install", "installation", "error", "bug",
        "excel", "word", "chrome", "browser", "update", "license", "launch"
    ]
}


def suggest_category(description: str) -> Dict[str, any]:
    """
    Intelligently analyzes ticket description text using rule-based keyword matching
    and returns suggested category, confidence, and matched keywords.
    """
    if not description or not description.strip():
        return {
            "suggested_category": "Other",
            "confidence": "None",
            "matched_keywords": []
        }

    # Normalize text to lowercase and split into words
    text_lower = description.lower()

    category_scores: Dict[str, List[str]] = {cat: [] for cat in CATEGORY_KEYWORDS}

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            # Match whole words or standard sub-phrases
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                category_scores[category].append(keyword)

    # Find category with highest number of keyword matches
    best_category = "Other"
    best_matches = []
    max_score = 0

    for category, matches in category_scores.items():
        if len(matches) > max_score:
            max_score = len(matches)
            best_category = category
            best_matches = matches

    if max_score >= 3:
        confidence = "High"
    elif max_score == 2:
        confidence = "Medium"
    elif max_score == 1:
        confidence = "Low"
    else:
        best_category = "Other"
        confidence = "None"
        best_matches = []

    return {
        "suggested_category": best_category,
        "confidence": confidence,
        "matched_keywords": best_matches
    }
