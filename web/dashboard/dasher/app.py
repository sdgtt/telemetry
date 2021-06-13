from flask import Flask, render_template
from pages import allboards as ab
# from junit2htmlreport import parser

app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template("index.html")


# @app.route("/report")
# def report():
#     ref = "pages/zynq_adrv9361_z7035_bob_reports.xml"
#     report = parser.Junit(ref)
#     return report.html()


@app.route("/boards")
def allboards():
    boards_ref = ab.get_board_list()
    headers = ["Board", "Status"]
    boards = [
        {
            "Online": "zynqmp" in board,
            "Board": board,
            "Status": "Pass",
            "HDL Commit": "791c6250 (5/6/2021)",
            "Linux Commit": "791caa50 (5/8/2021)",
        }
        for board in boards_ref
    ]
    return render_template("allboards.html", headers=headers, boards=boards)


@app.route("/board/<board_name>")
def board(board_name):
    boards_ref = ab.get_board_list()
    boards = [
        {
            "u-boot Reached": "True",
            "Linux Booted": "True",
            "Linux Tests": {"pass": 10, "fail": 0},
            "pyadi Tests": {"pass": 10, "fail": 0},
            "Status": "Pass",
            "HDL Commit": "791c6250 (5/6/2021)",
            "Linux Commit": "791caa50 (5/8/2021)",
            "Jenkins Job": "123",
        }
        for board in boards_ref
    ]
    return render_template("board.html", board_name=board_name, boards=boards)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
