import os
import re
import telemetry
from string import Template

class Markdown:
    def __init__(self, file):
        self.filename = os.path.basename(file)
        with open(file,'r') as f:
            self.template_str = f.read() 
            self.template = Template(self.template_str)

    def get_identifiers(self):
        return re.findall('\$(\w+)\s',self.template_str)

    def substitute(self, fields):
        return self.template.substitute(fields)
    
    def generate(self, fields, custom_file_name=None):
        formatted = self.substitute(fields)
        output = self.filename.split('.')[0] + ".md"
        if custom_file_name:
            output = custom_file_name
        with open(f"{os.path.join(output)}",'w') as f:
            f.write(formatted)
        return output
    
class ResultsMarkdown(Markdown):
    CRITICAL = ["UpdateBOOTFiles"]

    def __init__(self, data):
        self.param_dict = self.generate_param(data)
        dir = os.path.dirname(os.path.realpath(__file__))
        template_path = os.path.join(dir, "templates", "results.template.md")
        super(ResultsMarkdown, self).__init__(template_path)

    def generate_param(self,data):
        param_dict = {}
        for bn, info in data.items():
            if info == "NA":
                param_dict[bn] = None
                continue
            test_build_status = None
            if str(info["last_failing_stage"]) in self.CRITICAL:
                test_build_status = "FAILURE"
            elif int(info["drivers_missing"])>0 or\
                int(info["dmesg_errors_found"])>0 or\
                int(info["pytest_errors"])>0 or\
                int(info["pytest_failures"])>0 or\
                (int(info["pytest_skipped"])==0 and int(info["pytest_tests"]==0)):
                test_build_status = "UNSTABLE"
            elif str(info["last_failing_stage"]) == "NA":
                test_build_status = "PASSING"
            else:
                test_build_status = "INVALID"

            # update test stage status
            uboot_reached_status = "✔" if bool(info["uboot_reached"]) else "❌"
            linux_prompt_reached_status = "✔" if bool(info["linux_prompt_reached"]) else "❌"
            drivers_enumerated_status = "✔" if int(info["drivers_missing"]) == 0 and test_build_status != "FAILURE" else "❌"
            dmesg_status = "✔" if int(info["dmesg_errors_found"]) == 0 and test_build_status != "FAILURE" else "❌"
            pytest_tests_status = "✔" if int(info["pytest_failures"]) == 0 and test_build_status != "FAILURE" else "❌"

            # added validations
            pytest_tests_status = "⛔" if int(info["pytest_skipped"]) == 0 and int(info["pytest_tests"]) == 0 else pytest_tests_status

            # update test stage details
            if test_build_status == "FAILURE":
                iio_drivers_missing_details = "No Details"
                iio_drivers_found_details = "No Details"
                dmesg_errors_found_details = "No Details"
                pytest_failures_details = "No Details"
            else:
                iio_drivers_missing_details = "No missing drivers" if len(info["missing_devs"]) == 0 else ("<br>").join(info["missing_devs"])
                iio_drivers_found_details = "No iio drivers found" if len(info["enumerated_devs"]) == 0 else ("<br>").join(info["enumerated_devs"])
                dmesg_errors_found_details = "No errors" if len(info["dmesg_err"]) == 0 else ("<br>").join(info["dmesg_err"])   
                pytest_failures_details = "No failures"             
                pytest_failures_details = "Invalid" if pytest_tests_status == "⛔" else pytest_failures_details
                pytest_details = [] # list of all pytest failure details
                if len(info["pytest_failure"]) != 0:
                    if isinstance(info["pytest_failure"][0], list):
                        if len(info["pytest_failure"][0]) > 0: 
                            for items in info["pytest_failure"][0]:
                                # add the details of first test case in the list as separate items (no changes)
                                pytest_details.append(items)
                        for data in info["pytest_failure"][1:]:
                            if isinstance(data, list):
                                if len(data) > 0:
                                    # add the details of remaining test cases in the list and add "* " to data[0] (test case name) for markdown 
                                    pytest_details.append(f"* {data[0]}")                            
                                    for details in data[1:]:
                                        pytest_details.append(details)
                        # create structure of pytest failure details for markdown
                        pytest_failures_details = ("\n\n").join(pytest_details)                                
                    else:
                        pytest_failures_details = ("<br>").join(info["pytest_failure"])

            last_failing_stage = str(info["last_failing_stage"])
            last_failing_stage_failure = str(info["last_failing_stage_failure"])

            param_dict[bn] = {
                "board_name" : bn,
                "branch": info["info_txt"]["BRANCH"],
                "pr_id": info["info_txt"]["PR_ID"],
                "timestamp": info["info_txt"]["TIMESTAMP"],
                "direction": info["info_txt"]["DIRECTION"],
                "triggered_by": info["info_txt"]["Triggered by"],
                "commit_sha": info["info_txt"]["COMMIT SHA"],
                "commit_date": info["info_txt"]["COMMIT_DATE"],
                "test_job_name": info["jenkins_project_name"],
                "test_build_number": info["jenkins_build_number"],
                "test_build_status": test_build_status,
                "uboot_reached_status": uboot_reached_status,
                "linux_prompt_reached_status": linux_prompt_reached_status,
                "drivers_enumerated_status":  drivers_enumerated_status,
                "dmesg_status":  dmesg_status,
                "pytest_tests_status": pytest_tests_status,
                "drivers_enumerated": "",
                "drivers_missing": "",
                "dmesg_warnings_found": "",
                "dmesg_errors_found": "",
                "pytest_tests": "",
                "pytest_errors": "",
                "pytest_failures": "",
                "pytest_skipped": "",
                "last_failing_stage": last_failing_stage if last_failing_stage != "NA" else "No Details",
                "last_failing_stage_failure":last_failing_stage_failure if last_failing_stage_failure != "NA" else "No Details",
                "iio_drivers_missing_details": iio_drivers_missing_details,
                "iio_drivers_found_details": iio_drivers_found_details,
                "dmesg_errors_found_details": dmesg_errors_found_details,
                "pytest_failures_details": pytest_failures_details,
                "test_status": test_build_status,
            }
        return param_dict

    def generate_gist(self, url, token):
        print(f"========== Publish Results ==========")
        for bn,param in self.param_dict.items():
            if not param:
                print(f'Result: {bn} | ---- | HW not available')
                continue
            outfile = self.generate(param, bn+".md")
            gist = telemetry.gist.Gist(url, token)
            gist_link = gist.create_gist(outfile, f'''Boardname: {param["board_name"]}\n
                                           Branch: {param["branch"]}\nPR ID: {param["pr_id"]}\n
                                           timestamp: {param["timestamp"]}''')
            print(f'Result: {bn} | {gist.gh_url}/{gist_link} | {param["test_status"]}')
