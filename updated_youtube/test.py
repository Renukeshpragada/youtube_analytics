import requests

def ask_ollama(prompt):
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "tinyllama",
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )
    return r.json()["response"]

print(ask_ollama("Give 3 YouTube video title ideas about AI"))
