"""Sistema de cache para reducir llamadas a APIs."""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Any

from loguru import logger


class CacheManager:
    """
    Manager de cache usando SQLite.
    Almacena respuestas de API con TTL configurable.
    """
    
    def __init__(
        self,
        db_path: str = "data/cache.db",
        default_ttl_hours: int = 24,
    ):
        """
        Inicializa el cache.
        
        Args:
            db_path: Ruta a la base de datos SQLite
            default_ttl_hours: TTL default en horas
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.default_ttl = timedelta(hours=default_ttl_hours)
        
        self._init_db()
    
    def _init_db(self):
        """Inicializa la base de datos."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    source TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires 
                ON cache(expires_at)
            """)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene valor del cache si existe y no expiró.
        
        Args:
            key: Clave del cache
        
        Returns:
            Valor deserializado o None si no existe/expiró
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value, expires_at FROM cache WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            value, expires_at = row
            expires = datetime.fromisoformat(expires_at)
            
            if datetime.now() > expires:
                # Expirado, eliminar
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                return None
            
            return json.loads(value)
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None,
        source: str = "unknown",
    ):
        """
        Guarda valor en cache.
        
        Args:
            key: Clave del cache
            value: Valor a guardar (debe ser serializable a JSON)
            ttl: Time-to-live (usa default si no se especifica)
            source: Fuente del dato (para debugging)
        """
        ttl = ttl or self.default_ttl
        now = datetime.now()
        expires = now + ttl
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO cache (key, value, created_at, expires_at, source)
                VALUES (?, ?, ?, ?, ?)
            """, (key, json.dumps(value), now.isoformat(), expires.isoformat(), source))
    
    def delete(self, key: str):
        """Elimina entrada del cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))
    
    def clear(self):
        """Limpia todo el cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache")
        logger.info("Cache limpiado")
    
    def cleanup_expired(self) -> int:
        """
        Elimina entradas expiradas.
        
        Returns:
            Número de entradas eliminadas
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM cache WHERE expires_at < ?",
                (datetime.now().isoformat(),)
            )
            deleted = cursor.rowcount
        
        if deleted > 0:
            logger.info(f"Cache cleanup: {deleted} entradas eliminadas")
        
        return deleted
    
    def stats(self) -> dict:
        """Obtiene estadísticas del cache."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
            
            expired = conn.execute(
                "SELECT COUNT(*) FROM cache WHERE expires_at < ?",
                (datetime.now().isoformat(),)
            ).fetchone()[0]
            
            by_source = dict(conn.execute(
                "SELECT source, COUNT(*) FROM cache GROUP BY source"
            ).fetchall())
        
        return {
            "total_entries": total,
            "expired_entries": expired,
            "active_entries": total - expired,
            "by_source": by_source,
        }


# Funciones helper para uso con decorador
_default_cache: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """Obtiene instancia global del cache."""
    global _default_cache
    if _default_cache is None:
        _default_cache = CacheManager()
    return _default_cache


def cached(key_prefix: str, ttl_hours: int = 24):
    """
    Decorador para cachear resultados de funciones.
    
    Usage:
        @cached("fmp_ratios", ttl_hours=12)
        def get_ratios(symbol: str) -> dict:
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Construir key desde argumentos
            key_parts = [key_prefix] + [str(a) for a in args]
            key = ":".join(key_parts)
            
            cache = get_cache()
            
            # Intentar obtener del cache
            cached_value = cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_value
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            cache.set(key, result, timedelta(hours=ttl_hours), source=key_prefix)
            logger.debug(f"Cache miss, stored: {key}")
            
            return result
        
        return wrapper
    return decorator
