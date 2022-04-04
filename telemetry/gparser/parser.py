from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm
from urllib.parse import urlparse
import json
import os
import re
import requests
import traceback
import junitparser
from junitparser import JUnitXml, Skipped, Error, Failure

# Temporary directory to contain downloaded file
FILE_DIR = 'event_horizon'

def get_parser(url):
    '''Factory method that provides appropriate parser object base on given url'''
    parsers = {
        '^.*dmesg_[a-zA-Z0-9-]+\.log': Dmesg,
        '^.*dmesg_.+err\.log': DmesgError,
        '^.*dmesg_.+warn\.log': DmesgWarning,
        '^.*enumerated_devs\.log': EnumeratedDevs,
        '^.*missing_devs\.log': MissingDevs,
        '^.*pyadi-iio.*\.xml': [PytestFailure, PytestSkipped, PytestError]
    }

    # find parser
    for sk, parser in parsers.items():
        if re.match(sk, url):
            if isinstance(parser, list):
                return [p(url) for p in parser]
            else:
                return parser(url)

    raise Exception("Cannot find Parser for {}".format(url))

def retry_session(retries=3, backoff_factor=0.3, 
        status_forcelist=(429, 500, 502, 504),
        session=None,
    ):
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

def grabber(url, fname):
    ''' Downloads file from a given url as fname'''
    resp = retry_session().get(url, stream=True)
    if not resp.ok:
        raise Exception(url + " - url not found!" )
    total = int(resp.headers.get("content-length", 0))
    with open(fname, "wb") as file, tqdm(
        desc=fname, total=total, unit="iB", unit_scale=True, unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


class Parser:
    '''Base class for a parser object'''
    def __init__(self, url):
        
        self.url = url
        self.server = None
        self.job = None
        self.job_no = None
        self.job_date = None
        self.file_name = None
        self.file_info = None
        self.target_board = None
        self.artifact_info_type = None
        self.payload_raw = []
        self.payload = []
        self.payload_param = []
        self.initialize()

    def initialize(self):
        url_ = urlparse(self.url)
        self.multilevel = False
        if len(url_.path.split('/job/')) > 2:
            self.multilevel = True

        # initialize attributes
        self.server = url_.scheme + '://' + url_.netloc + '/' + url_.path.split('/')[1]
        self.job, self.job_no, self.job_date  = self.get_job_info()
        file_info = self.get_file_info()
        self.file_name = file_info[0]
        self.file_info = file_info[1]
        self.target_board = file_info[2]
        self.artifact_info_type=file_info[3]
        self.payload_raw=self.get_payload_raw()
        payload_parsed=self.get_payload_parsed()
        self.payload=payload_parsed[0]
        if len(payload_parsed) == 2:
            self.payload_param=payload_parsed[1]

    def show_info(self):
        return self.__dict__

    def get_job_info(self):
        '''returns jenkins project name, job no and job date'''
        if self.multilevel:
            url = urlparse(self.url)
            job=url.path.split('/')[3] + '/' + url.path.split('/')[5]
            job_no=url.path.split('/')[6]
            # TODO: get job date using jenkins api
            job_date=None
            return (job,job_no,job_date)
        else:
            raise Exception("Does not support non multilevel yet!")

    def get_file_info(self):
        '''returns file name, file info, target_board, artifact_info_type'''
        if self.multilevel:
            url = urlparse(self.url)
            file_name = url.path.split('/')[-1]
            file_info = file_name.split('_')
            target_board=file_info[0]
            artifact_info_type=file_info[1] + '_' + file_info[2]
            artifact_info_type = remove_suffix(artifact_info_type,".log")
            return (file_name, file_info, target_board, artifact_info_type)
        else:
            raise Exception("Does not support non multilevel yet!")


    def get_payload_raw(self):
        payload = []
        file_path = os.path.join(FILE_DIR, self.file_name)
        try:
            if not os.path.exists(FILE_DIR):
                os.mkdir(FILE_DIR)
            grabber(self.url, file_path)
            with open(file_path, "r") as f:
                payload = [l.strip() for l in f.readlines()]
        except Exception as ex:
            traceback.print_exc()
            print("Error Parsing File!")
        finally:
            os.remove(file_path)
        return payload

    def get_payload_parsed(self):
        payload = []
        for p in self.payload_raw:
            # try to extract timestamp from data
            x = re.search("\[.*(\d+\.\d*)\]\s(.*)", p)
            if x:
                payload.append((x.group(1),x.group(2)))
            else:
                x = re.search("(.*)", p)
                payload.append(x.group(1))
        return payload

class Dmesg(Parser):

    def __init__(self, url):
        super(Dmesg, self).__init__(url)

    def get_file_info(self):
        '''returns file name, file info, target_board, artifact_info_type'''
        if self.multilevel:
            url = urlparse(self.url)
            file_name = url.path.split('/')[-1]
            file_info = file_name.split('_')
            target_board=file_info[1]
            artifact_info_type=file_info[0]
            if len(file_info) == 3:
                artifact_info_type += '_' + file_info[2]
            artifact_info_type = remove_suffix(artifact_info_type,".log")
            return (file_name, file_info, target_board, artifact_info_type)
        else:
            raise Exception("Does not support non multilevel yet!")

class DmesgError(Dmesg):
    
    def __init__(self, url):
        super(DmesgError, self).__init__(url)

class DmesgWarning(Dmesg):
    
    def __init__(self, url):
        super(DmesgWarning, self).__init__(url)

class EnumeratedDevs(Parser):
    
    def __init__(self, url):
        super(EnumeratedDevs, self).__init__(url)

class MissingDevs(Parser):
    
    def __init__(self, url):
        super(MissingDevs, self).__init__(url)

class xmlParser(Parser):
    def __init__(self, url):
        super(xmlParser, self).__init__(url)
        
    def get_file_info(self):
        '''returns file name, file info, target_board, artifact_info_type'''
        if self.multilevel:
            url = urlparse(self.url)
            url_path = url.path.split('/')
            file_name = url_path[-1]
            if isinstance(self, PytestFailure):
                file_info = "pytest_failure"
            elif isinstance(self, PytestSkipped):
                file_info = "pytest_skipped"
            elif isinstance(self, PytestError):
                file_info = "pytest_error"
            target_board = file_name.replace('_','-')
            target_board = remove_suffix(target_board,"-reports.xml")
            artifact_info_type=file_info
            return (file_name, file_info, target_board, artifact_info_type)
        else:
            raise Exception("Does not support non multilevel yet!")
        
    def get_payload_raw(self):
        payload = []
        file_path = os.path.join(FILE_DIR, self.file_name)
        try:
            if not os.path.exists(FILE_DIR):
                os.mkdir(FILE_DIR)
            grabber(self.url, file_path)
            # Parser
            xml = JUnitXml.fromfile(file_path)
            resultType = getattr(junitparser, self.file_info.split("_")[1].capitalize())
            for suite in xml:
                for case in suite:
                    if case.result and type(case.result[0]) is resultType:
                        payload.append(case.name)
        except Exception as ex:
            traceback.print_exc()
            print("Error Parsing File!")
        finally:
            os.remove(file_path)
        return payload
    
    def get_payload_parsed(self):
        payload = []
        payload_split = {"procedure":[], "param":[]}
        for payload in self.payload_raw:
            procedure_param = payload.split("[")
            payload_split["procedure"].append(procedure_param[0])
            if len(procedure_param) == 2:
                payload_split["param"].append(procedure_param[1][:-1])
            else:
                payload_split["param"].append("NA")
        payload = payload_split["procedure"]
        payload_param = payload_split["param"]
        return (payload, payload_param)

class PytestFailure(xmlParser):
    def __init__(self, url):
        super(PytestFailure, self).__init__(url)
class PytestSkipped(xmlParser):
    def __init__(self, url):
        super(PytestSkipped, self).__init__(url)
class PytestError(xmlParser):
    def __init__(self, url):
        super(PytestError, self).__init__(url)