"""Score IA avanzado con múltiples factores incluyendo sentimiento."""

from dataclasses import dataclass, field
from typing import Optional
import re
import yfinance as yf
from loguru import logger

from src.models.stock import Stock
from src.analysis.analyzer import StockAnalysis, NewsItem


@dataclass
class AIScoreBreakdown:
    """Desglose del Score IA."""
    # Componentes principales (0-10 cada uno)
    fundamental_score: float = 0.0
    valuation_score: float = 0.0
    growth_score: float = 0.0
    momentum_score: float = 0.0
    sentiment_score: float = 0.0
    quality_score: float = 0.0

    # Score total ponderado
    total_score: float = 0.0

    # Detalles
    sentiment_summary: str = ""
    momentum_trend: str = ""  # "bullish", "neutral", "bearish"
    valuation_vs_sector: str = ""  # "cheap", "fair", "expensive"
    growth_outlook: str = ""  # "accelerating", "stable", "decelerating"

    # Flags de riesgo/oportunidad
    flags: list[str] = field(default_factory=list)


# Palabras clave para análisis de sentimiento
POSITIVE_KEYWORDS = [
    "beat", "beats", "exceeds", "surpass", "upgrade", "upgrades", "buy",
    "outperform", "strong", "growth", "record", "profit", "gains", "surge",
    "jumps", "soars", "rally", "bullish", "positive", "success", "boost",
    "innovation", "breakthrough", "expansion", "dividend", "buyback",
    "acquisition", "partnership", "deal", "win", "award", "launch",
]

NEGATIVE_KEYWORDS = [
    "miss", "misses", "below", "downgrade", "downgrades", "sell", "cut",
    "underperform", "weak", "decline", "loss", "losses", "drop", "plunge",
    "falls", "crash", "bearish", "negative", "warning", "concern", "risk",
    "lawsuit", "investigation", "recall", "delay", "layoff", "layoffs",
    "debt", "default", "bankruptcy", "fraud", "scandal", "fine", "penalty",
]

NEUTRAL_KEYWORDS = [
    "hold", "neutral", "maintain", "steady", "flat", "unchanged", "mixed",
]


class AIScorer:
    """Motor de scoring IA avanzado."""

    # Pesos para cada componente
    WEIGHTS = {
        "fundamental": 0.20,    # Ratios financieros básicos
        "valuation": 0.25,      # Qué tan barata está
        "growth": 0.20,         # Proyección de crecimiento
        "momentum": 0.15,       # Tendencia técnica
        "sentiment": 0.10,      # Sentimiento de noticias
        "quality": 0.10,        # Calidad del negocio
    }

    def score(
        self,
        stock: Stock,
        analysis: Optional[StockAnalysis] = None,
        sector_median_pe: Optional[float] = None,
    ) -> AIScoreBreakdown:
        """
        Calcula Score IA completo.

        Args:
            stock: Stock con métricas básicas
            analysis: Análisis completo (noticias, earnings, etc)
            sector_median_pe: P/E mediano del sector para comparación

        Returns:
            AIScoreBreakdown con todos los componentes
        """
        breakdown = AIScoreBreakdown()

        # 1. Score Fundamental (ratios básicos)
        breakdown.fundamental_score = self._score_fundamentals(stock)

        # 2. Score de Valuación (qué tan barata)
        breakdown.valuation_score, breakdown.valuation_vs_sector = (
            self._score_valuation(stock, analysis, sector_median_pe)
        )

        # 3. Score de Crecimiento
        breakdown.growth_score, breakdown.growth_outlook = (
            self._score_growth(stock, analysis)
        )

        # 4. Score de Momentum
        breakdown.momentum_score, breakdown.momentum_trend = (
            self._score_momentum(stock)
        )

        # 5. Score de Sentimiento
        if analysis and analysis.news:
            breakdown.sentiment_score, breakdown.sentiment_summary = (
                self._score_sentiment(analysis.news)
            )
        else:
            breakdown.sentiment_score = 5.0  # Neutral si no hay noticias
            breakdown.sentiment_summary = "No news available"

        # 6. Score de Calidad
        breakdown.quality_score = self._score_quality(stock, analysis)

        # Calcular score total ponderado
        breakdown.total_score = round(
            breakdown.fundamental_score * self.WEIGHTS["fundamental"]
            + breakdown.valuation_score * self.WEIGHTS["valuation"]
            + breakdown.growth_score * self.WEIGHTS["growth"]
            + breakdown.momentum_score * self.WEIGHTS["momentum"]
            + breakdown.sentiment_score * self.WEIGHTS["sentiment"]
            + breakdown.quality_score * self.WEIGHTS["quality"],
            2
        )

        # Agregar flags de oportunidad/riesgo
        breakdown.flags = self._generate_flags(stock, analysis, breakdown)

        return breakdown

    def _score_fundamentals(self, stock: Stock) -> float:
        """Score de fundamentos básicos (0-10)."""
        score = 5.0
        m = stock.metrics

        # ROE
        if m.roe is not None:
            roe_pct = m.roe * 100 if m.roe < 1 else m.roe
            if roe_pct >= 25:
                score += 2
            elif roe_pct >= 20:
                score += 1.5
            elif roe_pct >= 15:
                score += 1
            elif roe_pct < 10:
                score -= 1

        # Margen neto
        if m.net_margin is not None:
            if m.net_margin > 0.20:
                score += 1.5
            elif m.net_margin > 0.15:
                score += 1
            elif m.net_margin > 0.10:
                score += 0.5
            elif m.net_margin < 0.05:
                score -= 1

        # Current ratio
        if m.current_ratio is not None:
            if m.current_ratio >= 2:
                score += 1
            elif m.current_ratio < 1:
                score -= 1.5

        # D/E
        if m.debt_to_equity is not None:
            if m.debt_to_equity <= 0.3:
                score += 1
            elif m.debt_to_equity > 1:
                score -= 1

        return max(0, min(10, score))

    def _score_valuation(
        self,
        stock: Stock,
        analysis: Optional[StockAnalysis],
        sector_median_pe: Optional[float],
    ) -> tuple[float, str]:
        """Score de valuación - qué tan barata está (0-10)."""
        score = 5.0
        vs_sector = "fair"
        m = stock.metrics

        # PEG (más importante para GARP)
        peg = None
        if analysis and analysis.peg_finviz:
            peg = analysis.peg_finviz
        elif m.peg_ratio:
            peg = m.peg_ratio

        if peg is not None:
            if peg <= 0.5:
                score += 3
                vs_sector = "very cheap"
            elif peg <= 0.75:
                score += 2
                vs_sector = "cheap"
            elif peg <= 1:
                score += 1
            elif peg > 1.5:
                score -= 1
                vs_sector = "expensive"
            elif peg > 2:
                score -= 2
                vs_sector = "very expensive"

        # P/E vs sector
        if m.pe_ratio and sector_median_pe:
            pe_ratio = m.pe_ratio / sector_median_pe
            if pe_ratio < 0.7:
                score += 2
                vs_sector = "cheap vs sector"
            elif pe_ratio < 0.9:
                score += 1
            elif pe_ratio > 1.3:
                score -= 1
            elif pe_ratio > 1.5:
                score -= 2

        # Forward P/E (si tenemos)
        if analysis and analysis.fwd_pe:
            if analysis.fwd_pe < 15:
                score += 1
            elif analysis.fwd_pe > 30:
                score -= 1

        # P/FCF (precio a free cash flow)
        # Muy importante para saber si está barata en términos de cash real

        return max(0, min(10, score)), vs_sector

    def _score_growth(
        self,
        stock: Stock,
        analysis: Optional[StockAnalysis],
    ) -> tuple[float, str]:
        """Score de crecimiento proyectado (0-10)."""
        score = 5.0
        outlook = "stable"
        m = stock.metrics

        # EPS growth histórico
        if m.eps_growth_5y is not None:
            growth = m.eps_growth_5y * 100 if m.eps_growth_5y < 1 else m.eps_growth_5y
            if growth >= 25:
                score += 2
                outlook = "strong"
            elif growth >= 15:
                score += 1.5
            elif growth >= 10:
                score += 1
            elif growth < 5:
                score -= 1
                outlook = "weak"

        # EPS proyectado (Finviz)
        if analysis:
            if analysis.eps_this_year and analysis.eps_next_year:
                # Comparar crecimiento este año vs próximo
                if analysis.eps_next_year > analysis.eps_this_year:
                    score += 1.5
                    outlook = "accelerating"
                elif analysis.eps_next_year < analysis.eps_this_year * 0.9:
                    score -= 1
                    outlook = "decelerating"

            # EPS este año alto = muy bueno
            if analysis.eps_this_year and analysis.eps_this_year > 0.3:
                score += 1

        # Revenue growth
        if m.revenue_growth_5y is not None:
            if m.revenue_growth_5y > 0.15:
                score += 1
            elif m.revenue_growth_5y < 0:
                score -= 1

        return max(0, min(10, score)), outlook

    def _score_momentum(self, stock: Stock) -> tuple[float, str]:
        """Score de momentum técnico (0-10)."""
        score = 5.0
        trend = "neutral"

        try:
            ticker = yf.Ticker(stock.symbol)
            hist = ticker.history(period="3mo")

            if hist.empty:
                return score, trend

            current_price = hist["Close"].iloc[-1]

            # SMA 20
            sma_20 = hist["Close"].rolling(20).mean().iloc[-1]
            # SMA 50
            sma_50 = hist["Close"].rolling(50).mean().iloc[-1] if len(hist) >= 50 else sma_20

            # Precio vs promedios
            if current_price > sma_20 > sma_50:
                score += 2
                trend = "bullish"
            elif current_price > sma_20:
                score += 1
                trend = "slightly bullish"
            elif current_price < sma_20 < sma_50:
                score -= 2
                trend = "bearish"
            elif current_price < sma_20:
                score -= 1
                trend = "slightly bearish"

            # Distancia del precio al máximo de 52 semanas
            high_52w = hist["Close"].max()
            low_52w = hist["Close"].min()
            range_52w = high_52w - low_52w

            if range_52w > 0:
                position = (current_price - low_52w) / range_52w
                if position < 0.3:
                    score += 1  # Cerca de mínimos = oportunidad
                elif position > 0.9:
                    score -= 0.5  # Cerca de máximos

            # RSI aproximado (simplificado)
            changes = hist["Close"].diff()
            gains = changes.where(changes > 0, 0).rolling(14).mean()
            losses = (-changes.where(changes < 0, 0)).rolling(14).mean()

            if losses.iloc[-1] > 0:
                rs = gains.iloc[-1] / losses.iloc[-1]
                rsi = 100 - (100 / (1 + rs))

                if rsi < 30:
                    score += 1.5  # Oversold
                    trend = "oversold - potential bounce"
                elif rsi > 70:
                    score -= 0.5  # Overbought

        except Exception as e:
            logger.debug(f"Error calculando momentum: {e}")

        return max(0, min(10, score)), trend

    def _score_sentiment(self, news: list[NewsItem]) -> tuple[float, str]:
        """Score de sentimiento basado en noticias (0-10)."""
        if not news:
            return 5.0, "No news"

        positive_count = 0
        negative_count = 0
        total_words = 0

        for item in news:
            title_lower = item.title.lower()
            words = re.findall(r'\w+', title_lower)
            total_words += len(words)

            for word in words:
                if word in POSITIVE_KEYWORDS:
                    positive_count += 1
                elif word in NEGATIVE_KEYWORDS:
                    negative_count += 1

        # Calcular score
        score = 5.0
        if positive_count + negative_count > 0:
            sentiment_ratio = (positive_count - negative_count) / (positive_count + negative_count)
            score += sentiment_ratio * 3

        # Generar resumen
        if positive_count > negative_count * 2:
            summary = f"Very positive ({positive_count}+ / {negative_count}-)"
        elif positive_count > negative_count:
            summary = f"Positive ({positive_count}+ / {negative_count}-)"
        elif negative_count > positive_count * 2:
            summary = f"Very negative ({positive_count}+ / {negative_count}-)"
        elif negative_count > positive_count:
            summary = f"Negative ({positive_count}+ / {negative_count}-)"
        else:
            summary = f"Neutral ({positive_count}+ / {negative_count}-)"

        return max(0, min(10, score)), summary

    def _score_quality(
        self,
        stock: Stock,
        analysis: Optional[StockAnalysis],
    ) -> float:
        """Score de calidad del negocio (0-10)."""
        score = 5.0
        m = stock.metrics

        # ROA alto = negocio eficiente
        if m.roa is not None:
            if m.roa > 0.15:
                score += 2
            elif m.roa > 0.10:
                score += 1
            elif m.roa < 0.05:
                score -= 1

        # FCF positivo
        if analysis and analysis.free_cash_flow:
            if analysis.free_cash_flow > 0:
                score += 1
                # FCF > Net Income = calidad de earnings
                if analysis.net_income_ttm and analysis.free_cash_flow > analysis.net_income_ttm:
                    score += 1

        # Cash vs Debt
        if analysis and analysis.total_cash and analysis.total_debt:
            if analysis.total_cash > analysis.total_debt:
                score += 1  # Net cash position

        # Gross margin alto = ventaja competitiva
        if m.gross_margin is not None:
            if m.gross_margin > 0.40:
                score += 1
            elif m.gross_margin < 0.20:
                score -= 1

        return max(0, min(10, score))

    def _generate_flags(
        self,
        stock: Stock,
        analysis: Optional[StockAnalysis],
        breakdown: AIScoreBreakdown,
    ) -> list[str]:
        """Genera flags de oportunidad y riesgo."""
        flags = []

        # Oportunidades
        if breakdown.valuation_score >= 8:
            flags.append("OPPORTUNITY: Very undervalued")

        if breakdown.sentiment_score >= 7 and breakdown.momentum_score >= 7:
            flags.append("OPPORTUNITY: Positive momentum + sentiment")

        if breakdown.growth_outlook == "accelerating":
            flags.append("OPPORTUNITY: Accelerating growth")

        if breakdown.momentum_trend == "oversold - potential bounce":
            flags.append("OPPORTUNITY: Technically oversold")

        # PEG muy bajo
        if analysis and analysis.peg_finviz and analysis.peg_finviz < 0.5:
            flags.append(f"OPPORTUNITY: Very low PEG ({analysis.peg_finviz:.2f})")

        # Riesgos
        if breakdown.sentiment_score <= 3:
            flags.append("RISK: Negative news sentiment")

        if breakdown.momentum_trend == "bearish":
            flags.append("RISK: Bearish technical trend")

        if breakdown.growth_outlook == "decelerating":
            flags.append("RISK: Decelerating growth")

        if stock.metrics.debt_to_equity and stock.metrics.debt_to_equity > 1:
            flags.append("RISK: High debt levels")

        # Earnings próximos
        if analysis and analysis.earnings and analysis.earnings.next_earnings_date:
            flags.append(f"EVENT: Earnings on {analysis.earnings.next_earnings_date}")

        return flags
