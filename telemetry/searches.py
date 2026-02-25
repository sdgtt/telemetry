import telemetry
import datetime
import os
import copy


class searches:
    use_test_index = False

    def __init__(self, mode="elastic", server="alpine"):
        if mode == "elastic":
            self.db = telemetry.elastic(server=server)

    def _get_schema(self, name):
        loc = os.path.dirname(__file__)
        return os.path.join(loc, "resources", name)

    def artifacts(self,
                   target_board=None,
                   job=None,
                   job_no = None,
                   artifact_info_type = None,
                ):
        """Query artifacts data from elasticsearch.

        Args:
            target_board: Filter by target board name (e.g., "zynq-zc706-adv7511")
            job: Filter by Jenkins job name (e.g., "HW_tests/HW_test_multiconfig")
            job_no: Filter by Jenkins build number (integer field in ES schema)
            artifact_info_type: Filter by artifact type (e.g., "dmesg_error", "pytest_failure")

        Returns:
            List of artifact documents sorted by archive_date (descending)

        Note on Elasticsearch field types and .keyword suffix:
            The .keyword suffix is ONLY needed for fields mapped as "text" type that have
            a multi-field "keyword" sub-field for exact matching.

            For fields already mapped as "keyword" type, do NOT use .keyword suffix.
            For fields mapped as "integer" type, do NOT use .keyword suffix.

            In the artifacts index schema (based on actual ES mapping):
            - target_board: keyword type -> do NOT use .keyword
            - job: keyword type -> do NOT use .keyword
            - job_no: integer type -> do NOT use .keyword
            - artifact_info_type: keyword type -> do NOT use .keyword
        """
        index = "artifacts" if not self.use_test_index else "dummy"

        # Build list of match clauses for the bool query
        s = []

        # target_board is a KEYWORD field in ES - do NOT use .keyword suffix
        # keyword fields already store exact values without tokenization
        if target_board:
            s.append({"match": {"target_board": target_board}})

        # job is a KEYWORD field in ES - do NOT use .keyword suffix
        if job:
            s.append({"match": {"job": job}})

        # job_no is an INTEGER field in ES - do NOT use .keyword suffix
        if job_no:
            s.append({"match": {"job_no": job_no}})

        # artifact_info_type is a KEYWORD field in ES - do NOT use .keyword suffix
        if artifact_info_type:
            s.append({"match": {"artifact_info_type": artifact_info_type}})
        # Create query
        if s:
            query = {
                "sort": [{"archive_date": {"order": "desc"}}],
                "query": {"bool": {"must": s}},
            }
        else:
            query = {
                "sort": [{"archive_date": {"order": "desc"}}],
                "query": {"match_all": {}},
            }

        res = self.db.es.search(index=index, size=1000, body=query)
        artifacts_data = [data["_source"] for data in res["hits"]["hits"]]
        return artifacts_data

    def boot_tests(self,
                   boot_folder_name=None,
                   jenkins_project_name=None,
                   jenkins_build_no = None,
                ):
        """Query boot test results from elasticsearch.

        Args:
            boot_folder_name: Filter by boot folder/board name (e.g., "zynq-zc706-adv7511")
            jenkins_project_name: Filter by Jenkins project name (e.g., "HW_tests/HW_test_multiconfig")
            jenkins_build_no: Filter by Jenkins build number

        Returns:
            Dictionary mapping board names to their test result records,
            sorted by jenkins_job_date (ascending)

        Note on Elasticsearch field types:
            All fields in boot_tests index that are queried here are text/keyword types,
            so .keyword suffix is appropriate for exact matching.
        """
        index = "boot_tests" if not self.use_test_index else "dummy"

        # Build list of match clauses for the bool query
        s = []

        # boot_folder_name is a text field - use .keyword for exact matching
        if boot_folder_name:
            s.append({"match": {"boot_folder_name.keyword": boot_folder_name}})

        # jenkins_project_name is a text field - use .keyword for exact matching
        if jenkins_project_name:
            s.append({"match": {"jenkins_project_name.keyword": jenkins_project_name}})

        # jenkins_build_number is stored as keyword type in boot_tests schema
        # (different from job_no in artifacts which is integer)
        if jenkins_build_no:
            s.append({"match": {"jenkins_build_number.keyword": jenkins_build_no}})
        # Create query
        if s:
            query = {
                "sort": [{"jenkins_job_date": {"order": "asc"}}],
                "query": {"bool": {"must": s}},
            }
        else:
            query = {
                "sort": [{"jenkins_job_date": {"order": "asc"}}],
                "query": {"match_all": {}},
            }
        res = self.db.es.search(index=index, size=1000, body=query)

        # fields = [
        #     "boot_folder_name",
        #     "hdl_hash",
        #     "linux_hash",
        #     "boot_partition_hash",
        #     "hdl_branch",
        #     "linux_branch",
        #     "boot_partition_branch",
        #     "is_hdl_release",
        #     "is_linux_release",
        #     "is_boot_partition_release",
        #     "uboot_reached",
        #     "linux_prompt_reached",
        #     "drivers_enumerated",
        #     "drivers_missing",
        #     "dmesg_warnings_found",
        #     "dmesg_errors_found",
        #     "jenkins_job_date",
        #     "jenkins_build_number",
        #     "jenkins_project_name",
        #     "jenkins_agent",
        #     "jenkins_trigger",
        #     "source_adjacency_matrix",
        #     "pytest_errors",
        #     "pytest_failures",
        #     "pytest_skipped",
        #     "pytest_tests",
        #     "last_failing_stage",
        #     "last_failing_stage_failure"
        # ]

        # Extract all unique boot_folder_name's
        names = [val["_source"]["boot_folder_name"] for val in res["hits"]["hits"]]
        names = list(set(names))  # get unique entries

        results = {}
        for name in names:
            rows = []
            # Extract rows with given board name
            for val in res["hits"]["hits"]:
                if val["_source"]["boot_folder_name"] == name:
                    r = copy.copy(val["_source"])
                    del r["boot_folder_name"]
                    rows.append(r)
            results[name] = rows

        return results

    def ad9361_tx_quad_cal_test(self, test_name=None, device=None, channel=None):
        """ Query AD9361 tx quad cal test data to elasticsearch """
        index = "ad936x_tx_quad_cal" if not self.use_test_index else "dummy"
        s = []
        if test_name:
            s.append({"match": {"test_name": test_name}})
        if device:
            s.append({"match": {"device": device}})
        if channel:
            s.append({"match": {"channel": str(channel)}})
        # Create query
        if s:
            query = {
                "sort": [{"date": {"order": "asc"}}],
                "query": {"bool": {"must": s}},
            }
        else:
            query = {"sort": [{"date": {"order": "asc"}}], "query": {"match_all": {}}}
        res = self.db.es.search(index=index, size=1000, body=query)

        x = [val["_source"]["date"] for val in res["hits"]["hits"]]
        y = [val["_source"]["failed"] for val in res["hits"]["hits"]]
        t = [val["_source"]["iterations"] for val in res["hits"]["hits"]]
        return x, y, t

    def github_stats(self, repo=None, date=None):
        """ Query github stats from elasticsearch """
        index = "github_stats" if not self.use_test_index else "dummy"
        s = []
        if repo:
            s.append({"match": {"repo": repo}})
        if date:
            s.append({"match": {"date": date}})
        # Create query
        if s:
            query = {
                "sort": [{"date": {"order": "asc"}}],
                "query": {"bool": {"must": s}},
            }
        else:
            query = {"sort": [{"date": {"order": "asc"}}], "query": {"match_all": {}}}
        res = self.db.es.search(index=index, size=1000, body=query)

        dates = [val["_source"]["date"] for val in res["hits"]["hits"]]
        repo = [val["_source"]["repo"] for val in res["hits"]["hits"]]
        views = [val["_source"]["views"] for val in res["hits"]["hits"]]
        clones = [val["_source"]["clones"] for val in res["hits"]["hits"]]
        view_unique = [val["_source"]["view_unique"] for val in res["hits"]["hits"]]
        clones_unique = [val["_source"]["clones_unique"] for val in res["hits"]["hits"]]
        return {
            repo[i]: {
                "date": dates[i],
                "views": views[i],
                "clones": clones[i],
                "view_unique": view_unique[i],
                "clones_unique": clones_unique[i],
            }
            for i in range(len(dates))
        }

    def github_release_stats(self, repo=None, tag=None, date=None):
        """ Query github release stats from elasticsearch """
        index = "github_release_stats" if not self.use_test_index else "dummy"
        s = []
        if repo:
            s.append({"match": {"repo": repo}})
        if tag:
            s.append({"match": {"tag": tag}})
        if date:
            s.append({"match": {"date": date}})
        # Create query
        if s:
            query = {
                "sort": [{"date": {"order": "asc"}}],
                "query": {"bool": {"must": s}},
            }
        else:
            query = {"sort": [{"date": {"order": "asc"}}], "query": {"match_all": {}}}
        res = self.db.es.search(index=index, size=1000, body=query)

        dates = [val["_source"]["date"] for val in res["hits"]["hits"]]
        repo = [val["_source"]["repo"] for val in res["hits"]["hits"]]
        downloads = [val["_source"]["downloads"] for val in res["hits"]["hits"]]
        tag = [val["_source"]["tag"] for val in res["hits"]["hits"]]
        release_date = [val["_source"]["release_date"] for val in res["hits"]["hits"]]

        return {
            repo[i]: {
                "date": dates[i],
                "downloads": downloads[i],
                "tag": tag[i],
                "release_date": release_date[i],
            }
            for i in range(len(dates))
        }

