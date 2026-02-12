from urllib.parse import urlparse
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