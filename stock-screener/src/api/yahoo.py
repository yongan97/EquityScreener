"""Cliente para Yahoo Finance (datos históricos y validación)."""

from typing import Optional
from datetime import datetime, timedelta

import yfinance as yf
import pandas as pd
from loguru import logger


class YahooFinanceClient:
    """
    Cliente para Yahoo Finance usando yfinance.
    Útil para datos históricos y validación cruzada.
    """
    
    def __init__(self):
        self._cache: dict = {}
    
    def get_ticker(self, symbol: str) -> yf.Ticker:
        """Obtiene objeto Ticker (con cache)."""
        if symbol not in self._cache:
            self._cache[symbol] = yf.Ticker(symbol)
        return self._cache[symbol]
    
    def get_info(self, symbol: str) -> dict:
        """
        Obtiene información básica del ticker.
        
        Returns:
            Dict con info del ticker o dict vacío si error
        """
        try:
            ticker = self.get_ticker(symbol)
            return ticker.info or {}
        except Exception as e:
            logger.warning(f"Error obteniendo info de {symbol}: {e}")
            return {}
    
    def get_financials(self, symbol: str) -> Optional[pd.DataFrame]:
        """Obtiene estados financieros."""
        try:
            ticker = self.get_ticker(symbol)
            return ticker.financials
        except Exception as e:
            logger.warning(f"Error obteniendo financials de {symbol}: {e}")
            return None
    
    def get_balance_sheet(self, symbol: str) -> Optional[pd.DataFrame]:
        """Obtiene balance sheet."""
        try:
            ticker = self.get_ticker(symbol)
            return ticker.balance_sheet
        except Exception as e:
            logger.warning(f"Error obteniendo balance de {symbol}: {e}")
            return None
    
    def get_history(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> Optional[pd.DataFrame]:
        """
        Obtiene datos históricos de precio.
        
        Args:
            symbol: Símbolo
            period: Período (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Intervalo (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            DataFrame con OHLCV o None si error
        """
        try:
            ticker = self.get_ticker(symbol)
            return ticker.history(period=period, interval=interval)
        except Exception as e:
            logger.warning(f"Error obteniendo historial de {symbol}: {e}")
            return None
    
    def get_key_metrics(self, symbol: str) -> dict:
        """
        Extrae métricas clave del info de Yahoo.
        
        Returns:
            Dict con métricas mapeadas a nuestro formato
        """
        info = self.get_info(symbol)
        
        if not info:
            return {}
        
        return {
            # Valuación
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            "pb_ratio": info.get("priceToBook"),
            "ps_ratio": info.get("priceToSalesTrailing12Months"),
            
            # Crecimiento
            "earnings_growth": info.get("earningsGrowth"),
            "revenue_growth": info.get("revenueGrowth"),
            
            # Rentabilidad
            "roe": info.get("returnOnEquity"),
            "roa": info.get("returnOnAssets"),
            "profit_margin": info.get("profitMargins"),
            "operating_margin": info.get("operatingMargins"),
            "gross_margin": info.get("grossMargins"),
            
            # Liquidez y solvencia
            "current_ratio": info.get("currentRatio"),
            "quick_ratio": info.get("quickRatio"),
            "debt_to_equity": info.get("debtToEquity"),
            
            # Mercado
            "market_cap": info.get("marketCap"),
            "avg_volume": info.get("averageVolume"),
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            
            # Info
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "name": info.get("longName") or info.get("shortName"),
        }
    
    def validate_stock(self, symbol: str, expected_metrics: dict) -> dict:
        """
        Valida métricas de FMP contra Yahoo Finance.
        
        Args:
            symbol: Símbolo a validar
            expected_metrics: Métricas de FMP
        
        Returns:
            Dict con diferencias significativas
        """
        yahoo_metrics = self.get_key_metrics(symbol)
        
        if not yahoo_metrics:
            return {"error": "No se pudo obtener datos de Yahoo"}
        
        differences = {}
        threshold = 0.1  # 10% de diferencia
        
        for key, fmp_value in expected_metrics.items():
            yahoo_value = yahoo_metrics.get(key)
            
            if fmp_value is None or yahoo_value is None:
                continue
            
            if fmp_value == 0:
                continue
            
            diff_pct = abs(fmp_value - yahoo_value) / abs(fmp_value)
            
            if diff_pct > threshold:
                differences[key] = {
                    "fmp": fmp_value,
                    "yahoo": yahoo_value,
                    "diff_pct": round(diff_pct * 100, 2),
                }
        
        return differences
    
    def clear_cache(self):
        """Limpia cache de tickers."""
        self._cache.clear()
