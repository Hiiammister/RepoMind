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

def get_repo_tree(owner, repo, token=None):
    # get default branch first
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    repo_data = requests.get(repo_url, headers=headers).json()
    branch = repo_data.get("default_branch", "main")

    # fetch tree recursively
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    tree_resp = requests.get(tree_url, headers=headers)

    if tree_resp.status_code != 200:
        return []

    tree_data = tree_resp.json().get("tree", [])

    # keep only files
    files = [item["path"] for item in tree_data if item["type"] == "blob"]

    return files