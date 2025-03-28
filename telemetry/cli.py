"""Console script for telemetry."""
import sys
import click
import datetime
import telemetry
import os

import telemetry.report
from telemetry.report.utility import map_th_to_bp, map_bp_to_th

def validate(field, value, schema):
    """Validate a field and value data type
    againts a given es schema
    """
    properties = schema["mappings"]["properties"]
    type_maps = {
        "keyword" : "str",
        "text" : "str",
        "boolean" : "bool",
        "integer" : "int",
        "date" : "datetime"
    }
    if not field in properties.keys():
        raise Exception(f"Schema validator: {field} not supported")

    # Validate data type
    expected_type = type_maps[properties[field]["type"]]
    actual_type = type(value).__name__

    try:
        if not actual_type == expected_type:
            raise Exception(f"Schema validator: {field} expects {expected_type} type, {actual_type} is given")
    except Exception:
        if expected_type == "bool":
            if value.lower() in ["false", "true"]:
                value = bool(value)
        if expected_type == "int":
            value = int(value)

@click.group()
def cli():
    pass


@click.command()
@click.option(
    "--tdir",
    default="/test/logs/unprocessed",
    help="Path to directory of unprocessed test logs",
)
@click.option("--server", default=None, help="Address of mongo server")
@click.option("--username", default=None, help="Username for mongo server")
@click.option("--password", default=None, help="Password for mongo server")
@click.option("--dbname", default=None, help="Target collection for mongo server")
@click.option("--board", default=None, help="Name of target board")
def prod_logs_upload(tdir, server, username, password, dbname, board):
    """Upload unprocessed test logs to mongo for synchrona."""
    sync = telemetry.prod.BoardLog(server, username, password, dbname, board)
    sync.default_unprocessed_log_dir = tdir
    sync.default_processed_log_dir = os.path.join(tdir, "processed")
    if not os.path.isdir(sync.default_processed_log_dir):
        os.mkdir(sync.default_processed_log_dir)
    sync() # go go


@click.command()
@click.option("--server", default="picard", help="Address of Elasticsearch server")
@click.option(
    "--filename",
    default="resource_utilization.csv",
    help="Full path to resource utilization csv file generated by HDL builds",
)
def log_hdl_resources_from_csv(server, filename):
    tel = telemetry.ingest(server=server)
    tel.log_hdl_resources_from_csv(filename)


@click.command()
@click.option("--server", default="picard", help="Address of Elasticsearch server")
@click.argument("in_args", nargs=-1)
def log_artifacts(server, in_args):
    entry = {
        "url": "NA",
        "server": "NA",
        "job": "NA",
        "job_no": 0,
        "job_date": None,
        "job_build_parameters": "NA",
        "file_name": "NA",
        "target_board": "NA",
        "artifact_info_type": "NA",
        "payload_raw": "NA",
        "payload_ts": "NA",
        "payload": "NA",
        "payload_param": "NA"
    }
    if len(in_args) == 0:
        click.echo("Must have non-zero arguments for database entry")
        sys.exit(1)
    if int(len(in_args) / 2) != len(in_args) / 2:
        click.echo(
            "ERROR: Number of inputs arguments must be even\n"
            + "       and in the form of: entry1<space>value1<space>entry2<space>value2"
        )
        sys.exit(1)
    for i in range(0, len(in_args), 2):
        if in_args[i] in entry:
            if in_args[i + 1].lower() == "true":
                entry[in_args[i]] = True
            elif in_args[i + 1].lower() == "false":
                entry[in_args[i]] = False
            else:
                entry[in_args[i]] = in_args[i + 1]
        else:
            click.echo("ERROR: " + in_args[i] + " not a valid entry")
            sys.exit(1)
    tel = telemetry.ingest(server=server)
    tel.log_artifacts(**entry)

@click.command()
@click.option("--jenkins-server", required=True, help="Address of Jenkins server")
@click.option("--jenkins-username", required=False, help="Username with access on the Jenkins server")
@click.option("--jenkins-password", required=False, help="Password for Jenkins username")
@click.option("--es-server", required=True, help="Address of Elasticsearch server")
@click.option("--job-name", default="HW_tests/HW_test_multiconfig", help="Name of Jenkins job")
@click.option("--job", multiple=True, help="Job(s)/build(s) to process")
def grab_and_log_artifacts(
        jenkins_server,
        jenkins_username,
        jenkins_password,
        es_server,
        job_name,
        job
    ):
    if not len(job) > 0:
        click.echo("Atleast 1 Job/Build (--job) is needed.")
        sys.exit(1)
    g = telemetry.gargantua(
        jenkins_server,
        jenkins_username,
        jenkins_password,
        es_server,
        job_name,
        job
    )
    g.log_artifacts()

@click.command()
@click.option("--server", default="picard", help="Address of Elasticsearch server")
@click.argument("in_args", nargs=-1)
def log_boot_logs(server, in_args):
    
    tel = telemetry.ingest(server=server)
    schema = tel.db.import_schema(tel._get_schema("boot_tests.json"))
    entry = dict()
    for k,v in schema["mappings"]["properties"].items():
        if k == "source_adjacency_matrix":
            continue
        if v["type"] in ["txt","keyword"]:
            entry.update({k:"NA"})
        elif v["type"] in ["integer"]:
            entry.update({k: 0})
        elif v["type"] in ["boolean"]:
            entry.update({k: False})
        elif k == "jenkins_job_date":
            entry.update({k:datetime.datetime.now()})
        else:
            entry.update({k: None})

    if len(in_args) == 0:
        click.echo("Must have non-zero arguments for database entry")
        sys.exit(1)
    if int(len(in_args) / 2) != len(in_args) / 2:
        click.echo(
            "ERROR: Number of inputs arguments must be even\n"
            + "       and in the form of: entry1<space>value1<space>entry2<space>value2"
        )
        sys.exit(1)

    for i in range(0, len(in_args), 2):
        if in_args[i] in entry:
            validate(in_args[i], in_args[i+1],schema)
            if in_args[i + 1].lower() == "true":
                entry[in_args[i]] = True
            elif in_args[i + 1].lower() == "false":
                entry[in_args[i]] = False
            else:
                entry[in_args[i]] = in_args[i + 1]
        else:
            click.echo("ERROR: " + in_args[i] + " not a valid entry")
            sys.exit(1)

    tel = telemetry.ingest(server=server)
    tel.log_boot_tests(**entry)

@click.command()
@click.option("--server", default="picard", help="Address of Elasticsearch server")
@click.option("--job_name", required=True, help="Jenkisn job name to fetch")
@click.option("--build_number", required=True, help="Build no to fetch")
@click.option("--board_name", default=None, help="Board to fetch, will select all if empty")
@click.option("--github_gist_url", default=None, help="Base URL to the gist repository")
@click.option("--github_gist_token", default=None, help="Token required for gist access")
def create_results_gist(server, job_name, build_number, board_name, github_gist_url, github_gist_token):
    tel = telemetry.searches(server=server)
    boot_test = tel.boot_tests(
        boot_folder_name=board_name,
        jenkins_project_name=job_name,
        jenkins_build_no=build_number
    )

    if len(boot_test.keys()) == 0:
        print(f"No boot test data found for {job_name} - {build_number}")
    # get artifacts
    artifacts_info_txt=tel.artifacts(
        target_board=None,
        job=job_name,
        job_no = build_number,
        artifact_info_type = "info_txt",
    )
    if len(artifacts_info_txt) == 0:
        print(f"No artifacts_info_txt found for {job_name} - {build_number}")

    built_projects = list()
    translated_built_projects = list()
    data = {}
    translated_data = {}
    for artifact in artifacts_info_txt:
        if artifact["payload"] == "Built projects":
            built_projects.append(artifact["payload_param"])

    # translate first to test harness board naming scheme
    for board in built_projects:
        translated = map_bp_to_th(board)
        if translated:
            if type(translated) == list:
                for variant in translated:
                    if variant not in translated_built_projects:
                        translated_built_projects.append(variant)
            else:
                translated_built_projects.append(translated)
        else:
            translated_built_projects.append(board)

    for board in translated_built_projects:
        if not board in boot_test.keys():
            data[board] = "NA"
        else:
            info = boot_test[board]
            artifacts = tel.artifacts(board, job_name, build_number)
            artifact_types = ["enumerated_devs", "missing_devs", "dmesg_err", "pytest_failure"]
            for artifactory_type in artifact_types:
                info[0].update({artifactory_type: []})
                for artifact in artifacts:
                    if artifact["artifact_info_type"] == artifactory_type:
                        info[0][artifactory_type].append(artifact["payload"])
            
            if artifacts_info_txt:
                info[0]["info_txt"] = dict()
                info[0]["info_txt"].update({"Built projects": list()})
                for artifact in artifacts_info_txt:
                    if artifact["payload"] == "Built projects":
                        info[0]["info_txt"]["Built projects"].append(artifact["payload_param"])
                        continue
                    info[0]["info_txt"].update({artifact["payload"]:artifact["payload_param"]})

            
            info[0]["variance_info"] = board.split("-v")[1] if len(board.split("-v")) == 2 else None
            data[board] = info[0]

    # translate back to boot partition naming scheme
    for bn, details in data.items():
        translated = map_th_to_bp(bn)
        if translated:
            board_name = translated
        else:
            board_name = bn
        if board_name in translated_data:
            if type(details) == dict and "variance_info" in details:
                board_name += f" ({details['variance_info']})"
        translated_data.update({board_name: details})

    m = telemetry.markdown.ResultsMarkdown(translated_data)
    m.generate_gist(github_gist_url, github_gist_token)
    
@click.command()
def main(args=None):
    """Console script for telemetry."""
    click.echo("Replace this message by putting your code into " "telemetry.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


cli.add_command(prod_logs_upload)
cli.add_command(log_boot_logs)
cli.add_command(log_hdl_resources_from_csv)
cli.add_command(log_artifacts)
cli.add_command(grab_and_log_artifacts)
cli.add_command(create_results_gist)
cli.add_command(main)

if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
