import requests
import uuid
import sys

# Configuration
# Configuration
import argparse

# Configuration
DEFAULT_PORTS = [8000, 8001, 8002, 8003, 8004, 8888]
DEFAULT_KEY = "hackathon-secret-key"

def find_active_server():
    print("Searching for active Honeypot server...", end="", flush=True)
    for port in DEFAULT_PORTS:
        try:
            url = f"http://localhost:{port}/health"
            requests.get(url, timeout=0.5)
            print(f" Found on port {port}!")
            return f"http://localhost:{port}/message"
        except Exception:
            continue
    print(" No server found on common ports.")
    return None

# Parse Arguments
parser = argparse.ArgumentParser(description="Agentic Honeypot Interactive Tester")
parser.add_argument("--url", type=str, help="Full URL to the /message endpoint")
parser.add_argument("--key", type=str, default=DEFAULT_KEY, help="API Key")
args = parser.parse_args()

API_URL = args.url
API_KEY = args.key

if not API_URL:
    # Try auto-discovery if no URL provided
    API_URL = find_active_server()

if not API_URL:
    print("[Error] Could not find running server. Please specify --url.")
    sys.exit(1)

# Append /message if missing (convenience)
if not API_URL.endswith("/message") and not API_URL.endswith("/"):
     API_URL += "/message"


def main():
    print("="*50)
    print("   Agentic Honeypot - Interactive Scammer Test")
    print("="*50)
    print("You are acting as the SCAMMER.")
    print("The AI (Grandma Betsy) will reply to you.")
    print("Type 'exit' or 'quit' to stop.")
    print("-" * 50)

    # Generate a random session ID for this test run
    session_id = str(uuid.uuid4())[:8]
    print(f"Session ID: {session_id}")
    
    # Trigger first empty message to initialize session and get persona
    try:
        init_payload = {
            "sessionId": session_id,
            "message": { "sender": "scammer", "text": "init_ping", "timestamp": 123 },
            "conversationHistory": [], 
            "metadata": {}
        }
        # We assume the first response will initialize the session.
        # But a cleaner way is to just let the first user message trigger it.
        # Let's inspect the logs or valid response after first message.
    except:
        pass
    
    print("(Persona will be assigned automatically by the server. Sending first message...)\n")
    print("-" * 50)
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("\n[You]: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input:
                continue

            # ... (prepare payload) ...


            # Prepare Payload
            payload = {
                "sessionId": session_id,
                "message": {
                    "sender": "scammer",
                    "text": user_input,
                    "timestamp": 1234567890
                },
                "conversationHistory": conversation_history,
                "metadata": {
                    "channel": "manual_cli",
                    "language": "en"
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": API_KEY
            }

            # Send Request
            print("Sending...", end="\r")
            try:
                response = requests.post(API_URL, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                # Update History (Client-side tracking for simulation)
                # Matches strict schema: sender + text
                conversation_history.append({"sender": "scammer", "text": user_input, "timestamp": 1234567890})
                conversation_history.append({"sender": "user", "text": data["reply"], "timestamp": 1234567899})
                
                # Display Response
                print(f"[Grandma]: {data['reply']}")
                
                # Display Metadata
                scam_status = "SCAM DETECTED!" if data['scam_detected'] else "Safe"
                print(f"   >>> System Analysis: {scam_status} (Score: {data['confidence_score']:.2f})")

            except requests.exceptions.ConnectionError:
                print("\n[Error]: Could not connect to the API. Is the server running on port 8001?")
            except Exception as e:
                print(f"\n[Error]: {e}")
                
        except KeyboardInterrupt:
            break
            
    print("\nTest finished.")

if __name__ == "__main__":
    main()
