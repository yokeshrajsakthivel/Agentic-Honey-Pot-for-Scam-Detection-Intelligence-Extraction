import requests
import json
import time

URL = "http://localhost:8002/message"
HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": "hackathon-secret-key"
}
PAYLOAD = {
    "sessionId": "test-session-001",
    "message": "Hello, I am calling from the bank. You need to transfer money to this secure UPI ID: scammer@bank immediately or your account will be blocked.",
    "conversationHistory": [],
    "metadata": {}
}

def test_api():
    print(f"Testing API at {URL}...")
    try:
        start = time.time()
        response = requests.post(URL, json=PAYLOAD, headers=HEADERS)
        elapsed = (time.time() - start) * 1000
        
        print(f"Status Code: {response.status_code}")
        print(f"Time Taken: {elapsed:.2f}ms")
        
        if response.status_code == 200:
            print("Response JSON:")
            print(json.dumps(response.json(), indent=2))
        else:
            print("Error Response:")
            print(response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_api()
