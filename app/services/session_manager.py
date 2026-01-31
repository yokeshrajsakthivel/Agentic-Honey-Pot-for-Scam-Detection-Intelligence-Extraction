from typing import Dict, Any
import logging

class SessionManager:
    # In-memory storage with file persistence
    _sessions: Dict[str, Dict[str, Any]] = {}
    FILE_PATH = "sessions.json"
    CLEANUP_INTERVAL = 10 # Cleanup every 10 updates (lightweight)
    SESSION_TTL = 3600 # 1 hour in seconds
    _update_counter = 0

    def __init__(self):
        self._load_from_file()

    def _cleanup_old_sessions(self):
        import time
        current_time = time.time()
        keys_to_delete = []
        
        for sid, data in self._sessions.items():
            last_active = data.get("last_active", 0)
            if current_time - last_active > self.SESSION_TTL:
                keys_to_delete.append(sid)
        
        if keys_to_delete:
            logging.info(f"Cleaning up {len(keys_to_delete)} expired sessions.")
            for key in keys_to_delete:
                del self._sessions[key]
            self._save_to_file()

    def _load_from_file(self):
        import json
        import os
        if os.path.exists(self.FILE_PATH):
            try:
                with open(self.FILE_PATH, "r") as f:
                    self._sessions = json.load(f)
            except Exception as e:
                logging.error(f"Failed to load sessions: {e}")

    def _save_to_file(self):
        import json
        try:
            with open(self.FILE_PATH, "w") as f:
                json.dump(self._sessions, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save sessions: {e}")

    def get_session(self, session_id: str) -> Dict[str, Any]:
        import time
        
        # Periodic cleanup check
        self._update_counter += 1
        if self._update_counter >= self.CLEANUP_INTERVAL:
            self._cleanup_old_sessions()
            self._update_counter = 0

        if session_id not in self._sessions:
            import random
            personas = ["elderly", "student", "busy_mom", "skeptic"]
            selected_persona = random.choice(personas)
            
            self._sessions[session_id] = {
                "message_count": 0,
                "persona": selected_persona,
                "start_time": time.time(),
                "last_active": time.time(),
                "intelligence": {
                    "upi_ids": [],
                    "urls": [],
                    "phone_numbers": [],
                    "account_numbers": [],
                    "ifsc_codes": [],
                    "bank_names": [],
                    "crypto_wallets": [],
                    "person_names": [],
                    "entities": []
                }
            }
            # Log the selected persona for debugging/demo
            logging.info(f"New session {session_id} assigned persona: {selected_persona}")
            self._save_to_file()
        
        # Update last active
        self._sessions[session_id]["last_active"] = time.time()
        return self._sessions[session_id]

    def update_session(self, session_id: str, intelligence_data: Dict[str, list]):
        session = self.get_session(session_id)
        session["message_count"] += 1
        
        # Merge intelligence dynamically
        for key in intelligence_data:
            # Initialize key if not exists (handling migration/schema changes)
            if key not in session["intelligence"]:
                session["intelligence"][key] = []
            
            current = set(session["intelligence"][key])
            new_items = set(intelligence_data[key])
            session["intelligence"][key] = list(current.union(new_items))
        
        self._save_to_file()

session_manager = SessionManager()
