import os
import logging
from supabase import create_client, Client
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Try to import streamlit for secrets fallback
try:
    import streamlit as st
except ImportError:
    st = None

load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseManager:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        # Fallback to streamlit secrets if available
        if not url or not key:
            if st is not None:
                try:
                    url = url or st.secrets.get("SUPABASE_URL")
                    key = key or st.secrets.get("SUPABASE_KEY")
                except Exception:
                    pass

        if url and key:
            try:
                self.client: Optional[Client] = create_client(url, key)
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.client = None
        else:
            self.client = None
            logger.warning("Supabase credentials not found. Supabase operations will fail.")

    def _ensure_client(self):
        if self.client is None:
            raise RuntimeError("Supabase client is not initialized. Please set SUPABASE_URL and SUPABASE_KEY in your environment or Streamlit secrets.")

    def sign_up(self, email, password):
        self._ensure_client()
        return self.client.auth.sign_up({"email": email, "password": password})

    def login(self, email, password):
        self._ensure_client()
        return self.client.auth.sign_in_with_password({"email": email, "password": password})

    def logout(self):
        self._ensure_client()
        return self.client.auth.sign_out()

    def get_user(self):
        self._ensure_client()
        return self.client.auth.get_user()

    def create_conversation(self, user_id: str, title: str) -> Dict[str, Any]:
        self._ensure_client()
        data = self.client.table("conversations").insert({
            "user_id": user_id,
            "title": title
        }).execute()
        return data.data[0]

    def get_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        self._ensure_client()
        try:
            data = self.client.table("conversations").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return data.data
        except Exception as e:
            logger.error(f"Error fetching conversations: {e}")
            return []

    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        self._ensure_client()
        try:
            data = self.client.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", desc=False).execute()
            messages = data.data
            for m in messages:
                if 'extras' in m:
                    if isinstance(m['extras'], str):
                        try:
                            import json
                            m['extras'] = json.loads(m['extras'])
                        except:
                            m['extras'] = {}
                    elif m['extras'] is None:
                        m['extras'] = {}
                else:
                    m['extras'] = {}
            return messages
        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
            return []

    def save_message(self, conversation_id: str, role: str, content: str, extras: Optional[Dict] = None):
        self._ensure_client()
        try:
            self.client.table("messages").insert({
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "extras": extras or {}
            }).execute()
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            raise e

    def update_conversation_title(self, conversation_id: str, title: str):
        self._ensure_client()
        self.client.table("conversations").update({"title": title}).eq("id", conversation_id).execute()

    def upload_asset(self, bucket_name: str, file_path: str, file_bytes: bytes) -> str:
        """Uploads a file to Supabase Storage and returns the public URL."""
        self._ensure_client()
        res = self.client.storage.from_(bucket_name).upload(file_path, file_bytes, {"content-type": "image/png"})
        return self.client.storage.from_(bucket_name).get_public_url(file_path)

supabase_mgr = SupabaseManager()
