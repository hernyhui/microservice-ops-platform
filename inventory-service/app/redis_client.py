import redis
from .config import settings

REDIS_AVAILABLE = False
redis_client = None

try:
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True,
        socket_timeout=2,
        socket_connect_timeout=2,
    )
    redis_client.ping()
    REDIS_AVAILABLE = True
    print("✅ Connected to real Redis server")
except Exception as e:
    print(f"⚠️ Real Redis not available: {e}")
    print("🔄 Using fakeredis as fallback...")
    try:
        import fakeredis
        redis_client = fakeredis.FakeRedis(decode_responses=True)
        redis_client.ping()
        REDIS_AVAILABLE = True
        print("✅ Connected to fakeredis (in-memory)")
    except Exception as fe:
        print(f"❌ fakeredis also failed: {fe}")
        redis_client = None
        REDIS_AVAILABLE = False

INVENTORY_KEY_PREFIX = "inventory:stock:"


def get_stock_from_cache(product_id: str) -> int | None:
    if not REDIS_AVAILABLE:
        return None
    try:
        key = f"{INVENTORY_KEY_PREFIX}{product_id}"
        value = redis_client.get(key)
        if value is not None:
            return int(value)
        return None
    except Exception:
        return None


def set_stock_to_cache(product_id: str, stock: int, expire_seconds: int = 300):
    if not REDIS_AVAILABLE:
        return
    try:
        key = f"{INVENTORY_KEY_PREFIX}{product_id}"
        redis_client.setex(key, expire_seconds, str(stock))
    except Exception:
        pass


def decrement_stock_in_cache(product_id: str, quantity: int) -> int | None:
    if not REDIS_AVAILABLE:
        return None
    try:
        key = f"{INVENTORY_KEY_PREFIX}{product_id}"
        return redis_client.decrby(key, quantity)
    except Exception:
        return None


def delete_stock_cache(product_id: str):
    if not REDIS_AVAILABLE:
        return
    try:
        key = f"{INVENTORY_KEY_PREFIX}{product_id}"
        redis_client.delete(key)
    except Exception:
        pass
