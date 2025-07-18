import requests
import json

headers = {
    'Authorization': 'Bearer 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',
    'Content-Type': 'application/json'
}

payload = {
    'model': 'llama-3.1-8b-instant',
    'messages': [
        {'role': 'system', 'content': 'You are an IT support specialist.'},
        {'role': 'user', 'content': 'which ram is best to use in my laptop?'}
    ],
    'max_tokens': 150,
    'temperature': 0.1
}

response = requests.post('https://api.groq.com/openai/v1/chat/completions', 
                        headers=headers, json=payload, timeout=30)

print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Response: {data["choices"][0]["message"]["content"]}')
else:
    print(f'Error: {response.text}')
