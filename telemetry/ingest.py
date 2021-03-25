import telemetry
import datetime
import os
import csv


class ingest:
    use_test_index = False

    def __init__(self, mode="elastic", server="alpine"):
        if mode == "elastic":
            self.db = telemetry.elastic(server=server)

    def _get_schema(self, name):
        loc = os.path.dirname(__file__)
        return os.path.join(loc, "resources", name)

    def _translate_hdl_resource_fields(self, fieldss):
        out = []
        for field in fieldss:
            fields = field.replace("(%)", "_percent")
            fields = fields.replace("(#)", "_count")
            fields = fields.replace("/", "_")
            fields = fields.replace(" ", "_")
            fields = fields.replace("(Avg)", "avg")
            fields = fields.replace(">", "gt")
            fields = fields.replace("-", "_")
            fields = fields.replace("+", "_")
            fields = fields.replace(".", "p")
            fields = fields.replace("*", "")
            fields = fields.replace("(Cell)", "_cell")
            fields = fields.replace("(Pblock)", "_pblock")
            fields = fields.replace("__", "_")
            # Dupe so if long spaces show up they get squashed
            fields = fields.replace("__", "_")
            fields = fields.replace("__", "_")
            fields = fields.replace("__", "_")
            out.append(fields)

        # Check
        s = self.db.import_schema(self._get_schema("hdl_resources.json"))
        for k in s["mappings"]["properties"]:
            if k not in out:
                raise Exception("Cannot find field {}".format(k))

    def log_boot_tests(
        self,
        boot_folder_name,
        hdl_hash,
        linux_hash,
        boot_partition_hash,
        hdl_branch,
        linux_branch,
        boot_partition_branch,
        is_hdl_release,
        is_linux_release,
        is_boot_partition_release,
        uboot_reached,
        linux_prompt_reached,
        drivers_enumerated,
        dmesg_warnings_found,
        dmesg_errors_found,
        jenkins_job_date,
        jenkins_build_number,
        jenkins_project_name,
        jenkins_agent,
    ):
        """ Upload boot test results to elasticsearch """
        # Build will produce the following:
        #   hdl commit hash
        #   linux commit hash
        #   hdl release flag
        #   hdl master flag
        #   linux release flag
        #   linux master flag
        #
        #   fully booted status
        #   uboot reached status
        #   drivers enumerated correctly
        #
        #   dmesg warnings found
        #   dmesg errors found

        # Create query
        entry = {
            "boot_folder_name": boot_folder_name,
            "hdl_hash": hdl_hash,
            "linux_hash": linux_hash,
            "boot_partition_hash": boot_partition_hash,
            "hdl_branch": hdl_branch,
            "linux_branch": linux_branch,
            "boot_partition_branch": boot_partition_branch,
            "is_hdl_release": is_hdl_release,
            "is_linux_release": is_linux_release,
            "is_boot_partition_release": is_boot_partition_release,
            "uboot_reached": uboot_reached,
            "linux_prompt_reached": linux_prompt_reached,
            "drivers_enumerated": drivers_enumerated,
            "dmesg_warnings_found": dmesg_warnings_found,
            "dmesg_errors_found": dmesg_errors_found,
            "jenkins_job_date": jenkins_job_date,
            "jenkins_build_number": jenkins_build_number,
            "jenkins_project_name": jenkins_project_name,
            "jenkins_agent": jenkins_agent,
        }
        # Setup index if necessary
        self.db.index_name = "dummy" if self.use_test_index else "boot_tests"
        s = self.db.import_schema(self._get_schema("boot_tests.json"))
        self.db.create_db_from_schema(s)
        # Add entry
        self.db.add_entry(entry)

    def log_hdl_resources_from_csv(self, filename):

        if not os.path.exists(filename):
            raise Exception("File does not exist: " + str(filename))

        with open(filename, "r") as csvfile:
            csvreader = csv.reader(csvfile)
            fields = next(csvreader)
            values = next(csvreader)
        fields = fields[1:]
        self._translate_hdl_resource_fields(fields)
        values = values[1:]
        entry = dict(zip(fields, values))
        # Setup index if necessary
        self.db.index_name = "hdl_resources" if not self.use_test_index else "dummy"
        s = self.db.import_schema(self._get_schema("hdl_resources.json"))
        self.db.create_db_from_schema(s)
        # Add entry
        self.db.add_entry(entry)

    def log_ad9361_tx_quad_cal_test(
        self,
        test_name,
        device,
        failed,
        iterations,
        channel,
        date=datetime.datetime.now(),
    ):
        """ Upload AD9361 tx quad cal test data to elasticsearch """
        # Create query
        entry = {
            "test_name": test_name,
            "date": date,
            "failed": failed,
            "iterations": iterations,
            "device": device,
            "channel": channel,
        }
        # Setup index if necessary
        self.db.index_name = "dummy" if self.use_test_index else "ad936x_tx_quad_cal"
        s = self.db.import_schema(self._get_schema("ad936x_tx_quad_cal.json"))
        self.db.create_db_from_schema(s)
        # Add entry
        self.db.add_entry(entry)

    def log_lte_evm_test(
        self,
        device_name,
        tx_attn,
        rx_gain_control_mode,
        lo_freq,
        tmn,
        bw,
        evm_pbch,
        evm_pcfich,
        evm_phich,
        evm_pdcch,
        evm_rs,
        evm_sss,
        evm_pss,
        evm_pdsch,
        date=datetime.datetime.now(),
    ):
        """ Upload LTE EVM tests to elasticsearch """
        # Create query
        entry = {
            "device_name": device_name,
            "date": date,
            "tx_attn": tx_attn,
            "rx_gain_control_mode": rx_gain_control_mode,
            "lo_freq": lo_freq,
            "tmn": tmn,
            "bw": bw,
            "evm_pbch": evm_pbch,
            "evm_pcfich": evm_pcfich,
            "evm_phich": evm_phich,
            "evm_pdcch": evm_pdcch,
            "evm_rs": evm_rs,
            "evm_sss": evm_sss,
            "evm_pss": evm_pss,
            "evm_pdsch": evm_pdsch,
        }
        # Setup index if necessary
        self.db.index_name = "lte_evm" if not self.use_test_index else "dummy"
        s = self.db.import_schema(self._get_schema("evm_tests_el.json"))
        self.db.create_db_from_schema(s)
        # Add entry
        self.db.add_entry(entry)

    def log_github_stats(
        self,
        repo,
        views,
        clones,
        view_unique,
        clones_unique,
        date=datetime.datetime.now(),
    ):
        """ Upload github stats to elasticsearch """
        # Create query
        entry = {
            "repo": repo,
            "date": date,
            "views": views,
            "clones": clones,
            "view_unique": view_unique,
            "clones_unique": clones_unique,
        }
        # Setup index if necessary
        self.db.index_name = "github_stats" if not self.use_test_index else "dummy"
        s = self.db.import_schema(self._get_schema("github_stats.json"))
        self.db.create_db_from_schema(s)
        # Add entry
        self.db.add_entry(entry)

    def log_github_release_stats(
        self,
        repo,
        tag,
        downloads,
        release_date,
        date=datetime.datetime.now(),
    ):
        """ Upload github release stats to elasticsearch """
        # Create query
        entry = {
            "repo": repo,
            "date": date,
            "downloads": downloads,
            "tag": tag,
            "release_date": release_date,
        }
        # Setup index if necessary
        self.db.index_name = (
            "github_release_stats" if not self.use_test_index else "dummy"
        )
        s = self.db.import_schema(self._get_schema("github_release_stats.json"))
        self.db.create_db_from_schema(s)
        # Add entry
        self.db.add_entry(entry)