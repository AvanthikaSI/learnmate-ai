"""
exporter.py - Export utility for LearnMate AI learning sessions.

Supports exporting session notes and chat history to:
1. Markdown (.md)
2. Plain Text (.txt)
3. PDF (.pdf)
"""

import os
import re
from typing import List, Dict, Any
from fpdf import FPDF
from fpdf.enums import XPos, YPos


def sanitize_for_pdf(text: str) -> str:
    """
    Sanitizes Unicode characters and emojis for compatibility with
    standard FPDF Latin-1 core fonts, ensuring error-free PDF creation
    across Windows and Linux (Streamlit Cloud).
    """
    replacements = {
        "\u2014": "-",   # em-dash
        "\u2013": "-",   # en-dash
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u2022": "*",   # bullet
        "\u2026": "...", # ellipsis
        "\u2192": "->",  # right arrow
        "\u2190": "<-",  # left arrow
        "\u2265": ">=",  # greater than or equal
        "\u2264": "<=",  # less than or equal
        "\u2705": "[x]", # check mark
        "\u274c": "[ ]", # cross mark
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
        
    # Filter to characters encodable in latin-1, replacing unsupported symbols
    return text.encode("latin-1", "replace").decode("latin-1")


def export_to_markdown(session: Dict[str, Any], interactions: List[Dict[str, Any]]) -> str:
    """
    Converts a session and its interactions into clean Markdown format.
    """
    md = []
    md.append("# LearnMate AI - Learning Session Notes")
    md.append(f"**Topic:** {session.get('topic', 'General')}")
    md.append(f"**Title:** {session.get('title', 'Untitled Session')}")
    md.append(f"**Created:** {session.get('created_at', '')}")
    md.append(f"**Total Activities / Interactions:** {len(interactions)}")
    md.append("\n---\n")

    for idx, item in enumerate(interactions, 1):
        md.append(f"## {idx}. {item.get('activity', 'Interaction')}")
        md.append(f"*Timestamp: {item.get('created_at', '')}*\n")
        md.append("### Prompt / Question")
        md.append(f"> {item.get('user_prompt', '').strip()}\n")
        md.append("### LearnMate Response")
        md.append(f"{item.get('ai_response', '').strip()}\n")
        md.append("\n---\n")

    md.append("\n*Generated with LearnMate AI.*")
    return "\n".join(md)


def export_to_txt(session: Dict[str, Any], interactions: List[Dict[str, Any]]) -> str:
    """
    Converts a session and its interactions into structured plain text.
    """
    lines = []
    lines.append("=" * 70)
    lines.append("LEARNMATE AI - LEARNING SESSION NOTES")
    lines.append("=" * 70)
    lines.append(f"Topic: {session.get('topic', 'General')}")
    lines.append(f"Title: {session.get('title', 'Untitled Session')}")
    lines.append(f"Date:  {session.get('created_at', '')}")
    lines.append(f"Total Interactions: {len(interactions)}")
    lines.append("=" * 70)
    lines.append("")

    for idx, item in enumerate(interactions, 1):
        lines.append(f"[{idx}] ACTIVITY: {item.get('activity', 'Interaction').upper()}")
        lines.append(f"Time: {item.get('created_at', '')}")
        lines.append("-" * 50)
        lines.append("PROMPT / QUESTION:")
        lines.append(item.get('user_prompt', '').strip())
        lines.append("")
        lines.append("LEARNMATE RESPONSE:")
        lines.append(item.get('ai_response', '').strip())
        lines.append("-" * 50)
        lines.append("")

    lines.append("=" * 70)
    lines.append("End of Session Notes - LearnMate AI")
    lines.append("=" * 70)
    return "\n".join(lines)


class PDFReport(FPDF):
    """Custom PDF class with header and footer."""
    def header(self):
        self.set_font("helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "LearnMate AI - Study Notes", border=0, align="R")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        page_str = f"Page {self.page_no()} / {{nb}}"
        self.cell(0, 10, page_str, border=0, align="C")


def export_to_pdf(session: Dict[str, Any], interactions: List[Dict[str, Any]]) -> bytes:
    """
    Generates a formatted PDF document containing all session notes.
    Returns binary PDF bytes.
    """
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title Banner
    pdf.set_fill_color(30, 41, 59)  # Slate dark blue
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 18)
    pdf.cell(0, 14, sanitize_for_pdf("  LearnMate AI - Study Session"), fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    # Session Meta Table
    pdf.set_text_color(40, 40, 40)
    pdf.set_font("helvetica", "B", 12)
    topic_str = sanitize_for_pdf(f"Topic: {session.get('topic', 'General')}")
    pdf.cell(0, 7, topic_str, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("helvetica", "", 10)
    title_str = sanitize_for_pdf(f"Title: {session.get('title', 'Untitled')}")
    pdf.cell(0, 6, title_str, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    date_str = sanitize_for_pdf(f"Created: {session.get('created_at', '')} | Total Activities: {len(interactions)}")
    pdf.cell(0, 6, date_str, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)

    # Horizontal divider line
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # Interactions / Activities
    for idx, item in enumerate(interactions, 1):
        activity_title = sanitize_for_pdf(f"{idx}. Activity: {item.get('activity', 'Interaction')}")
        
        # Activity Header
        pdf.set_fill_color(240, 244, 248)
        pdf.set_text_color(15, 23, 42)
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 8, f"  {activity_title}", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

        # Question / Prompt Section
        prompt_text = sanitize_for_pdf(item.get("user_prompt", "").strip())
        if prompt_text:
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(70, 70, 70)
            pdf.cell(0, 6, "Prompt / Question:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("helvetica", "I", 10)
            pdf.set_text_color(90, 90, 90)
            pdf.multi_cell(0, 5, prompt_text)
            pdf.ln(3)

        # AI Response Section
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(16, 100, 160)
        pdf.cell(0, 6, "LearnMate Explanation:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(30, 30, 30)

        response_text = sanitize_for_pdf(item.get("ai_response", "").strip())
        # Clean formatting symbols for clean PDF rendering
        clean_text = re.sub(r"\*\*(.*?)\*\*", r"\1", response_text)
        clean_text = re.sub(r"\*(.*?)\*", r"\1", clean_text)
        clean_text = re.sub(r"`(.*?)`", r"\1", clean_text)
        clean_text = re.sub(r"#{1,6}\s*", "", clean_text)

        pdf.multi_cell(0, 5.5, clean_text)
        pdf.ln(6)

        # Divider between activities
        pdf.set_draw_color(225, 230, 235)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

    return bytes(pdf.output())
