from datetime import datetime

import streamlit as st


def _semester_sort_key(value):
    if isinstance(value, int):
        return (0, value)
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            return (0, int(stripped))
    try:
        return (0, int(value))
    except (TypeError, ValueError):
        return (1, str(value))


def _load_css(path="styles.css"):
    try:
        with open(path, "r", encoding="utf-8") as file:
            st.markdown(f"<style>{file.read()}</style>", unsafe_allow_html=True)
    except OSError:
        st.warning("styles.css not found; using default styles.")


def _hero(subtitle):
    st.markdown(
        f"""
<div class="hero">
    <h1>PES Mentor-Based Student Intelligence System</h1>
    <p>{subtitle}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def _format_timestamp(value):
    if not value:
        return "-"
    try:
        parsed = datetime.fromisoformat(value)
        return parsed.astimezone().strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return value
