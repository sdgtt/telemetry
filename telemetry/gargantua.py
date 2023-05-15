from bs4 import BeautifulSoup
import os
import re
import requests
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

    def get_artifacts(self):
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
                            artifacts.append(Artifact(_parser))
                    else:
                        artifacts.append(Artifact(parser))
                except Exception as ex:
                    print(f"Cannot create Artifact object {f}; Reason {str(ex)}")
        return artifacts

    def log_artifacts(self):
        artifacts = self.get_artifacts()
        ignore = ["dmesg"]
        for artifact in artifacts:
            if artifact.artifact_info_type in ignore:
                continue
            artifact.log_elastic(self.es_server)

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

    def __init__(self,parser):
        # get parser object based on url
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

    def log_elastic(self, es_server):
        '''Send data elasticsearch '''
        try:
            t = telemetry.ingest(server=es_server)
            for i,p in enumerate(self.payload_raw):
                entry = self.to_dict()
                entry.update({"job_build_parameters": "NA"})
                entry.update({"payload": self.payload[i][1] \
                    if len(self.payload[i]) == 2 else self.payload[i]})
                entry.update({"payload_ts": self.payload[i][0] \
                    if len(self.payload[i]) == 2 else "NA"})
                entry.update({"payload_param": self.payload_param[i]})
                entry.update({"payload_raw": p})
                print("Saving entry to Elastic {}".format(entry))
                t.log_artifacts(**entry)
                
        except Exception as ex:
            print("Cannot ingest artifact")
            raise ex

    def search_elastic(self):
        '''Obtain data from the elasticsearch using appx. match'''
        pass