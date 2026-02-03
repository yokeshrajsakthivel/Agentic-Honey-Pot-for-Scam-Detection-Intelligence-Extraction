import requests
import uuid
import sys

# Configuration
# Configuration
PORTS_TO_CHECK = [8000, 8001, 8002, 8003, 8004, 8888]
API_KEY = "hackathon-secret-key"
API_URL = None

def find_active_server():
    print("Searching for active Honeypot server...", end="", flush=True)
    for port in PORTS_TO_CHECK:
        try:
            # Try hitting the health endpoint (fastest check)
            url = f"http://localhost:{port}/health"
            requests.get(url, timeout=0.5)
            print(f" Found on port {port}!")
            return f"http://localhost:{port}/message"
        except requests.exceptions.ConnectionError:
            continue
        except Exception:
            continue
    print(" No server found on common ports.")
    return None

# Auto-detect or use arg
if len(sys.argv) > 1:
    arg = sys.argv[1]
    if arg.startswith("http"):
        API_URL = f"{arg}/message" if not arg.endswith("/message") else arg
    else:
        API_URL = f"http://localhost:{arg}/message"
else:
    API_URL = find_active_server()

if not API_URL:
    print("[Error] Could not find running server. Please specify port: python interactive_tester.py <port>")
    sys.exit(1)

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
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("\n[You]: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input:
                continue

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
