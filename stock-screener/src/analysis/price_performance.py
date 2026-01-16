"""Módulo para obtener variaciones de precio desde Yahoo Finance."""

from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

import yfinance as yf
from loguru import logger


@dataclass
class PricePerformance:
    """Variaciones de precio en diferentes períodos."""

    perf_1d: Optional[float] = None
    perf_1w: Optional[float] = None
    perf_1m: Optional[float] = None
    perf_ytd: Optional[float] = None
    perf_52w: Optional[float] = None

    def to_dict(self) -> dict:
        """Convierte a diccionario."""
        return {
            "perf_1d": self.perf_1d,
            "perf_1w": self.perf_1w,
            "perf_1m": self.perf_1m,
            "perf_ytd": self.perf_ytd,
            "perf_52w": self.perf_52w,
        }


def get_price_performance(symbol: str) -> PricePerformance:
    """
    Obtiene variaciones de precio para un símbolo.

    Args:
        symbol: Símbolo del ticker (ej: AAPL)

    Returns:
        PricePerformance con variaciones 1D, 1W, 1M, YTD, 52W
    """
    perf = PricePerformance()

    try:
        ticker = yf.Ticker(symbol)

        # Obtener historial de 1 año + buffer
        history = ticker.history(period="1y", interval="1d")

        if history.empty:
            logger.warning(f"No hay historial de precios para {symbol}")
            return perf

        # Precio actual (último cierre)
        current_price = history["Close"].iloc[-1]

        # 1 día: comparar con el cierre anterior
        if len(history) >= 2:
            prev_close = history["Close"].iloc[-2]
            perf.perf_1d = (current_price - prev_close) / prev_close

        # 1 semana: buscar el precio de hace ~5 días de trading
        if len(history) >= 6:
            week_ago_price = history["Close"].iloc[-6]
            perf.perf_1w = (current_price - week_ago_price) / week_ago_price

        # 1 mes: buscar el precio de hace ~21 días de trading
        if len(history) >= 22:
            month_ago_price = history["Close"].iloc[-22]
            perf.perf_1m = (current_price - month_ago_price) / month_ago_price

        # YTD: desde inicio del año actual
        today = datetime.now()
        year_start = datetime(today.year, 1, 1)
        ytd_data = history[history.index >= year_start.strftime("%Y-%m-%d")]
        if len(ytd_data) >= 1:
            # Buscar el primer precio disponible del año
            year_start_price = ytd_data["Close"].iloc[0]
            perf.perf_ytd = (current_price - year_start_price) / year_start_price

        # 52 semanas: comparar con hace ~252 días de trading (o el más antiguo disponible)
        if len(history) >= 252:
            year_ago_price = history["Close"].iloc[0]
            perf.perf_52w = (current_price - year_ago_price) / year_ago_price
        elif len(history) >= 100:
            # Si no hay 252 días, usar el más antiguo disponible
            oldest_price = history["Close"].iloc[0]
            perf.perf_52w = (current_price - oldest_price) / oldest_price

        logger.debug(
            f"{symbol} performance: 1D={perf.perf_1d:.2%} 1W={perf.perf_1w:.2%} "
            f"1M={perf.perf_1m:.2%} YTD={perf.perf_ytd:.2%} 52W={perf.perf_52w:.2%}"
            if all([perf.perf_1d, perf.perf_1w, perf.perf_1m, perf.perf_ytd, perf.perf_52w])
            else f"{symbol} performance calculated (some values may be None)"
        )

    except Exception as e:
        logger.warning(f"Error obteniendo performance de {symbol}: {e}")

    return perf


def get_batch_performance(symbols: list[str]) -> dict[str, PricePerformance]:
    """
    Obtiene performance para múltiples símbolos.

    Args:
        symbols: Lista de símbolos

    Returns:
        Diccionario symbol -> PricePerformance
    """
    results = {}

    for symbol in symbols:
        results[symbol] = get_price_performance(symbol)

    return results
