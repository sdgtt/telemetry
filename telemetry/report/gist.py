import os
from github import Github, Auth, InputFileContent


class Gist:
    def __init__(self, url=None, token=None):
        try:
            if not token:
                token=os.environ['GH_TOKEN']
        except KeyError as ex:
            raise Exception("Github token not defined")
        
        try:
            if not url:
                url=os.environ['GH_URL']
        except KeyError as ex:
            raise Exception("Github Gist url not defined")

        self.gh = Github(auth = Auth.Token(token))
        self.gh_auth_user = self.gh.get_user()
        self.gh_url = url

    def create_gist(self, markdown_file, desc=""):

        markdown_str = ""
        with open(markdown_file, 'r') as f:
            markdown_str = f.read()

        # Create a Gist
        gist = self.gh_auth_user.create_gist(
            public=False,
            files={markdown_file: InputFileContent(markdown_str)},
            description=desc
        )

        return gist.id
