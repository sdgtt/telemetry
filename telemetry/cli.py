"""Console script for telemetry."""
import sys
import click
import datetime
import telemetry


@click.group()
def cli():
    pass


@click.command()
@click.option("--server", default="picard", help="Address of Elasticsearch server")
@click.argument("in_args", nargs=-1)
def log_boot_logs(server, in_args):
    entry = {
        "boot_folder_name": "NA",
        "hdl_hash": "NA",
        "linux_hash": "NA",
        "hdl_branch": "NA",
        "linux_branch": "NA",
        "is_hdl_release": False,
        "is_linux_release": False,
        "uboot_reached": False,
        "linux_prompt_reached": False,
        "drivers_enumerated": False,
        "dmesg_warnings_found": False,
        "dmesg_errors_found": False,
        "jenkins_job_date": datetime.datetime.now(),
        "jenkins_build_number": 0,
        "jenkins_project_name": 0,
        "jenkins_agent": "NA",
    }
    if int(len(in_args) / 2) != len(in_args) / 2:
        click.echo(
            "ERROR: Number of inputs arguments must be even\n"
            + "       and in the form of: entry1<space>value1<space>entry2<space>value2"
        )
        sys.exit(1)
    for i in range(0, len(in_args), 2):
        if in_args[i] in entry:
            entry[in_args[i]] = in_args[i + 1]
        else:
            click.echo("ERROR: " + in_args[i] + " not a valid entry")
            sys.exit(1)
    tel = telemetry.ingest(server=server)
    tel.log_boot_tests(**entry)


@click.command()
def main(args=None):
    """Console script for telemetry."""
    click.echo("Replace this message by putting your code into " "telemetry.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


cli.add_command(log_boot_logs)
cli.add_command(main)

if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
