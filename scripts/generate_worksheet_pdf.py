"""Script to generate a PDF worksheet for the Data-Dex Pokémon Lab."""

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
FONT_PATH = ASSETS_DIR / "pokemon_solid.ttf"
OUTPUT_PATH = ASSETS_DIR / "data_quests_worksheet.pdf"


class WorksheetPDF(FPDF):
    def header(self):
        # 1. Trainer Name & Date (Top Line)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(0, 0, 0)  # Black
        self.cell(
            0,
            10,
            "Trainer Name: __________________________",
            border=0,
            align="L",
        )
        self.set_text_color(0, 0, 0)
        self.cell(
            0,
            10,
            "Date: ____________________",
            border=0,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="R",
        )
        self.ln(2)

        # 2. Main Title (Pokémon Style)
        if FONT_PATH.exists():
            if "Pokémon" not in self.fonts:
                self.add_font("Pokémon", "", str(FONT_PATH))
            self.set_font("Pokémon", "", 24)
        else:
            self.set_font("Helvetica", "B", 20)

        title_text = "Data-Dex: Ultimate Stat Lab"
        self.set_text_color(59, 129, 196)  # Pokémon blue outline

        # Save coordinates to print the text multiple times for a stroke effect
        curr_x = self.get_x()
        curr_y = self.get_y()
        offset = 0.3  # Outline width

        # Print "Backing" in blue at offsets
        for dx in [-offset, 0, offset]:
            for dy in [-offset, 0, offset]:
                if dx == 0 and dy == 0:
                    continue
                self.set_xy(curr_x + dx, curr_y + dy)
                self.cell(0, 15, title_text, border=0, align="C")

        # Print "Foreground" in yellow
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
        self.ln(3)

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
        self.set_y(-15)
        # self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def level_header(self, title):
        self.ln(2)
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(59, 129, 196)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, f" {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.ln(3)

    def question(self, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(0, 0, 0)
        # Checkbox placeholder
        self.cell(6, 6, "", border=1)
        self.set_x(26)
        self.multi_cell(0, 6, text)
        self.ln(1)
        # Answer box
        self.set_x(26)
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(100, 100, 100)
        self.cell(
            0,
            8,
            "My Findings: __________________________________________________________________________",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.ln(3)


def generate_pdf():
    pdf = WorksheetPDF()
    pdf.set_margins(left=20, top=20, right=20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Introduction with styled link
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(50, 50, 50)

    url = "datadex.famruiz.com"
    pdf.write(6, "Welcome, Trainer! Use the Data-Dex application (")

    # Styled Link (Visual only, no functional hyperlink as per request)
    pdf.set_text_color(59, 129, 196)  # Pokémon blue
    pdf.set_font("Helvetica", "U", 12)
    pdf.write(6, url)

    # Reset and continue
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(50, 50, 50)
    pdf.write(
        6,
        ") to explore the world of Pokémon stats. Complete the quests below and document your discoveries.\n",
    )

    pdf.ln(2)

    # Level 1
    pdf.level_header("Level 1: Basic Navigation")
    pdf.question(
        "The Tiny Titan: Use the 'Exploring the World' scatter plot to find a Pokémon shorter than 1'8\" (0.5m) with an Attack over 100."
    )
    pdf.question(
        "Speed King: Check the Type Leaderboard. Which Type has the highest average Speed?"
    )

    # Level 2
    pdf.level_header("Level 2: Comparing Data")
    pdf.question(
        "The Shape of Stats: Both Mew and Deoxys (Normal Forme) have a total base stat (the sum of all 6 stats) of 600. Use the Radar Chart to compare them. How are they different?"
    )
    pdf.question(
        "Above the Bar: Pick your favorite Pokémon. Is its HP above or below the Global Average line found in the Type Leaderboard?"
    )
    pdf.question(
        'Trainer vs Pokémon: Add your height and weight to the "Trainer Comparison" section in the sidebar. How do you stack up against your favorite Pokémon?'
    )

    # Level 3
    pdf.level_header("Level 3: Finding Outliers")
    pdf.question(
        'Deceptive Appearances: Find a tiny (under 6" / 0.15m) but very heavy (over 2200 lbs / 999kg) Pokémon.'
    )
    pdf.question(
        "The Unbreakable Wall: Find a  Pokémon that has extremely high (200+) defense and special defense stats, but very low stats otherwise."
    )
    pdf.output(str(OUTPUT_PATH))
    print(f"PDF generated successfully at: {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_pdf()
