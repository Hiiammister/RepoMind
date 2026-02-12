import requests
def generate(prompt: str, ollama_url: str = "http://localhost:11434/api/v1/ollama/generate"):
    payload = {
        "model": "llama2",
        "prompt": prompt,
        "stream": False,
        "options":{"temperature":0.7}
    }
    try:
        r = requests.post(ollama_url, json=payload, timeout=60)
        if r.status_code!=200:
            return None
        return r.json().get("response","")
    except requests.RequestException as e:
        return None