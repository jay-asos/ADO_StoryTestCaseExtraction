"""
Token Usage Statistics Manager
Tracks and persists token usage data to show TOON optimization impact
"""

import json
import os
import logging
from datetime import datetime
from typing import List, Dict
from src.models import TokenUsageRecord, TokenUsageStats

logger = logging.getLogger(__name__)


class TokenStatsManager:
    """Manages token usage statistics storage and retrieval"""
    
    def __init__(self, stats_file: str = "token_usage_stats.json"):
        """Initialize the token stats manager"""
        self.stats_file = stats_file
        self.stats: TokenUsageStats = self._load_stats()
    
    def _load_stats(self) -> TokenUsageStats:
        """Load statistics from file or create new if not exists"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    # Convert record dicts to TokenUsageRecord objects
                    if 'records' in data:
                        data['records'] = [
                            TokenUsageRecord(**record) for record in data['records']
                        ]
                    return TokenUsageStats(**data)
            except Exception as e:
                logger.error(f"Failed to load token stats from {self.stats_file}: {e}")
                return TokenUsageStats()
        return TokenUsageStats()
    
    def _save_stats(self):
        """Save statistics to file"""
        try:
            # Convert to dict for JSON serialization
            data = self.stats.dict()
            # Convert datetime objects to ISO format strings
            if 'last_updated' in data:
                data['last_updated'] = data['last_updated'].isoformat()
            if 'records' in data:
                for record in data['records']:
                    if 'timestamp' in record:
                        record['timestamp'] = record['timestamp'].isoformat()
            
            with open(self.stats_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved token stats to {self.stats_file}")
        except Exception as e:
            logger.error(f"Failed to save token stats to {self.stats_file}: {e}")
    
    def add_record(self, story_id: str, story_title: str, estimated_tokens: int, 
                   actual_tokens: int, tokens_saved: int, toon_enabled: bool,
                   api_call_type: str = "test_case_extraction"):
        """Add a new token usage record"""
        record = TokenUsageRecord(
            timestamp=datetime.now(),
            story_id=story_id,
            story_title=story_title,
            estimated_tokens=estimated_tokens,
            actual_tokens=actual_tokens,
            tokens_saved=tokens_saved,
            toon_enabled=toon_enabled,
            api_call_type=api_call_type
        )
        
        self.stats.records.append(record)
        self.stats.total_api_calls += 1
        self.stats.total_estimated_tokens += estimated_tokens
        self.stats.total_actual_tokens += actual_tokens
        self.stats.total_tokens_saved += tokens_saved
        
        # Calculate average savings percentage
        if self.stats.total_estimated_tokens > 0:
            self.stats.average_tokens_saved_percentage = (
                (self.stats.total_tokens_saved / self.stats.total_estimated_tokens) * 100
            )
        
        self.stats.last_updated = datetime.now()
        
        # Keep only last 100 records to avoid file bloat
        if len(self.stats.records) > 100:
            self.stats.records = self.stats.records[-100:]
        
        self._save_stats()
        
        logger.info(f"Added token usage record: Story={story_id}, "
                   f"Estimated={estimated_tokens}, Actual={actual_tokens}, "
                   f"Saved={tokens_saved}, TOON={'ON' if toon_enabled else 'OFF'}")
    
    def get_stats(self) -> TokenUsageStats:
        """Get current statistics"""
        return self.stats
    
    def get_recent_records(self, limit: int = 50) -> List[TokenUsageRecord]:
        """Get recent token usage records"""
        return self.stats.records[-limit:] if self.stats.records else []
    
    def get_summary(self) -> Dict:
        """Get a summary of token usage statistics"""
        return {
            'total_api_calls': self.stats.total_api_calls,
            'total_estimated_tokens': self.stats.total_estimated_tokens,
            'total_actual_tokens': self.stats.total_actual_tokens,
            'total_tokens_saved': self.stats.total_tokens_saved,
            'average_savings_percentage': round(self.stats.average_tokens_saved_percentage, 2),
            'last_updated': self.stats.last_updated.isoformat() if self.stats.last_updated else None
        }
    
    def clear_stats(self):
        """Clear all statistics"""
        self.stats = TokenUsageStats()
        self._save_stats()
        logger.info("Cleared all token usage statistics")


# Global instance
_token_stats_manager = None


def get_token_stats_manager() -> TokenStatsManager:
    """Get or create the global token stats manager instance"""
    global _token_stats_manager
    if _token_stats_manager is None:
        _token_stats_manager = TokenStatsManager()
    return _token_stats_manager
