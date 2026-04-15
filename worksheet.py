from flask import send_file
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
WORKSHEET_PATH = PROJECT_ROOT / "assets" / "data_quests_worksheet.pdf"
CHEATSHEET_PATH = PROJECT_ROOT / "assets" / "cheatsheet.pdf"
GUIDE_PATH = PROJECT_ROOT / "assets" / "DataDex_User_Guide.pdf"


def register_worksheet_routes(server):
    """Register routes to serve PDF lab materials."""

    @server.route("/worksheet")
    def download_worksheet():
        if WORKSHEET_PATH.exists():
            return send_file(
                WORKSHEET_PATH,
                as_attachment=True,
                download_name="Data-Dex_Stat_Lab_Worksheet.pdf",
                mimetype="application/pdf",
            )
        else:
            return "Worksheet file not found.", 404

    @server.route("/cheat-sheet")
    def download_cheatsheet():
        if CHEATSHEET_PATH.exists():
            return send_file(
                CHEATSHEET_PATH,
                as_attachment=True,
                download_name="Data-Dex_Instructor_Cheat_Sheet.pdf",
                mimetype="application/pdf",
            )
        else:
            return "Cheat sheet file not found.", 404

    @server.route("/user-guide")
    def download_user_guide():
        if GUIDE_PATH.exists():
            return send_file(
                GUIDE_PATH,
                as_attachment=True,
                download_name="Data-Dex_User_Guide.pdf",
                mimetype="application/pdf",
            )
        else:
            return "User guide file not found.", 404
