import requests

def research(query):
    url = "https://chat-api.you.com/research"

    payload = {
        "query": query,
        "chat_id": "3c90c3cc-0d44-4b50-8888-8dd25736052a"
    }
    headers = {
        "X-API-Key": "12b62109-18fd-4b94-815d-6cd1682fdb62<__>1QrGC6ETU8N2v5f4mk3YJDGl",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    return response.text