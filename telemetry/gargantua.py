from bs4 import BeautifulSoup
import json
import os
import re
import requests
from datetime import datetime
import telemetry

class Gargantua:
    '''Tool for grabbing and logging Jenkins artifacts'''
    def __init__(self,
        jenkins_server,
        jenkins_username,
        jenkins_password,
        es_server,
        job_name,
        jobs=[]
    ):
        self.job_name = job_name
        self.jobs = jobs
        self.server = jenkins_server.strip("/")
        self.auth = None
        if jenkins_username and jenkins_password:
            self.auth = (jenkins_username, jenkins_password)
        self.es_server = es_server

    def generate_urls(self):
        targets = []
        jns = self.job_name.split('/')
        job_name = ""
        for jn in jns:
            job_name += "/job/{}".format(jn)
        for j in self.jobs:
            targets.append(self.server + job_name + '/' + j + '/artifact')
        return targets

    def crawler(self, url, directory=""):
        '''Crawls a given jenkins job url and returns artifacts list by thier relative path'''
        files = []
        ignore = ['dmesg_err.log']
        if self.auth:
            page = requests.get(url,auth=self.auth)
        else:
            page = requests.get(url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, "html.parser")
            fileList = soup.find_all(class_="fileList")
            for el in list(fileList[0].children):
                file_pack = list(el.children)
                if len(file_pack) > 1:
                    links = file_pack[1].select("a")
                    if len(links) > 1:
                        sub_dir = ""
                        for link in links:
                            sub_dir += link.get_text() + '/'
                        # crawl again
                        files += self.crawler(url + '/' + sub_dir.strip('/'), directory + sub_dir)
                    else:
                        f = links[0].get_text()
                        if f in ignore:
                            continue
                        files.append(directory + f)
                        # if re.match('.*\.log',f):
                        #     files.append(directory + f)
            return files
        else:
            raise Exception(f"Cannot fetch {url}: Error code {page.status_code}")
    
    def crawl_files(self):
        artifact_urls = {}
        targets = self.generate_urls()
        for target in targets:
            artifact_urls.update(
                {
                    target : self.crawler(target)
                }
            )
        return artifact_urls

    def get_artifacts(self, content_filter=None):
        artifacts = []
        target_map = self.crawl_files()
        for job, files in target_map.items():
            for f in files:
                try:
                    # get parser
                    grabber = telemetry.grabber.Grabber(self.auth)
                    parser = telemetry.parser.get_parser(job + '/' + f,grabber)
                    if isinstance(parser, list):
                        for _parser in parser:
                            artifacts.append(Artifact(_parser, content_filter))
                    else:
                        artifacts.append(Artifact(parser, content_filter))
                except Exception as ex:
                    print(f"Cannot create Artifact object {f}; Reason {str(ex)}")
        return artifacts

    def log_artifacts(self, content_filter=None, filter_verbose=False, dry_run=False, dry_run_output=None):
        artifacts = self.get_artifacts(content_filter)
        ignore = ["dmesg"]
        for artifact in artifacts:
            if artifact.artifact_info_type in ignore:
                continue
            artifact.log_elastic(self.es_server, filter_verbose, dry_run, dry_run_output)

class Artifact:
    '''Class representing a test job artifact'''

    attributes = [
        "url",
        "server",
        "job",
        "job_no",
        "job_date",
        "file_name",
        "target_board",
        "artifact_info_type",
        "payload_raw",
        "payload",
        "payload_param"
    ]

    def __init__(self, parser, content_filter=None):
        # get parser object based on url
        self.content_filter = content_filter
        try:
            self.parser = parser
            for attrib in self.attributes:
                if hasattr(self.parser, attrib):
                    setattr(self, attrib, getattr(self.parser, attrib))
        except Exception as ex:
            print(str(ex))
            raise ex

    def display_info(self):
        return self.__dict__

    def to_dict(self):
        dict_map = {}
        for attr in self.attributes:
            dict_map.update({attr: getattr(self, attr)})
        return dict_map

    def log_elastic(self, es_server, filter_verbose=False, dry_run=False, dry_run_output=None):
        '''Send data to elasticsearch with optional pre-upload filtering'''
        try:
            entries_to_upload = []
            entries_filtered = []

            for i, p in enumerate(self.payload_raw):
                message = self.payload[i][1] if len(self.payload[i]) == 2 else self.payload[i]

                # Apply content filter if configured
                if self.content_filter:
                    should_upload, reason = self.content_filter.should_upload(
                        message=message,
                        issue_type=self.artifact_info_type,
                        board=getattr(self, 'target_board', None),
                        project=getattr(self, 'job', None)
                    )
                    if not should_upload:
                        if filter_verbose:
                            print(f"Filtered out (reason: {reason}): {p[:80]}...")
                        entries_filtered.append({
                            "reason": reason,
                            "payload_raw": p,
                            "payload": message
                        })
                        continue

                entry = self.to_dict()
                entry.update({"job_build_parameters": "NA"})
                entry.update({"payload": message})
                entry.update({"payload_ts": self.payload[i][0] \
                    if len(self.payload[i]) == 2 else "NA"})
                entry.update({"payload_param": self.payload_param[i]})
                entry.update({"payload_raw": p})
                entries_to_upload.append(entry)

            if dry_run:
                # Save to local file instead of uploading
                dry_run_data = {
                    "artifact_info": {
                        "file_name": getattr(self, 'file_name', 'unknown'),
                        "artifact_info_type": getattr(self, 'artifact_info_type', 'unknown'),
                        "target_board": getattr(self, 'target_board', 'unknown'),
                        "job": getattr(self, 'job', 'unknown'),
                        "url": getattr(self, 'url', 'unknown')
                    },
                    "summary": {
                        "total_entries": len(self.payload_raw),
                        "entries_to_upload": len(entries_to_upload),
                        "entries_filtered": len(entries_filtered)
                    },
                    "entries_to_upload": entries_to_upload,
                    "entries_filtered": entries_filtered
                }

                if dry_run_output is not None:
                    # Append to the output list (will be saved later)
                    dry_run_output.append(dry_run_data)

                print(f"[DRY-RUN] {self.file_name}: {len(entries_to_upload)} entries would be uploaded, {len(entries_filtered)} filtered out")
            else:
                # Actually upload to Elasticsearch
                t = telemetry.ingest(server=es_server)
                for entry in entries_to_upload:
                    print("Saving entry to Elastic {}".format(entry))
                    t.log_artifacts(**entry)

        except Exception as ex:
            print("Cannot ingest artifact")
            raise ex

    def search_elastic(self):
        '''Obtain data from the elasticsearch using appx. match'''
        pass