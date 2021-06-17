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

        for f in fields:
            if self.raw_boot_test_result:
                if f in self.raw_boot_test_result.keys():
                    setattr(self, f, self.raw_boot_test_result[f])
                elif f in ["drivers_enumerated", 
                            "drivers_missing", 
                            "dmesg_warnings_found", 
                            "dmesg_errors_found",
                            "pytest_errors",
                            "pytest_failures",
                            "pytest_skipped",
                            "pytest_tests"]:
                    setattr(self, f, "0")
                else:
                    setattr(self, f, "NA")
            else:
                setattr(self, f, None)

        self.boot_test_result, self.boot_test_failure = self.__is_pass()

    def __is_pass(self):
        # TODO: needs further detailed implementation
        # to represent correctly the actual status of the board
        if not self.raw_boot_test_result:
            return None,None
        result = 'Pass'
        failure = []
            # if self.linux_prompt_reached and\
            #    self.dmesg_errors_found == '0' and\
            #    self.pytest_errors == '0' and\
            #    self.pytest_failures == '0':
            #     return 'Pass' 
        if self.pytest_failures != '0':
            result = 'Fail'
            failure.append('pytest failure {}'.format(self.pytest_failures))
        if self.pytest_errors != '0':
            result = 'Fail'
            failure.append('pytest errors {}'.format(self.pytest_errors))
        if self.drivers_missing != '0':
            result = 'Fail'
            failure.append('linux drivers missing {}'.format(self.drivers_missing))
        if self.dmesg_errors_found != '0':
            result = 'Fail'
            failure.append('linux dmesg errors {}'.format(self.dmesg_errors_found))
        if not self.linux_prompt_reached:
            result = 'Fail'
            failure = ['Linux prompt not reached']
        if not self.uboot_reached:
            result = 'Fail'
            failure = ['u-boot not reached']
        if self.last_failing_stage_failure != 'NA':
            result = 'Fail'
            failure = [self.last_failing_stage_failure]
        return result,failure

    def display(self):
        return self.__dict__

class BoardBootTests:
    def __init__(self, boot_folder_name, jenkins_project_name=None):

        if not boot_folder_name:
            raise ValueError('boot_folder_name must not be null or empty')
        
        db_res = telemetry.searches(mode=MODE, server=ELASTIC_SERVER)
        # create boards object from raw db_res
        self._boot_tests = [ BootTest(res_dict) for res_dict in db_res.boot_tests(boot_folder_name, jenkins_project_name)[boot_folder_name] ]

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