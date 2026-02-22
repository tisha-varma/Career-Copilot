"""
API Key Pool Manager
Rotates through multiple Groq API keys to handle concurrent users.
Auto-skips rate-limited keys and falls back gracefully.
"""

import os
import time
import threading
from pathlib import Path
from typing import Optional


class APIKeyPool:
    """
    Manages a pool of Groq API keys with automatic rotation.
    
    Usage:
        pool = APIKeyPool()
        key = pool.get_key()       # Get the best available key
        pool.mark_rate_limited(key) # Mark a key as temporarily exhausted
    """
    
    def __init__(self):
        self._keys = []
        self._lock = threading.Lock()
        # Track rate-limited keys: {key: cooldown_until_timestamp}
        self._cooldowns = {}
        self._usage_counts = {}
        self._load_keys()
    
    def _load_keys(self):
        """Load API keys from environment variables and keys file."""
        # Primary key from env
        primary = os.environ.get("GROQ_API_KEY", "")
        if primary:
            self._keys.append(primary)
        
        # Additional keys: GROQ_API_KEY_2, GROQ_API_KEY_3, etc.
        for i in range(2, 11):
            key = os.environ.get(f"GROQ_API_KEY_{i}", "")
            if key:
                self._keys.append(key)
        
        # Comma-separated keys in GROQ_API_KEYS
        multi = os.environ.get("GROQ_API_KEYS", "")
        if multi:
            for key in multi.split(","):
                key = key.strip()
                if key and key not in self._keys:
                    self._keys.append(key)
        
        # Load from keys file (one key per line)
        keys_file = Path(__file__).parent / "keys"
        if keys_file.exists():
            try:
                for line in keys_file.read_text(encoding="utf-8").splitlines():
                    key = line.strip()
                    if key and not key.startswith("#") and key not in self._keys:
                        self._keys.append(key)
            except Exception as e:
                print(f"[APIKeyPool] Warning: Could not read keys file: {e}")
        
        # Initialize usage counts
        for key in self._keys:
            self._usage_counts[key] = 0
        
        print(f"[APIKeyPool] Loaded {len(self._keys)} API key(s)")
    
    @property
    def total_keys(self) -> int:
        return len(self._keys)
    
    @property
    def available_keys(self) -> int:
        """Number of keys not currently rate-limited."""
        now = time.time()
        with self._lock:
            return sum(
                1 for k in self._keys
                if self._cooldowns.get(k, 0) <= now
            )
    
    def has_available_key(self) -> bool:
        """Check if any API key is available WITHOUT consuming a rotation."""
        return self.available_keys > 0 or bool(os.environ.get("GROQ_API_KEY"))
    
    def get_key(self) -> Optional[str]:
        """
        Get the best available API key.
        Returns the least-used key that's not on cooldown.
        Returns None if all keys are rate-limited.
        """
        now = time.time()
        
        with self._lock:
            # Filter out keys on cooldown
            available = [
                k for k in self._keys
                if self._cooldowns.get(k, 0) <= now
            ]
            
            if not available:
                # Check if any cooldown is about to expire (within 5 seconds)
                soonest = None
                for k in self._keys:
                    cd = self._cooldowns.get(k, 0)
                    if cd > now and (soonest is None or cd < soonest):
                        soonest = cd
                
                if soonest and (soonest - now) <= 5:
                    # Wait for the soonest key
                    time.sleep(soonest - now + 0.1)
                    return self.get_key()
                
                return None
            
            # Pick the key with lowest usage count (round-robin effect)
            best = min(available, key=lambda k: self._usage_counts.get(k, 0))
            self._usage_counts[best] = self._usage_counts.get(best, 0) + 1
            return best
    
    def mark_rate_limited(self, key: str, cooldown_seconds: int = 60):
        """Mark a key as rate-limited for a cooldown period."""
        with self._lock:
            self._cooldowns[key] = time.time() + cooldown_seconds
            remaining = self.available_keys
            print(f"[APIKeyPool] Key ...{key[-6:]} rate-limited for {cooldown_seconds}s. "
                  f"{remaining}/{self.total_keys} keys available.")
    
    def mark_success(self, key: str):
        """Record a successful API call (resets any pending cooldown)."""
        with self._lock:
            if key in self._cooldowns and self._cooldowns[key] > time.time():
                # Key recovered early
                del self._cooldowns[key]
    
    def get_stats(self) -> dict:
        """Get pool statistics."""
        now = time.time()
        with self._lock:
            return {
                "total_keys": self.total_keys,
                "available_keys": sum(1 for k in self._keys if self._cooldowns.get(k, 0) <= now),
                "rate_limited": sum(1 for k in self._keys if self._cooldowns.get(k, 0) > now),
                "total_calls": sum(self._usage_counts.values()),
            }


# Singleton instance
_pool = None

def get_api_pool() -> APIKeyPool:
    """Get the global API key pool singleton."""
    global _pool
    if _pool is None:
        _pool = APIKeyPool()
    return _pool
