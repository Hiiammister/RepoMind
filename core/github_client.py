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

def get_repo_tree(owner, repo, branch=None, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Get default branch if not provided
    if branch is None:
        repo_url = f"https://api.github.com/repos/{owner}/{repo}"
        repo_resp = requests.get(repo_url, headers=headers)

        if repo_resp.status_code != 200:
            return []

        branch = repo_resp.json().get("default_branch", "main")

    # Fetch recursive tree
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    tree_resp = requests.get(tree_url, headers=headers)

    if tree_resp.status_code != 200:
        return []

    tree_data = tree_resp.json().get("tree", [])

    # Keep only files
    files = [item["path"] for item in tree_data if item["type"] == "blob"]

    return files

def get_file_content(owner, repo, path, branch="main", token=None, max_size_bytes=200_000):
    """
    Returns (content_str, status)
    status: "ok" | "skip_large" | "skip_binary" | "error"
    """
    # Skip obvious binaries by extension
    binary_exts = {
        ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico",
        ".pdf", ".zip", ".tar", ".gz", ".7z",
        ".mp4", ".mov", ".mp3", ".wav",
        ".exe", ".dll", ".so",
        ".woff", ".woff2", ".ttf", ".eot"
    }

    lower = path.lower()
    for ext in binary_exts:
        if lower.endswith(ext):
            return None, "skip_binary"

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return None, "error"

    data = r.json()

    # GitHub often includes size for files
    size = data.get("size", 0)
    if size and size > max_size_bytes:
        return None, "skip_large"

    # Content is base64 encoded
    encoded = data.get("content", "")
    if not encoded:
        return None, "error"

    try:
        decoded = base64.b64decode(encoded).decode("utf-8", errors="ignore")
    except Exception:
        return None, "error"

    # Additional safety: if decoded is still huge, skip
    if len(decoded.encode("utf-8", errors="ignore")) > max_size_bytes:
        return None, "skip_large"

    return decoded, "ok"