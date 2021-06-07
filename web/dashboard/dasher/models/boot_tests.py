import secrets
import telemetry

MODE = "elastic"
ELASTIC_SERVER="192.168.10.1"

class BootTest:
    def __init__(self, raw_boot_test_result=None):
        self.raw_boot_test_result = raw_boot_test_result
        self.__initialize_fields()
        
    def __initialize_fields(self):

        fields = [
            "boot_folder_name",
            "hdl_hash",
            "linux_hash",
            "boot_partition_hash",
            "hdl_branch",
            "linux_branch",
            "boot_partition_branch",
            "is_hdl_release",
            "is_linux_release",
            "is_boot_partition_release",
            "uboot_reached",
            "linux_prompt_reached",
            "drivers_enumerated",
            "drivers_missing",
            "dmesg_warnings_found",
            "dmesg_errors_found",
            "jenkins_job_date",
            "jenkins_build_number",
            "jenkins_project_name",
            "jenkins_agent",
            "source_adjacency_matrix",
            "pytest_errors",
            "pytest_failures",
            "pytest_skipped",
            "pytest_tests",
            "last_failing_stage",
            "last_failing_stage_failure"
        ]

        if self.raw_boot_test_result:
            for f,v in self.raw_boot_test_result.items():
                setattr(self, f, v)
        else:
            for f in fields:
                setattr(self, f, None)

        self.boot_test_result = self.__is_pass() #Pass/Fail

    def __is_pass(self):
        # TODO: needs further detailed implementation
        # to represent correctly the actual status of the board
        if self.raw_boot_test_result:
            if self.linux_prompt_reached and\
               self.dmesg_errors_found == '0' and\
               self.pytest_errors == '0' and\
               self.pytest_failures == '0':
                return 'Pass'   
            else:
                return 'Fail'
        return None

    def display(self):
        return self.__dict__

class BoardBootTests:
    def __init__(self, boot_folder_name):

        if not boot_folder_name:
            raise ValueError('boot_folder_name must not be null or empty')
        
        db_res = telemetry.searches(mode=MODE, server=ELASTIC_SERVER)
        # create boards object from raw db_res
        self._boot_tests = [ BootTest(res_dict) for res_dict in db_res.boot_tests(boot_folder_name)[boot_folder_name] ]

    @property
    def boot_tests(self):
        return self._boot_tests

if __name__ == "__main__":
    # b = Board("test")
    # print(b.__dict__)
    # b.status = "invalid"
    # assert b.status == BoardStatus.LINUX_READY
    B = BoardBootTests('zynq-zed-adv7511-ad9361-fmcomms2-3')
    print([bt.display() for bt in B.boot_tests])