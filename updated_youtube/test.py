import os
import streamlit as st
import requests

GROQ_API_KEY = st.secrets["groq"]["GROQ_API_KEY"]
GROQ_URL = st.secrets["groq"]["GROQ_URL"]
def ask_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {"role": "system", "content": "You are a helpful YouTube content strategist."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }

    response = requests.post(
        GROQ_URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    print(ask_groq("Give 3 YouTube video title ideas about filmymoji"))
