"""Script to generate a PDF worksheet for the Data-Dex Pokémon Lab."""

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
FONT_PATH = ASSETS_DIR / "Pokémon_solid.ttf"
OUTPUT_PATH = PROJECT_ROOT / "data_quests_worksheet.pdf"


class WorksheetPDF(FPDF):
    def header(self):
        # Add logo/title styling
        if FONT_PATH.exists():
            if "Pokémon" not in self.fonts:
                self.add_font("Pokémon", "", str(FONT_PATH))
            self.set_font("Pokémon", "", 24)
        else:
            self.set_font("Helvetica", "B", 20)

        self.set_text_color(255, 203, 5)  # Pokémon yellow
        self.cell(
            0,
            15,
            "DATA-DEX: ULTIMATE STAT LAB",
            border=0,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="C",
        )

        self.set_font("Helvetica", "B", 16)
        self.set_text_color(59, 129, 196)  # Pokémon blue
        self.cell(
            0,
            10,
            "Researcher Worksheet",
            border=0,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="C",
        )
        self.ln(10)

    def footer(self):
        self.set_y(-25)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        copyright_text = (
            "(c) 2026 Pokémon. (c) 1995-2026 Nintendo/Creatures Inc./GAME FREAK inc. "
            "Pokémon names are trademarks of Nintendo.\n"
            "This project is for educational purposes and not affiliated with Nintendo."
        )
        self.multi_cell(0, 5, copyright_text, align="C")
        self.set_y(-15)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def level_header(self, title):
        self.ln(5)
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(59, 129, 196)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, f" {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.ln(5)

    def question(self, text):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(0, 0, 0)
        # Checkbox placeholder
        self.cell(6, 6, "", border=1)
        self.set_x(16)
        self.multi_cell(0, 6, text)
        self.ln(2)
        # Answer box
        self.set_x(16)
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(100, 100, 100)
        self.cell(
            0,
            8,
            "My Findings: __________________________________________________________________________",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.ln(5)


def generate_pdf():
    pdf = WorksheetPDF()
    pdf.set_auto_page_break(auto=True, margin=30)
    pdf.add_page()

    # Introduction
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(50, 50, 50)
    intro_txt = (
        "Welcome, Researcher! Use the Data-Dex application to explore the hidden stats of Pokémon. "
        "Complete the quests below and document your discoveries."
    )
    pdf.multi_cell(0, 6, intro_txt)
    pdf.ln(5)

    # Level 1
    pdf.level_header("Level 1: Basic Navigation")
    pdf.question(
        "The Tiny Titan: Find a Pokémon shorter than 1'8\" (0.5m) with an Attack over 100."
    )
    pdf.question(
        "Speed King: Check the Type Leaderboard. Which Type has the highest average Speed?"
    )

    # Level 2
    pdf.level_header("Level 2: Comparing Data")
    pdf.question(
        "The Shape-Shifter: Compare a 'Heavyweight' (like Snorlax) and a 'Speedster' (like Pikachu). Describe their Radar Chart shapes."
    )
    pdf.question(
        "Above the Bar: Pick your favorite Pokémon. Is its HP above or below the Global Average line (around 70)?"
    )

    # Level 3
    pdf.level_header("Level 3: Finding Outliers")
    pdf.question(
        "The Rule Breaker: Find a very heavy Pokémon (over 440 lbs / 200kg) that is tiny (under 1'8\" / 0.5m)."
    )
    pdf.question(
        "The Specialist: Find a Pokémon with one HUGE stat spike but very weak stats elsewhere. What is the specialist's best stat?"
    )

    pdf.output(str(OUTPUT_PATH))
    print(f"PDF generated successfully at: {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_pdf()
