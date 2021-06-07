from flask import Flask, render_template
from pages import allboards as ab
from models import boards as b
from models import boot_tests as bt
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
    #retrieve boards from elastic server
    boards_ref = b.Boards().boards
    headers = ["Board", "Status"]
    boards = [
        {
            "Online": board.is_online,
            "Board": board.board_name,
            "Status": board.boot_test_result,
            "Jenkins Project Name": board.jenkins_project_name,
            "HDL Commit": board.hdl_hash,
            "Linux Commit": board.linux_hash
        }
        for board in boards_ref
    ]
    return render_template("allboards.html", headers=headers, boards=boards)


@app.route("/board/<board_name>")
def board(board_name):
    boot_tests = bt.BoardBootTests(board_name).boot_tests
    boards = [
        {
            "Tested branch": test.source_adjacency_matrix,
            "u-boot Reached": test.uboot_reached,
            "Linux Booted": test.linux_prompt_reached,
            "Linux Tests": {"pass": 10, "fail": 0},
            "pyadi Tests": {"pass": 10, "fail": 0},
            "Status": test.boot_test_result,
            "HDL Commit": test.hdl_hash,
            "Linux Commit": test.linux_hash,
            "Jenkins Project Name": test.jenkins_project_name,
            "Jenkins Build Number": test.jenkins_build_number,
            "Jenkins Job Date:": test.jenkins_job_date
        }
        for test in boot_tests
    ]
    return render_template("board.html", board_name=board_name, boards=boards)


@app.route("/kibana/<visualization>")
def kibana(visualization):
    return render_template("kibana.html", visualization=visualization)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
