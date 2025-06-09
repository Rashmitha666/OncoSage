import requests
import os

def get_groq_answer(question):
    """
    Get an answer from Groq's AI model.
    
    Args:
        question (str): The question to ask
        
    Returns:
        dict: A structured response with answer and source information
    """
    api_key = os.getenv("GROQ_API_KEY")  # Get API key from environment variable
    if not api_key:
        return {
            "answer": "Groq API key not configured. Please set GROQ_API_KEY environment variable.",
            "source": "Groq AI",
            "source_url": "https://console.groq.com"
        }
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful medical assistant that provides accurate, evidence-based information about drugs, diseases, and medical conditions. Always cite your sources when possible."
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"].strip()
            return {
                "answer": answer,
                "source": "Groq AI",
                "source_url": "https://console.groq.com"
            }
        else:
            return {
                "answer": f"Error from Groq API: {response.status_code}",
                "source": "Groq AI",
                "source_url": "https://console.groq.com"
            }
    except Exception as e:
        return {
            "answer": f"Error querying Groq: {str(e)}",
            "source": "Groq AI",
            "source_url": "https://console.groq.com"
        } 