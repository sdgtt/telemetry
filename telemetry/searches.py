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

    def boot_tests(self, boot_folder_name=None):
        """ Query boot test results from elasticsearch """
        index = "boot_tests" if not self.use_test_index else "dummy"
        s = []
        if boot_folder_name:
            s.append({"match": {"boot_folder_name": boot_folder_name}})
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
