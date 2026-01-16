"""Motor de scoring para rankear stocks."""

from typing import Optional
from src.models.stock import Stock


class ScoringEngine:
    """
    Motor de scoring para rankear stocks que pasan los filtros.
    Asigna puntaje basado en qué tan bien cumple cada criterio.
    """
    
    def __init__(self, config: dict):
        """
        Inicializa el motor de scoring.
        
        Args:
            config: Configuración de scoring con pesos
        """
        self.enabled = config.get("enabled", True)
        self.weights = config.get("weights", {
            "valuation": 0.25,
            "growth": 0.25,
            "profitability": 0.25,
            "financial_health": 0.25,
        })
    
    def score(self, stock: Stock) -> tuple[float, dict]:
        """
        Calcula score total y breakdown por categoría.
        
        Args:
            stock: Stock a evaluar
        
        Returns:
            Tuple de (score_total, breakdown_dict)
        """
        breakdown = {}
        
        # Score de valuación (menor PEG = mejor)
        breakdown["valuation"] = self._score_valuation(stock)
        
        # Score de crecimiento
        breakdown["growth"] = self._score_growth(stock)
        
        # Score de rentabilidad
        breakdown["profitability"] = self._score_profitability(stock)
        
        # Score de salud financiera
        breakdown["financial_health"] = self._score_financial_health(stock)
        
        # Score ponderado
        total = sum(
            breakdown.get(cat, 0) * self.weights.get(cat, 0)
            for cat in self.weights
        )
        
        return round(total, 2), breakdown
    
    def _score_valuation(self, stock: Stock) -> float:
        """
        Score de valuación (0-10).
        Menor PEG y P/E razonable = mejor.
        """
        score = 5.0  # Base
        metrics = stock.metrics
        
        # PEG: mejor si más bajo (pero positivo)
        if metrics.peg_ratio is not None:
            if metrics.peg_ratio <= 0.5:
                score += 3
            elif metrics.peg_ratio <= 0.75:
                score += 2
            elif metrics.peg_ratio <= 1:
                score += 1
            elif metrics.peg_ratio > 1.5:
                score -= 2
        
        # P/E: penalizar extremos
        if metrics.pe_ratio is not None:
            if 10 <= metrics.pe_ratio <= 20:
                score += 2  # Rango ideal
            elif 5 <= metrics.pe_ratio <= 30:
                score += 1
            elif metrics.pe_ratio > 50:
                score -= 2
        
        return max(0, min(10, score))
    
    def _score_growth(self, stock: Stock) -> float:
        """
        Score de crecimiento (0-10).
        Mayor crecimiento proyectado = mejor.
        """
        score = 5.0
        metrics = stock.metrics
        
        # EPS growth 5Y
        if metrics.eps_growth_5y is not None:
            growth = metrics.eps_growth_5y * 100  # Convertir a %
            
            if growth >= 20:
                score += 3
            elif growth >= 15:
                score += 2
            elif growth >= 10:
                score += 1
            elif growth < 5:
                score -= 1
        
        # Revenue growth (bonus)
        if metrics.revenue_growth_5y is not None:
            if metrics.revenue_growth_5y > 0.1:
                score += 1
        
        return max(0, min(10, score))
    
    def _score_profitability(self, stock: Stock) -> float:
        """
        Score de rentabilidad (0-10).
        Mayor ROE y márgenes = mejor.
        """
        score = 5.0
        metrics = stock.metrics
        
        # ROE
        if metrics.roe is not None:
            roe_pct = metrics.roe * 100 if metrics.roe < 1 else metrics.roe
            
            if roe_pct >= 25:
                score += 3
            elif roe_pct >= 20:
                score += 2
            elif roe_pct >= 15:
                score += 1
            elif roe_pct < 10:
                score -= 1
        
        # Margen neto (bonus)
        if metrics.net_margin is not None:
            if metrics.net_margin > 0.15:
                score += 1
            elif metrics.net_margin > 0.10:
                score += 0.5
        
        # ROA (bonus)
        if metrics.roa is not None:
            if metrics.roa > 0.10:
                score += 1
        
        return max(0, min(10, score))
    
    def _score_financial_health(self, stock: Stock) -> float:
        """
        Score de salud financiera (0-10).
        Mejor liquidez y menor deuda = mejor.
        """
        score = 5.0
        metrics = stock.metrics
        
        # Current ratio
        if metrics.current_ratio is not None:
            if metrics.current_ratio >= 2.5:
                score += 2
            elif metrics.current_ratio >= 2:
                score += 1.5
            elif metrics.current_ratio >= 1.5:
                score += 1
            elif metrics.current_ratio < 1:
                score -= 2
        
        # Quick ratio
        if metrics.quick_ratio is not None:
            if metrics.quick_ratio >= 1.5:
                score += 1.5
            elif metrics.quick_ratio >= 1:
                score += 1
            elif metrics.quick_ratio < 0.5:
                score -= 1
        
        # Debt/Equity
        if metrics.debt_to_equity is not None:
            if metrics.debt_to_equity <= 0.2:
                score += 2
            elif metrics.debt_to_equity <= 0.3:
                score += 1.5
            elif metrics.debt_to_equity <= 0.5:
                score += 1
            elif metrics.debt_to_equity > 1:
                score -= 2
        
        return max(0, min(10, score))
