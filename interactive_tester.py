import requests
import uuid
import sys

# Configuration
API_URL = "http://localhost:8002/message"
API_KEY = "hackathon-secret-key"

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
                "message": user_input,
                "conversationHistory": conversation_history,
                "metadata": {"source": "manual_cli"}
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
                conversation_history.append({"role": "user", "content": user_input})
                conversation_history.append({"role": "assistant", "content": data["reply"]})
                
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
