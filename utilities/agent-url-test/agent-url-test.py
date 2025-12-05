import requests

# Replace with your Azure OpenAI endpoint and API key
endpoint = "https://aistudioeytrai8084113755.openai.azure.com/openai/deployments/gpt-4o-1/chat/completions?api-version=2025-01-01-preview"
api_key = "7aa9c239b718451f95a76ff33aeffd9a"

headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}

data = {
    "prompt": "Hello, how are you?",
    "max_tokens": 50,
    "temperature": 0.7,
}

print("Calling Azure OpenAI API...")
response = requests.post(endpoint, headers=headers, json=data)

if response.status_code == 200:
    print("Model response:", response.json())
else:
    print(f"Error while calling API {response.status_code}: {response.text}")