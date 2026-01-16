"""Lógica principal del screener de acciones."""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

from loguru import logger

from src.api.yahoo_screener import YahooScreener
from src.api.finviz import FinvizClient
from src.models.stock import Stock, StockMetrics, ScreenerResult
from src.core.filters import FilterEngine
from src.core.scoring import ScoringEngine


class StockScreener:
    """
    Screener principal de acciones.
    Puede usar Finviz o Yahoo Finance como fuente de universo.
    """

    def __init__(
        self,
        config_path: str = "config/default.json",
        use_cache: bool = True,
    ):
        """
        Inicializa el screener.

        Args:
            config_path: Ruta al archivo de configuración
            use_cache: Si usar cache local
        """
        self.config = self._load_config(config_path)
        self.use_cache = use_cache
        self.data_source = self.config.get("data_source", "yahoo")

        # Inicializar componentes
        self.yahoo_client = YahooScreener()
        self.finviz_client = None
        if self.data_source == "finviz":
            self.finviz_client = FinvizClient()

        self.filter_engine = FilterEngine(self.config)
        self.scoring_engine = ScoringEngine(self.config.get("scoring", {}))

        logger.info(f"Screener inicializado con config: {self.config['name']} (source: {self.data_source})")
    
    def _load_config(self, path: str) -> dict:
        """Carga configuración desde JSON."""
        config_path = Path(path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config no encontrada: {path}")
        
        with open(config_path) as f:
            config = json.load(f)
        
        # Si extiende otra config, mergear
        if "extends" in config:
            base_path = config_path.parent / f"{config['extends']}.json"
            base_config = self._load_config(str(base_path))
            config = self._merge_config(base_config, config)
        
        return config
    
    def _merge_config(self, base: dict, override: dict) -> dict:
        """Mergea configuraciones (override sobre base)."""
        result = base.copy()
        
        for key, value in override.items():
            if key == "extends":
                continue
            if isinstance(value, dict) and key in result:
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def run(self, limit: Optional[int] = None) -> ScreenerResult:
        """
        Ejecuta el screener completo.

        Args:
            limit: Límite de stocks a procesar (para testing)

        Returns:
            ScreenerResult con stocks que pasan todos los filtros
        """
        start_time = time.time()
        errors = []

        logger.info("Iniciando screener...")

        # Paso 1: Obtener universo inicial según data_source
        operability = self.config.get("operability", {})

        try:
            if self.data_source == "finviz" and self.finviz_client:
                # Usar Finviz para obtener universo con filtros GARP
                logger.info("Obteniendo universo desde Finviz...")
                finviz_filters = self.finviz_client.get_garp_filters()
                finviz_results = self.finviz_client.screen(finviz_filters)

                # Convertir a formato de candidatos
                candidates = [
                    {"symbol": r["symbol"], "name": r.get("name", "")}
                    for r in finviz_results
                ]
                logger.info(f"Finviz retornó {len(candidates)} candidatos pre-filtrados")
            else:
                # Usar Yahoo Finance
                candidates = self.yahoo_client.screen_stocks(
                    market_cap_min=operability.get("market_cap_min", 2e9),
                    price_min=operability.get("price_min", 5),
                    volume_min=operability.get("avg_volume_min", 300000),
                    exchange=operability.get("exchange"),
                )

            logger.info(f"Candidatos iniciales: {len(candidates)}")
        except Exception as e:
            logger.error(f"Error en screening inicial: {e}")
            errors.append(str(e))
            candidates = []

        if limit:
            candidates = candidates[:limit]

        # Paso 2: Construir stocks con Yahoo (métricas detalladas) y aplicar filtros
        passing_stocks = []
        total_scanned = 0

        for i, candidate in enumerate(candidates):
            symbol = candidate.get("symbol")

            if not symbol:
                continue

            total_scanned += 1

            try:
                # Construir Stock con métricas completas desde Yahoo
                stock = self.yahoo_client.build_stock(symbol, candidate)

                if not stock:
                    continue

                # Aplicar filtros (verificación adicional con datos detallados)
                if self.filter_engine.passes_all(stock):
                    # Calcular score
                    if self.config.get("scoring", {}).get("enabled"):
                        stock.score, stock.score_breakdown = self.scoring_engine.score(stock)

                    passing_stocks.append(stock)
                    logger.debug(f"✓ {symbol} (score: {stock.score})")
                else:
                    logger.debug(f"✗ {symbol}")

            except Exception as e:
                logger.warning(f"Error procesando {symbol}: {e}")
                errors.append(f"{symbol}: {str(e)}")

            # Progress log cada 50 stocks
            if (i + 1) % 50 == 0:
                logger.info(f"Progreso: {i + 1}/{len(candidates)} procesados, {len(passing_stocks)} passing")

        # Paso 3: Ordenar por score
        if self.config.get("scoring", {}).get("enabled"):
            passing_stocks.sort(key=lambda s: s.score or 0, reverse=True)

        # Limitar resultados
        max_results = self.config.get("output", {}).get("max_results", 100)
        passing_stocks = passing_stocks[:max_results]

        execution_time = time.time() - start_time

        result = ScreenerResult(
            timestamp=datetime.now(),
            config_name=self.config["name"],
            total_scanned=total_scanned,
            total_matches=len(passing_stocks),
            stocks=passing_stocks,
            execution_time_seconds=round(execution_time, 2),
            errors=errors,
        )

        logger.info(
            f"Screener completado: {result.total_matches}/{result.total_scanned} "
            f"en {result.execution_time_seconds}s"
        )

        return result

    def close(self):
        """Libera recursos."""
        self.yahoo_client.close()
        if self.finviz_client:
            self.finviz_client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
