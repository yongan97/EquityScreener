"""Cliente para Financial Modeling Prep API."""

import os
import time
from typing import Optional
from datetime import datetime

import httpx
from loguru import logger

from src.models.stock import Stock, StockMetrics


class FMPClient:
    """Cliente para interactuar con Financial Modeling Prep API."""

    BASE_URL = "https://financialmodelingprep.com/api/v3"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FMP_API_KEY")
        if not self.api_key:
            raise ValueError("FMP_API_KEY no configurada")
        self.client = httpx.Client(timeout=30)
        self._request_count = 0
        self._last_request_time = 0

    def _request(self, endpoint: str, params: dict = None) -> dict | list:
        """Realiza request a la API con rate limiting."""
        params = params or {}
        params["apikey"] = self.api_key

        # Rate limiting: max 5 requests per second for free tier
        now = time.time()
        if now - self._last_request_time < 0.25:
            time.sleep(0.25 - (now - self._last_request_time))

        url = f"{self.BASE_URL}/{endpoint}"
        logger.debug(f"GET {endpoint}")

        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            self._request_count += 1
            self._last_request_time = time.time()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                logger.warning(f"403 Forbidden for {endpoint} - endpoint may require paid plan")
                return []
            raise

    def get_stock_list(self) -> list[dict]:
        """Obtiene lista de todas las acciones disponibles (endpoint gratuito)."""
        return self._request("stock/list")

    def get_tradeable_stocks(self) -> list[dict]:
        """Obtiene lista de acciones activamente tradeable (endpoint gratuito)."""
        return self._request("available-traded/list")

    def get_quotes_batch(self, symbols: list[str]) -> list[dict]:
        """
        Obtiene cotizaciones para múltiples símbolos (endpoint gratuito).

        Args:
            symbols: Lista de símbolos (máximo ~50 por request)

        Returns:
            Lista de cotizaciones
        """
        if not symbols:
            return []
        symbols_str = ",".join(symbols[:50])  # Limitar a 50 por request
        return self._request(f"quote/{symbols_str}")

    def screen_stocks_free(
        self,
        market_cap_min: float = 2e9,
        price_min: float = 5,
        volume_min: int = 300000,
        exchange: list[str] = None,
    ) -> list[dict]:
        """
        Versión gratuita del screener usando endpoints públicos.

        Obtiene lista de stocks y filtra localmente.
        """
        logger.info("Usando método de screening gratuito...")

        # 1. Obtener lista de stocks tradeables
        logger.info("Obteniendo lista de stocks...")
        all_stocks = self.get_tradeable_stocks()

        if not all_stocks:
            logger.warning("No se pudo obtener lista de stocks, intentando alternativa...")
            all_stocks = self.get_stock_list()

        if not all_stocks:
            logger.error("No se pudo obtener lista de stocks")
            return []

        logger.info(f"Total stocks disponibles: {len(all_stocks)}")

        # 2. Filtrar por exchange
        exchanges = exchange or ["NYSE", "NASDAQ"]
        filtered = [
            s for s in all_stocks
            if s.get("exchangeShortName") in exchanges
            and s.get("type") == "stock"
        ]
        logger.info(f"Stocks en exchanges {exchanges}: {len(filtered)}")

        # 3. Obtener cotizaciones en batches para filtrar por precio/market cap
        candidates = []
        symbols = [s["symbol"] for s in filtered]

        logger.info(f"Obteniendo cotizaciones para {len(symbols)} símbolos...")
        batch_size = 50

        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            quotes = self.get_quotes_batch(batch)

            for quote in quotes:
                try:
                    mkt_cap = quote.get("marketCap") or 0
                    price = quote.get("price") or 0
                    volume = quote.get("avgVolume") or quote.get("volume") or 0

                    if (mkt_cap >= market_cap_min and
                        price >= price_min and
                        volume >= volume_min):
                        candidates.append(quote)
                except (TypeError, ValueError):
                    continue

            if (i + batch_size) % 500 == 0:
                logger.info(f"Procesados {i + batch_size}/{len(symbols)} símbolos, {len(candidates)} candidatos...")

        logger.info(f"Candidatos después de filtros básicos: {len(candidates)}")
        return candidates

    def screen_stocks(
        self,
        market_cap_min: float = 2e9,
        price_min: float = 5,
        volume_min: int = 300000,
        exchange: list[str] = None,
    ) -> list[dict]:
        """
        Obtiene lista de stocks que pasan filtros básicos.
        Intenta usar endpoint premium, si falla usa versión gratuita.
        """
        # Intentar endpoint premium primero
        try:
            params = {
                "marketCapMoreThan": int(market_cap_min),
                "priceMoreThan": price_min,
                "volumeMoreThan": volume_min,
                "isActivelyTrading": "true",
                "isEtf": "false",
                "isFund": "false",
            }

            if exchange:
                params["exchange"] = ",".join(exchange)

            result = self._request("stock-screener", params)
            if result:
                return result
        except Exception as e:
            logger.warning(f"Endpoint premium no disponible: {e}")

        # Fallback a versión gratuita
        return self.screen_stocks_free(market_cap_min, price_min, volume_min, exchange)
    
    def get_ratios(self, symbol: str) -> dict:
        """Obtiene ratios financieros de un símbolo."""
        data = self._request(f"ratios/{symbol}")
        return data[0] if data else {}
    
    def get_key_metrics(self, symbol: str) -> dict:
        """Obtiene métricas clave de un símbolo."""
        data = self._request(f"key-metrics/{symbol}")
        return data[0] if data else {}
    
    def get_financial_growth(self, symbol: str) -> dict:
        """Obtiene métricas de crecimiento."""
        data = self._request(f"financial-growth/{symbol}")
        return data[0] if data else {}
    
    def get_company_profile(self, symbol: str) -> dict:
        """Obtiene perfil de la compañía."""
        data = self._request(f"profile/{symbol}")
        return data[0] if data else {}
    
    def build_stock(self, symbol: str, basic_data: dict = None) -> Stock:
        """
        Construye objeto Stock completo con todas las métricas.

        Args:
            symbol: Símbolo de la acción
            basic_data: Datos básicos del screener o quote (opcional)

        Returns:
            Stock con métricas completas
        """
        # Obtener profile para sector/industry si no están en basic_data
        profile = None
        if basic_data and not basic_data.get("sector"):
            profile = self.get_company_profile(symbol)
        elif not basic_data:
            basic_data = self.get_company_profile(symbol)
            profile = basic_data

        # Merge profile data if available
        if profile:
            basic_data = {**basic_data, **profile} if basic_data else profile

        # Obtener métricas adicionales
        ratios = self.get_ratios(symbol)
        key_metrics = self.get_key_metrics(symbol)
        growth = self.get_financial_growth(symbol)

        # Construir métricas
        metrics = StockMetrics(
            # Valuación - handle both quote and profile formats
            pe_ratio=basic_data.get("pe") or ratios.get("priceEarningsRatio"),
            peg_ratio=ratios.get("priceEarningsToGrowthRatio"),
            pb_ratio=ratios.get("priceToBookRatio"),
            ps_ratio=ratios.get("priceToSalesRatio"),

            # Crecimiento
            eps_growth_5y=growth.get("fiveYEpsGrowthPerShare"),
            revenue_growth_5y=growth.get("fiveYRevenueGrowthPerShare"),

            # Rentabilidad
            roe=ratios.get("returnOnEquity"),
            roa=ratios.get("returnOnAssets"),
            gross_margin=ratios.get("grossProfitMargin"),
            operating_margin=ratios.get("operatingProfitMargin"),
            net_margin=ratios.get("netProfitMargin"),

            # Liquidez
            current_ratio=ratios.get("currentRatio"),
            quick_ratio=ratios.get("quickRatio"),

            # Solvencia
            debt_to_equity=ratios.get("debtEquityRatio"),
            interest_coverage=ratios.get("interestCoverage"),
        )

        # Handle both quote format (marketCap, avgVolume) and profile format (mktCap, volAvg)
        return Stock(
            symbol=symbol,
            name=basic_data.get("companyName") or basic_data.get("name", ""),
            exchange=basic_data.get("exchangeShortName") or basic_data.get("exchange", ""),
            sector=basic_data.get("sector", ""),
            industry=basic_data.get("industry", ""),
            price=basic_data.get("price", 0),
            market_cap=basic_data.get("mktCap") or basic_data.get("marketCap", 0),
            avg_volume=basic_data.get("volAvg") or basic_data.get("avgVolume", 0),
            metrics=metrics,
            last_updated=datetime.now(),
            data_source="fmp",
        )
    
    def close(self):
        """Cierra el cliente HTTP."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
