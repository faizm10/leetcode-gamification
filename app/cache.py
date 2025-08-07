import redis
import json
from typing import Optional, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.ttl = settings.CACHE_TTL
    
    def get_prediction(self, trip_id: str, stop_id: str, departure_time: str, date: str) -> Optional[Dict[str, Any]]:
        """Get cached prediction if available."""
        cache_key = f"prediction:{trip_id}:{stop_id}:{departure_time}:{date}"
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for {cache_key}")
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
        return None
    
    def set_prediction(self, trip_id: str, stop_id: str, departure_time: str, date: str, 
                      prediction_data: Dict[str, Any]) -> bool:
        """Cache prediction result."""
        cache_key = f"prediction:{trip_id}:{stop_id}:{departure_time}:{date}"
        try:
            self.redis_client.setex(
                cache_key,
                self.ttl,
                json.dumps(prediction_data)
            )
            logger.info(f"Cached prediction for {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    def invalidate_predictions(self, trip_id: Optional[str] = None, stop_id: Optional[str] = None):
        """Invalidate cached predictions."""
        try:
            if trip_id and stop_id:
                pattern = f"prediction:{trip_id}:{stop_id}:*"
            elif trip_id:
                pattern = f"prediction:{trip_id}:*"
            elif stop_id:
                pattern = f"prediction:*:{stop_id}:*"
            else:
                pattern = "prediction:*"
            
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cached predictions")
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            info = self.redis_client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'total_commands_processed': info.get('total_commands_processed', 0)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}


# Global cache manager instance
cache_manager = CacheManager()
