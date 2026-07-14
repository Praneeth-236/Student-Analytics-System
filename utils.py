import hashlib

def format_list(items):
    if not items:
        return "None"
    return ", ".join(items)


def risk_color(level):
    if level == "High":
        return "#d62828"
    if level == "Moderate":
        return "#f4a261"
    return "#2a9d8f"


def color_label(text, color):
    return f"<span style='color:{color}; font-weight:600'>{text}</span>"


def tags(items):
    if not items:
        return "<span style='color:#666'>None</span>"
    parts = []
    for item in items:
        parts.append(
            "<span style='display:inline-block; padding:2px 8px; margin:2px 4px; "
            "border-radius:12px; background:#f1f1f1; font-size:0.85rem'>"
            f"{item}</span>"
        )
    return " ".join(parts)


def hash_password(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_password(raw_password, expected_hash):
    return hash_password(raw_password) == expected_hash


def password_policy_ok(password, min_length, require_digit):
    if len(password) < min_length:
        return False
    if require_digit and not any(char.isdigit() for char in password):
        return False
    return True
