"""Generate the Data-Dex: Ultimate Stat Lab — User Guide PDF.

Single-column layout only — no manual XY column tricks to avoid overlap.
"""

from pathlib import Path
from PIL import Image as PILImage
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# ── Paths ─────────────────────────────────────────────────────────────────────
SS = Path("docs/guide_screenshots")
OUT_DIR = Path("assets")
OUT_DIR.mkdir(exist_ok=True)
OUT_PATH = OUT_DIR / "DataDex_User_Guide.pdf"

FULL_APP_IMG = SS / "full_app.png"
FILTERS_IMG = SS / "filters_panel.png"
DETAIL_IMG = SS / "detail_card.png"
RADAR_IMG = SS / "radar_card.png"
TRAINER_IMG = SS / "trainer_card.png"
LEADERBOARD_IMG = SS / "leaderboard_card.png"
WORLD_IMG = SS / "world_card.png"

ARIAL = "/Library/Fonts/Arial Unicode.ttf"
POKE = "assets/pokemon_solid.ttf"

# ── Colour palette ────────────────────────────────────────────────────────────
BG = (255, 255, 255)
ACCENT = (41, 121, 220)
AMBER = (190, 130, 0)
ORANGE = (200, 90, 5)
TEXT = (20, 20, 35)
DIM = (110, 115, 135)
GREEN = (25, 150, 60)
PURPLE = (100, 30, 180)
RULE = (210, 215, 225)

# A4 with 18 mm margins
L = 18  # left margin
R = 18  # right margin
CW = 210 - L - R  # content width = 174 mm


class Doc(FPDF):
    # ── helpers ────────────────────────────────────────────────────────────────
    def tc(self, triple):
        self.set_text_color(*triple)

    def fc(self, triple):
        self.set_fill_color(*triple)

    # ── chrome ────────────────────────────────────────────────────────────────
    def header(self):
        self.fc(BG)
        self.rect(0, 0, self.w, self.h, "F")

    def footer(self):
        self.set_y(-13)
        self.fc(RULE)
        self.rect(L, self.get_y(), CW, 0.25, "F")
        self.ln(1.5)
        self.tc(DIM)
        self.set_font("AU", "", 7.5)
        self.cell(
            0,
            5,
            f"Data-Dex: Ultimate Stat Lab — User Guide   |   Page {self.page_no()}",
            align="C",
        )

    # ── headings ──────────────────────────────────────────────────────────────
    def h2(self, num, title, color=ACCENT):
        self.ln(4)
        self.fc(color)
        self.rect(L, self.get_y(), 3, 7, "F")
        self.set_x(L + 6)
        self.tc(color)
        self.set_font("AU", "B", 13)
        self.cell(0, 7, f"{num}  {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    # ── body text ──────────────────────────────────────────────────────────────
    def body(self, txt, color=TEXT, size=9.5):
        self.tc(color)
        self.set_font("AU", "", size)
        self.multi_cell(0, 5.5, txt)
        self.ln(1)

    # ── bullet row ─────────────────────────────────────────────────────────────
    def bullet(self, label, desc, dot_color=ACCENT):
        y = self.get_y()
        self.fc(dot_color)
        self.rect(L, y + 1.5, 2.5, 3.5, "F")
        self.set_x(L + 5)
        self.tc(TEXT)
        self.set_font("AU", "B", 9)
        self.cell(0, 5.5, label, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(L + 5)
        self.tc(DIM)
        self.set_font("AU", "", 9)
        self.multi_cell(CW - 5, 5, desc)
        self.ln(1)

    # ── callout box ────────────────────────────────────────────────────────────
    def callout(self, txt, color=ACCENT):
        x, y = L, self.get_y()
        r, g, b = color
        self.fc(color)
        self.rect(x, y, 3, 12, "F")
        self.set_fill_color(min(255, r + 200), min(255, g + 200), min(255, b + 200))
        self.rect(x + 3, y, CW - 3, 12, "F")
        self.set_xy(x + 7, y + 2)
        self.tc(color)
        self.set_font("AU", "B", 9)
        self.multi_cell(CW - 10, 5, txt)
        self.set_y(max(self.get_y(), y + 12) + 2)

    # ── image helper ───────────────────────────────────────────────────────────
    def img(
        self,
        path: Path,
        caption: str,
        w: float | None = None,
        max_h: float | None = None,
    ):
        """Insert an image (max width = CW, optional max height). Triggers page break if tight."""
        if not (path and path.exists()):
            return
        iw = min(w, CW) if w else CW
        # If max_h is given, compute the width that keeps height <= max_h
        if max_h:
            with PILImage.open(path) as pil:
                px_w, px_h = pil.size
            aspect = px_h / px_w  # height-to-width ratio
            max_w_for_h = max_h / aspect  # width that gives exactly max_h
            iw = min(iw, max_w_for_h)
        # If less than 35 mm remain, break first
        if self.h - self.get_y() - self.b_margin < 35:
            self.add_page()
        x_off = L + (CW - iw) / 2  # centre the image
        self.image(str(path), x=x_off, w=iw)
        self.tc(DIM)
        self.set_font("AU", "I", 7.5)
        self.cell(CW, 4, caption, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

    # ── horizontal rule ────────────────────────────────────────────────────────
    def rule(self):
        self.ln(2)
        self.fc(RULE)
        self.rect(L, self.get_y(), CW, 0.25, "F")
        self.ln(3)


# ════════════════════════════════════════════════════════════════════════════════
def build():
    pdf = Doc("P", "mm", "A4")
    pdf.set_margins(L, 18, R)
    pdf.set_auto_page_break(True, margin=18)

    for style in ("", "B", "I", "BI"):
        pdf.add_font("AU", style, fname=ARIAL)
    pdf.add_font("PK", fname=POKE)

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 1 — COVER
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.set_y(72)
    pdf.set_font("PK", size=50)

    # Outlined title: blue shadow offsets then yellow on top
    ty = pdf.get_y()
    off = 0.6
    pdf.set_text_color(10, 80, 200)
    for dx, dy in [
        (-off, 0),
        (off, 0),
        (0, -off),
        (0, off),
        (-off, -off),
        (off, -off),
        (-off, off),
        (off, off),
    ]:
        pdf.set_xy(L + dx, ty + dy)
        pdf.cell(CW, 22, "DATA-DEX", align="C")
    pdf.set_text_color(255, 200, 0)
    pdf.set_xy(L, ty)
    pdf.cell(0, 22, "DATA-DEX", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("AU", "B", 16)
    pdf.tc(ACCENT)
    pdf.cell(0, 9, "Ultimate Stat Lab", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)
    pdf.set_font("AU", "", 11)
    pdf.tc(DIM)
    pdf.cell(0, 7, "User Guide", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)
    pdf.fc(ACCENT)
    pdf.rect((pdf.w - 50) / 2, pdf.get_y(), 50, 0.8, "F")
    pdf.ln(8)
    pdf.set_font("AU", "I", 10)
    pdf.tc(DIM)
    pdf.multi_cell(
        0,
        6,
        "Explore, compare, and discover Pokémon data\nthrough interactive charts and filters.",
        align="C",
    )

    # QR code + URL
    pdf.ln(10)
    qr_path = "qr-code.png"
    qr_size = 40  # mm
    qr_x = (pdf.w - qr_size) / 2
    pdf.image(qr_path, x=qr_x, w=qr_size)
    pdf.ln(3)
    pdf.set_font("AU", "B", 10)
    pdf.tc(ACCENT)
    pdf.cell(
        0,
        6,
        "https://datadex.famruiz.com/",
        align="C",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 2 — GETTING STARTED + FILTERS
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()

    pdf.h2("1", "Getting Started")
    pdf.body(
        "Data-Dex is an interactive browser-based dashboard designed to introduce simple "
        "data science concepts to kids using a subject they already love — Pokémon. "
        "A filter sidebar runs down the left side; the main area holds six analysis cards. "
        "Every filter change instantly refreshes all cards — no submit button required."
    )
    pdf.body(
        "The app comes with three companion PDFs to support classroom use:\n"
        "  \u2022 Student Worksheet \u2014 a guided activity sheet with questions for students to fill in "
        "while exploring the app. A download button is also available at the bottom of the filters sidebar.\n"
        "    datadex.famruiz.com/worksheet\n"
        "  \u2022 Instructor Cheat Sheet \u2014 suggested answers and teaching notes for educators.\n"
        "    datadex.famruiz.com/cheat-sheet\n"
        "  \u2022 This User Guide \u2014 a full walkthrough of every feature in the app.\n"
        "    datadex.famruiz.com/user-guide",
        color=DIM,
    )
    pdf.img(
        FULL_APP_IMG,
        "Full app overview — filters sidebar (left) + analysis cards (main area)",
        w=CW,
        max_h=80,
    )

    pdf.rule()

    pdf.h2("2", "Filters Sidebar", color=AMBER)
    pdf.body(
        "The sidebar controls which Pokémon appear across every card simultaneously. "
        "It has three collapsible sections:",
        color=DIM,
    )

    sections = [
        (
            "Basic Filters",
            AMBER,
            [
                (
                    "Regions",
                    "Restrict to one or more regional Pokédexes (Kanto, Johto, Hoenn…).",
                ),
                ("Types", "Show only Pokémon whose primary or secondary type matches."),
                ("Sort By", "Order the selector list by Pokédex # or alphabetically."),
            ],
        ),
        (
            "Stat Ranges",
            GREEN,
            [
                (
                    "HP / Atk / Def / Sp.Atk / Sp.Def / Speed",
                    "Each stat has a 0–255 range slider. Only Pokémon within all ranges appear.",
                ),
            ],
        ),
        (
            "Special Variants",
            PURPLE,
            [
                (
                    "Mega / Regional / G-Max",
                    "Toggle ON/OFF to include or exclude these forms.",
                ),
                (
                    "Legendaries / Mythicals / Ultra Beasts",
                    "Toggle ON/OFF for each category.",
                ),
                (
                    "Final Evolutions Only",
                    "When ON, hides unevolved and mid-stage Pokémon.",
                ),
                (
                    "Reset All Filters",
                    "Restores every filter and toggle to its default state.",
                ),
            ],
        ),
    ]
    for section_title, color, items in sections:
        pdf.ln(1)
        pdf.tc(color)
        pdf.set_font("AU", "B", 10)
        pdf.cell(0, 6, section_title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        for label, desc in items:
            pdf.bullet(label, desc, dot_color=color)
        pdf.ln(1)

    pdf.img(
        FILTERS_IMG,
        "Expanded filters sidebar showing all three sections",
        w=55,
        max_h=100,
    )
    pdf.callout(
        "One filter change instantly updates the Detail Card selector, Type Leaderboard, "
        "and World Exploration scatter plot. The Face-Off Radar is unaffected — "
        "Pokémon already added to it stay on the chart regardless of filters.",
        color=AMBER,
    )

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 3 — DETAIL CARD + RADAR
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()

    pdf.h2("3", "Pokémon Detail Card", color=GREEN)
    pdf.body(
        "The Detail Card sits in the upper-left of the main area. "
        "Use it to look up any Pokémon and add them to the Face-Off Radar.",
        color=DIM,
    )
    for label, desc in [
        ("Pokémon Selector", "Search and pick any Pokémon from the filtered list."),
        ("Sprite / Shiny", "Official artwork. Toggle Shiny for alternate colours."),
        ("Type Badges", "Shows primary and secondary type(s)."),
        ("Stat Bars", "HP, Atk, Def, Sp.Atk, Sp.Def, Speed with colour coding."),
        ("Play Cry", "Speaker icon plays the Pokémon's in-game sound."),
        (
            "Add to Comparison",
            "Adds the current Pokémon to the Face-Off Radar (max 6).",
        ),
        ("Evolution Lineage", "Tap a sprite in the chain to jump to that Pokémon."),
    ]:
        pdf.bullet(label, desc, dot_color=GREEN)
    pdf.ln(2)
    pdf.img(DETAIL_IMG, "Pokémon Detail Card — Bulbasaur selected", w=80, max_h=90)

    pdf.rule()

    pdf.h2("4", "Face-Off Radar", color=AMBER)
    pdf.body(
        "A spider/radar chart that overlays base stats for up to 6 Pokémon at once. "
        "Select a Pokémon in the Detail Card, click Add to Comparison, and repeat. "
        "Hover any spoke tip to see the exact stat value. "
        "Scroll to zoom in; use the Reset Zoom button to return to default. "
        "Click Clear Comparison to remove all Pokémon from the chart.",
        color=DIM,
    )
    pdf.img(
        RADAR_IMG,
        "Face-Off Radar — add Pokémon via the Detail Card to populate this chart",
        max_h=80,
    )
    pdf.callout(
        "Note: sidebar filters affect which Pokémon you can add via the selector, "
        "but any Pokémon already on the radar will stay there even if a filter would exclude them. "
        "Use Clear Comparison to remove them manually.",
        color=AMBER,
    )

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 4 — TRAINER + LEADERBOARD
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()

    pdf.h2("5", "Trainer Comparison", color=ORANGE)
    pdf.body(
        "Enter your height (ft) and weight (lbs) to see how you physically compare "
        "with the currently selected Pokémon. Results update automatically as you type.",
        color=DIM,
    )
    for label, desc in [
        ("Your Height (ft)", "Valid range 2–7 ft. Auto-updates after a short pause."),
        (
            "Your Weight (lbs)",
            "Valid range 10–500 lbs. Auto-updates after a short pause.",
        ),
        (
            "Height result",
            "States who is taller and the ratio (e.g. 'Charizard is taller — 1.2×').",
        ),
        (
            "Weight result",
            "States who is heavier and the ratio (e.g. 'You are heavier — 1.6×').",
        ),
    ]:
        pdf.bullet(label, desc, dot_color=ORANGE)
    pdf.ln(2)
    pdf.img(
        TRAINER_IMG,
        "Trainer Comparison — height and weight inputs with live comparison results",
        max_h=70,
    )

    pdf.rule()

    pdf.h2("6", "Type Leaderboard", color=PURPLE)
    pdf.body(
        "Horizontal bar chart ranking all Pokémon types by average base stat. "
        "Use the dropdown to switch between HP, Attack, Defense, Sp. Atk, Sp. Def, or Speed. "
        "Hover a bar for the exact average. Sidebar filters restrict the Pokémon pool — "
        "try selecting a single region to see how types rank within one generation.",
        color=DIM,
    )
    pdf.img(
        LEADERBOARD_IMG,
        "Type Leaderboard — ranked by average Attack stat across all Pokémon",
        max_h=80,
    )

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 5 — WORLD EXPLORATION
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()

    pdf.h2("7", "Exploring the World", color=ACCENT)
    pdf.body(
        "An open-ended scatter plot where you choose any two axes. "
        "Both the horizontal (X) and vertical (Y) axes can be set independently "
        "to any of the six base stats, Height, or Weight. "
        "Each dot represents a single Pokémon, coloured by its primary type. "
        "Hover a dot to see its name and exact values. "
        "Scroll to zoom, drag to pan, and use the Reset Zoom button to restore the default view. "
        "Sidebar filters instantly narrow the dataset.",
        color=DIM,
    )
    pdf.img(
        WORLD_IMG,
        "Exploring the World — Weight (X) vs Speed (Y) reveals outliers like Celesteela and Shuckle",
        max_h=90,
    )

    pdf.callout(
        "Try Height vs Weight to spot the heaviest Pokémon, "
        "or Speed vs HP to find fast, bulky Pokémon like Regieleki.",
        color=ACCENT,
    )

    pdf.ln(6)
    pdf.rule()
    pdf.ln(1)
    pdf.set_font("AU", "I", 8)
    pdf.tc(DIM)
    pdf.multi_cell(
        0,
        5,
        "Pokémon and all related names are trademarks of Nintendo/Creatures Inc./GAME FREAK inc. "
        "Data & sprites courtesy of PokéAPI (pokeapi.co). For educational use.",
        align="C",
    )

    pdf.output(str(OUT_PATH))
    print(f"✓ Saved: {OUT_PATH.resolve()}")


if __name__ == "__main__":
    build()
