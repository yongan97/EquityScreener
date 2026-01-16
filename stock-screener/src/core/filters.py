"""Motor de filtros para el screener."""

from typing import Optional, Callable
from loguru import logger

from src.models.stock import Stock


class FilterEngine:
    """
    Motor de filtros configurable.
    Aplica criterios de valuación, crecimiento, rentabilidad y solidez financiera.
    """
    
    def __init__(self, config: dict):
        """
        Inicializa el motor de filtros.
        
        Args:
            config: Configuración completa del screener
        """
        self.config = config
        self.filters = self._build_filters()
    
    def _build_filters(self) -> list[tuple[str, Callable[[Stock], bool]]]:
        """Construye lista de filtros desde la configuración."""
        filters = []
        
        # Filtros de valuación
        for metric, bounds in self.config.get("valuation", {}).items():
            if bounds.get("min") is not None or bounds.get("max") is not None:
                filters.append((
                    f"valuation.{metric}",
                    self._create_range_filter(metric, bounds)
                ))
        
        # Filtros de crecimiento
        for metric, bounds in self.config.get("growth", {}).items():
            if bounds.get("min") is not None or bounds.get("max") is not None:
                filters.append((
                    f"growth.{metric}",
                    self._create_range_filter(metric, bounds)
                ))
        
        # Filtros de rentabilidad
        for metric, bounds in self.config.get("profitability", {}).items():
            if bounds.get("min") is not None or bounds.get("max") is not None:
                filters.append((
                    f"profitability.{metric}",
                    self._create_range_filter(metric, bounds)
                ))
        
        # Filtros de liquidez
        for metric, bounds in self.config.get("liquidity", {}).items():
            if bounds.get("min") is not None or bounds.get("max") is not None:
                filters.append((
                    f"liquidity.{metric}",
                    self._create_range_filter(metric, bounds)
                ))
        
        # Filtros de solvencia
        for metric, bounds in self.config.get("solvency", {}).items():
            if bounds.get("min") is not None or bounds.get("max") is not None:
                filters.append((
                    f"solvency.{metric}",
                    self._create_range_filter(metric, bounds)
                ))
        
        # Filtros de operabilidad adicionales
        operability = self.config.get("operability", {})
        
        if operability.get("exclude_sectors"):
            filters.append((
                "operability.sector",
                lambda s: s.sector not in operability["exclude_sectors"]
            ))
        
        if operability.get("exclude_industries"):
            filters.append((
                "operability.industry",
                lambda s: s.industry not in operability["exclude_industries"]
            ))
        
        logger.info(f"Filtros configurados: {len(filters)}")
        return filters
    
    def _create_range_filter(
        self,
        metric: str,
        bounds: dict
    ) -> Callable[[Stock], bool]:
        """
        Crea función de filtro para un rango.

        Args:
            metric: Nombre de la métrica en StockMetrics
            bounds: Dict con 'min' y/o 'max' y opcionalmente 'required'

        Returns:
            Función que evalúa si el stock pasa el filtro
        """
        min_val = bounds.get("min")
        max_val = bounds.get("max")
        required = bounds.get("required", False)  # Por defecto, no requerido

        def filter_func(stock: Stock) -> bool:
            value = getattr(stock.metrics, metric, None)

            # Si no hay dato, depende de si es requerido
            if value is None:
                return not required  # Pasa si no es requerido

            if min_val is not None and value < min_val:
                return False

            if max_val is not None and value > max_val:
                return False

            return True

        return filter_func
    
    def passes_all(self, stock: Stock) -> bool:
        """
        Evalúa si un stock pasa todos los filtros.
        
        Args:
            stock: Stock a evaluar
        
        Returns:
            True si pasa todos los filtros
        """
        for filter_name, filter_func in self.filters:
            if not filter_func(stock):
                logger.debug(f"{stock.symbol} falló en {filter_name}")
                return False
        return True
    
    def evaluate(self, stock: Stock) -> dict[str, bool]:
        """
        Evalúa stock contra todos los filtros individualmente.
        
        Args:
            stock: Stock a evaluar
        
        Returns:
            Dict con resultado de cada filtro
        """
        return {
            name: func(stock)
            for name, func in self.filters
        }
    
    def get_failing_filters(self, stock: Stock) -> list[str]:
        """
        Obtiene lista de filtros que el stock no pasa.
        
        Args:
            stock: Stock a evaluar
        
        Returns:
            Lista de nombres de filtros fallidos
        """
        return [
            name
            for name, func in self.filters
            if not func(stock)
        ]
