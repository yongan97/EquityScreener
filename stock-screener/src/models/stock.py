"""Modelos de datos para el screener."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class StockMetrics:
    """Métricas financieras de una acción."""
    
    # Valuación
    pe_ratio: Optional[float] = None
    peg_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    
    # Crecimiento
    eps_growth_5y: Optional[float] = None
    revenue_growth_5y: Optional[float] = None
    eps_growth_ttm: Optional[float] = None
    
    # Rentabilidad
    roe: Optional[float] = None
    roa: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    
    # Liquidez
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    
    # Solvencia
    debt_to_equity: Optional[float] = None
    interest_coverage: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convierte a diccionario excluyendo valores None."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class Stock:
    """Representa una acción con sus datos y métricas."""
    
    symbol: str
    name: str
    exchange: str
    sector: str
    industry: str
    
    # Datos de mercado
    price: float
    market_cap: float
    avg_volume: int
    
    # Métricas calculadas
    metrics: StockMetrics = field(default_factory=StockMetrics)
    
    # Scoring
    score: Optional[float] = None
    score_breakdown: dict = field(default_factory=dict)
    
    # Metadata
    last_updated: datetime = field(default_factory=datetime.now)
    data_source: str = "fmp"
    
    def passes_filter(self, criteria: dict) -> bool:
        """Verifica si pasa un criterio específico."""
        for key, bounds in criteria.items():
            value = getattr(self.metrics, key, None)
            if value is None:
                continue
            if bounds.get("min") is not None and value < bounds["min"]:
                return False
            if bounds.get("max") is not None and value > bounds["max"]:
                return False
        return True
    
    def to_dict(self) -> dict:
        """Serializa a diccionario."""
        return {
            "symbol": self.symbol,
            "name": self.name,
            "exchange": self.exchange,
            "sector": self.sector,
            "industry": self.industry,
            "price": self.price,
            "market_cap": self.market_cap,
            "avg_volume": self.avg_volume,
            "metrics": self.metrics.to_dict(),
            "score": self.score,
            "score_breakdown": self.score_breakdown,
            "last_updated": self.last_updated.isoformat(),
            "data_source": self.data_source,
        }


@dataclass
class ScreenerResult:
    """Resultado de una ejecución del screener."""
    
    timestamp: datetime
    config_name: str
    total_scanned: int
    total_matches: int
    stocks: list[Stock]
    execution_time_seconds: float
    errors: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Serializa a diccionario."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "config_name": self.config_name,
            "total_scanned": self.total_scanned,
            "total_matches": self.total_matches,
            "stocks": [s.to_dict() for s in self.stocks],
            "execution_time_seconds": self.execution_time_seconds,
            "errors": self.errors,
        }
