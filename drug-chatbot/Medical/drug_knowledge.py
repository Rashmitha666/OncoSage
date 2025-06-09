import requests

def groq_search(query):
    api_key = "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"  # Replace with your actual Groq API key
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",  # You can use other available models too
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that answers drug-related questions."},
            {"role": "user", "content": query}
        ],
        "max_tokens": 256,
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            return f"Groq API error: {response.status_code} {response.text}"
    except Exception as e:
        return f"Error querying Groq: {e}"

def is_link_working(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def answer_multi_source(topic, question):
    responses = []

    # ... (get responses from various sources as before) ...

    # Example: filter responses with a 'source_url' field
    filtered_responses = []
    for resp in responses:
        url = resp.get("source_url")
        if url is None or is_link_working(url):
            filtered_responses.append(resp)
        else:
            # Optionally, you can log or add a note about the broken link
            pass

    return {"answers": filtered_responses}
