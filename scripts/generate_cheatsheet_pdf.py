"""Script to generate a PDF Cheat Sheet for the Data-Dex Pokémon Lab."""

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
FONT_PATH = ASSETS_DIR / "pokemon_solid.ttf"
OUTPUT_PATH = ASSETS_DIR / "cheatsheet.pdf"


class CheatSheetPDF(FPDF):
    def header(self):
        # 1. Main Title (Pokémon Style)
        if FONT_PATH.exists():
            if "Pokémon" not in self.fonts:
                self.add_font("Pokémon", "", str(FONT_PATH))
            self.set_font("Pokémon", "", 24)
        else:
            self.set_font("Helvetica", "B", 20)

        title_text = "Data-Dex: Ultimate Stat Lab"
        self.set_text_color(59, 129, 196)  # Pokémon blue outline

        # Save coordinates for stroke effect
        curr_x = self.get_x()
        curr_y = self.get_y()
        offset = 0.3

        for dx in [-offset, 0, offset]:
            for dy in [-offset, 0, offset]:
                if dx == 0 and dy == 0:
                    continue
                self.set_xy(curr_x + dx, curr_y + dy)
                self.cell(0, 15, title_text, border=0, align="C")

        self.set_xy(curr_x, curr_y)
        self.set_text_color(255, 203, 5)  # Pokémon yellow
        self.cell(
            0,
            15,
            title_text,
            border=0,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="C",
        )

        self.set_font("Helvetica", "B", 14)
        self.set_text_color(50, 50, 50)
        self.cell(
            0,
            8,
            "-- Instructor Cheat Sheet --",
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.ln(5)

    def footer(self):
        self.set_y(-25)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        copyright_text = (
            "© 2026 Pokémon. © 1995-2026 Nintendo/Creatures Inc./GAME FREAK inc. "
            "Pokémon names are trademarks of Nintendo.\n"
            "This project is for educational purposes and not affiliated with Nintendo.\n"
            "Data-Dex: datadex.famruiz.com"
        )
        self.multi_cell(0, 5, copyright_text, align="C")

    def level_header(self, title):
        self.ln(2)
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(59, 129, 196)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, f" {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.ln(3)

    def cheat_entry(self, question, answer, tip=None):
        # Question Title
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(0, 0, 0)
        self.write(6, f"Q: {question}\n")

        # Answer
        # self.set_x(26)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(40, 100, 40)  # Dark Green for answers
        self.write(6, "A: ")
        self.set_font("Helvetica", "", 10)
        self.write(6, f"{answer}\n")

        # Teacher Tip
        if tip:
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(150, 100, 0)  # Gold/Orange for tips
            self.write(5, "Tip: ")
            self.set_font("Helvetica", "I", 9)
            self.write(5, f"{tip}\n")

        self.ln(4)


def generate_pdf():
    pdf = CheatSheetPDF()
    pdf.set_margins(left=20, top=20, right=20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Introduction
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(
        0,
        5,
        "Use this guide to help students and highlight interesting facts during the Data-Dex Stat Lab session.\n",
    )
    pdf.ln(2)

    # Level 1
    pdf.level_header("Level 1: Basic Navigation")
    pdf.cheat_entry(
        "The Tiny Titan (Height < 1'8\", Attack > 100)",
        "Kartana. It is only 1'0\" (0.3m) tall but has a massive 181 Attack!",
        "Kartana is made of paper but is sharper than a samurai sword.",
    )
    pdf.cheat_entry(
        "Speed King (Fastest Type Average)",
        "Electric.",
        "Many kids guess Fire or Flying, but Electric consistently has the highest average speed.",
    )

    # Level 2
    pdf.level_header("Level 2: Comparing Data")
    pdf.cheat_entry(
        "The Shape of Stats (Mew vs. Deoxys Normal Forme)",
        "Mew is a perfect hexagon (100 in every stat). Deoxys is a 'Glass Cannon' with huge spikes in Attack and Speed, but almost no Defense.",
        "Even though they have the same 'Total' power (600), they play completely differently!",
    )
    pdf.cheat_entry(
        "Above the Bar (HP vs. Global Average)",
        "The Global Average HP is approximately 70.",
        "Even 'strong' Pokémon like Gengar actually have below-average HP.",
    )
    pdf.cheat_entry(
        "Trainer vs Pokémon",
        "Subjective comparison.",
        "Most kids will be taller than a Pikachu but much lighter than a Charizard!",
    )

    # Level 3
    pdf.level_header("Level 3: Finding Outliers")
    pdf.cheat_entry(
        "Deceptive Appearances (Tiny but ultra-heavy)",
        "Cosmoem. It is only 4 inches (0.1m) tall but weighs 2,204 lbs (999.9kg)!",
        "That's as heavy as a car, but it can fit in your hand. It's the densest Pokemon in the universe.",
    )
    pdf.cheat_entry(
        "The Unbreakable Wall (Highest Defense + Special Defense)",
        "Shuckle. It has 230 Defense and 230 Special Defense, but only 10 Attack.",
        "Shuckle is the ultimate tank--it can't hurt you, but you can't hurt it either!",
    )

    pdf.output(str(OUTPUT_PATH))
    print(f"Cheat Sheet PDF generated successfully at: {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_pdf()
