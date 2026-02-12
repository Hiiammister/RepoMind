from urllib.parse import urlparse
import requests
import base64
def parse_github_url(url:str):
    parsed=urlparse(url)

    if "github.com" not in parsed.netloc:
        return None, None
    parts =parsed.path.strip("/").split("/")
    if len(parts)<2:
        return None, None
    owner=parts[0]
    repo=parts[1].replace(".git","")
    return owner, repo

def getReadme(owner,repo, token=None):
    url=f"https://api.github.com/repos/{owner}/{repo}/readme"
    headers={}
    if token:
        headers["Authorization"]=f"token {token}"
    response=requests.get(url, headers=headers)
    if response.status_code!=200:
        return None
    data=response.json()
    content=data.get("content","")
    decoded=base64.b64decode(content).decode("utf-8", errors="ignore")
    return decoded