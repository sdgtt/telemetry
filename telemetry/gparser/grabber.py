from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm
import os
import requests

class Grabber:
    '''Class providing grabber functionality'''
    def __init__(self, auth=None):
        self.sess = self.retry_session()
        self.file_dir = "event_horizon"
        if auth:
            self.sess.auth = auth

    def download_file(self, url, filename):
        '''Downloads file'''
        resp = self.sess.get(url, stream=True)
        if not resp.ok:
            raise Exception(url + " - url not found!" )
        total = int(resp.headers.get("content-length", 0))
        fname = os.path.join(self.file_dir, filename)
        if not os.path.exists(self.file_dir):
            os.mkdir(self.file_dir)
        with open(fname, "wb") as file, tqdm(
            desc=fname, total=total, unit="iB", unit_scale=True, unit_divisor=1024,
        ) as bar:
            for data in resp.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)
        return fname

    def retry_session(self, retries=3, backoff_factor=0.3, 
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