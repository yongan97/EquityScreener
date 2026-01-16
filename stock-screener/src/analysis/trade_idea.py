"""Generador de Trade Ideas para enviar a clientes."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.models.stock import Stock
from src.analysis.analyzer import StockAnalysis
from src.analysis.ai_scoring import AIScoreBreakdown


@dataclass
class TradeIdea:
    """Trade Idea completa para copiar/pegar."""
    symbol: str
    generated_at: datetime
    markdown: str
    plain_text: str


def format_currency(value: float) -> str:
    """Formatea valores en billones/millones."""
    if value is None:
        return "N/A"
    if abs(value) >= 1e12:
        return f"${value/1e12:.2f}T"
    if abs(value) >= 1e9:
        return f"${value/1e9:.2f}B"
    if abs(value) >= 1e6:
        return f"${value/1e6:.2f}M"
    return f"${value:,.0f}"


def format_percent(value: float) -> str:
    """Formatea porcentajes."""
    if value is None:
        return "N/A"
    return f"{value*100:.1f}%" if abs(value) < 1 else f"{value:.1f}%"


def get_sector_spanish(sector: str) -> str:
    """Traduce sector a español."""
    translations = {
        "Technology": "Tecnologia",
        "Basic Materials": "Materiales Basicos",
        "Financial Services": "Servicios Financieros",
        "Healthcare": "Salud",
        "Consumer Cyclical": "Consumo Ciclico",
        "Consumer Defensive": "Consumo Defensivo",
        "Energy": "Energia",
        "Industrials": "Industriales",
        "Utilities": "Servicios Publicos",
        "Real Estate": "Bienes Raices",
        "Communication Services": "Comunicaciones",
    }
    return translations.get(sector, sector)


class TradeIdeaGenerator:
    """Genera Trade Ideas completas."""

    def generate(
        self,
        stock: Stock,
        analysis: StockAnalysis,
        ai_score: AIScoreBreakdown,
    ) -> TradeIdea:
        """
        Genera una Trade Idea completa.

        Args:
            stock: Stock con métricas
            analysis: Análisis completo
            ai_score: Score IA con breakdown

        Returns:
            TradeIdea con markdown y texto plano
        """
        now = datetime.now()
        m = stock.metrics

        # Determinar recomendación basada en score
        if ai_score.total_score >= 7.5:
            recommendation = "COMPRA FUERTE"
            rec_en = "STRONG BUY"
        elif ai_score.total_score >= 6.5:
            recommendation = "COMPRA"
            rec_en = "BUY"
        elif ai_score.total_score >= 5.5:
            recommendation = "MANTENER"
            rec_en = "HOLD"
        else:
            recommendation = "OBSERVAR"
            rec_en = "WATCH"

        # Generar markdown
        markdown = self._generate_markdown(
            stock, analysis, ai_score, recommendation, now
        )

        # Generar texto plano
        plain_text = self._generate_plain_text(
            stock, analysis, ai_score, rec_en, now
        )

        return TradeIdea(
            symbol=stock.symbol,
            generated_at=now,
            markdown=markdown,
            plain_text=plain_text,
        )

    def _generate_markdown(
        self,
        stock: Stock,
        analysis: StockAnalysis,
        ai_score: AIScoreBreakdown,
        recommendation: str,
        now: datetime,
    ) -> str:
        """Genera Trade Idea en formato Markdown profesional."""
        m = stock.metrics
        sector_es = get_sector_spanish(stock.sector) if stock.sector else "N/A"

        # Determinar market cap category
        if stock.market_cap and stock.market_cap >= 200e9:
            cap_cat = "Mega cap"
        elif stock.market_cap and stock.market_cap >= 10e9:
            cap_cat = "Large cap"
        elif stock.market_cap and stock.market_cap >= 2e9:
            cap_cat = "Mid cap"
        else:
            cap_cat = "Small cap"

        # Build thesis reasons based on scores
        reasons = []

        # Reason 1: Best strength
        if ai_score.fundamental_score >= 8 and m.roe:
            roe_pct = m.roe * 100 if m.roe < 1 else m.roe
            margin_pct = m.net_margin * 100 if m.net_margin and m.net_margin < 1 else (m.net_margin or 0)
            reasons.append(f"**Rentabilidad excepcional** - ROE del {roe_pct:.1f}% y margen neto del {margin_pct:.1f}%, muy por encima del promedio del sector.")
        elif ai_score.valuation_score >= 7:
            pe_str = f"P/E de {m.pe_ratio:.1f}x" if m.pe_ratio else "valuacion atractiva"
            reasons.append(f"**Valuacion atractiva** - {pe_str}, cotiza por debajo de su valor intrinseco segun metricas GARP.")
        elif ai_score.growth_score >= 7:
            growth_str = f"crecimiento de EPS del {format_percent(m.eps_growth_5y)}" if m.eps_growth_5y else "solido crecimiento proyectado"
            reasons.append(f"**Crecimiento sostenido** - {growth_str} en los ultimos 5 anos con perspectivas positivas.")

        # Reason 2: Second strength
        if ai_score.quality_score >= 7 and analysis.free_cash_flow:
            fcf_str = format_currency(analysis.free_cash_flow)
            reasons.append(f"**Generacion de caja solida** - Free Cash Flow de {fcf_str}, permitiendo reinversion y retorno a accionistas.")
        elif ai_score.momentum_score >= 7:
            reasons.append(f"**Momentum tecnico positivo** - {ai_score.momentum_trend}, indicando interes comprador sostenido.")
        elif m.current_ratio and m.current_ratio > 1.5:
            reasons.append(f"**Liquidez robusta** - Current Ratio de {m.current_ratio:.2f}, sin presion financiera a corto plazo.")

        # Reason 3: Balance strength
        if m.debt_to_equity and m.debt_to_equity < 0.5:
            if analysis.total_cash and analysis.total_debt:
                net = analysis.total_cash - analysis.total_debt
                if net > 0:
                    reasons.append(f"**Balance fortaleza** - Posicion neta de caja de {format_currency(net)}, sin presion de deuda. Ratio D/E de apenas {m.debt_to_equity:.2f}.")
                else:
                    reasons.append(f"**Deuda controlada** - Ratio D/E de {m.debt_to_equity:.2f}, conservador para el sector.")
            else:
                reasons.append(f"**Estructura de capital conservadora** - Ratio D/E de {m.debt_to_equity:.2f}, bajo riesgo financiero.")

        # Ensure at least 2 reasons
        if len(reasons) < 2:
            if ai_score.sentiment_score >= 6:
                reasons.append(f"**Sentimiento favorable** - {ai_score.sentiment_summary}")
            else:
                reasons.append("**Pasa filtros GARP** - Cumple criterios de Growth at Reasonable Price.")

        # Build risks
        risks = []
        if ai_score.valuation_score < 6 and m.pe_ratio and m.pe_ratio > 25:
            risks.append(f"**Valuacion elevada** - P/E de {m.pe_ratio:.1f}x por encima del promedio historico. Requiere que se cumplan expectativas de crecimiento.")
        if m.debt_to_equity and m.debt_to_equity > 0.8:
            risks.append(f"**Apalancamiento** - D/E de {m.debt_to_equity:.2f} implica sensibilidad a tasas de interes.")
        if ai_score.momentum_score < 5:
            risks.append(f"**Momentum debil** - {ai_score.momentum_trend}. Podria haber presion vendedora en el corto plazo.")
        if not risks:
            risks.append("**Riesgo de mercado** - Como toda inversion en renta variable, esta sujeta a volatilidad del mercado.")

        # Header
        md = f"""# Trade Idea: {stock.symbol} ({stock.name})

**Fecha:** {now.strftime('%d de %B de %Y').replace('January', 'enero').replace('February', 'febrero').replace('March', 'marzo').replace('April', 'abril').replace('May', 'mayo').replace('June', 'junio').replace('July', 'julio').replace('August', 'agosto').replace('September', 'septiembre').replace('October', 'octubre').replace('November', 'noviembre').replace('December', 'diciembre')}
**Recomendacion:** {recommendation}
**Sector:** {sector_es} - {analysis.industry or 'N/A'}

---

## Tesis de Inversion

{stock.name} representa una oportunidad atractiva en el sector de {sector_es.lower()}, combinando fundamentos solidos con una valuacion razonable segun la estrategia GARP (Growth at Reasonable Price).

**Razones para comprar:**

"""
        for i, reason in enumerate(reasons[:3], 1):
            md += f"{i}. {reason}\n\n"

        # Metrics table
        md += f"""---

## Metricas Clave

| | Valor | Contexto |
|---|---:|---|
| Precio actual | ${stock.price:.2f} | - |
| Market Cap | {format_currency(stock.market_cap)} | {cap_cat} |
| P/E | {f"{m.pe_ratio:.1f}x" if m.pe_ratio else "N/A"} | {"Prima por crecimiento" if m.pe_ratio and m.pe_ratio > 20 else "Atractivo" if m.pe_ratio else "-"} |
| ROE | {format_percent(m.roe)} | {"Excelente" if m.roe and (m.roe > 0.15 or m.roe > 15) else "Bueno" if m.roe else "-"} |
| Margen neto | {format_percent(m.net_margin)} | {"Solido" if m.net_margin and (m.net_margin > 0.1 or m.net_margin > 10) else "-"} |
| Crecimiento EPS 5Y | {format_percent(m.eps_growth_5y)} | {"Fuerte" if m.eps_growth_5y and (m.eps_growth_5y > 0.1 or m.eps_growth_5y > 10) else "-"} |
| Current Ratio | {f"{m.current_ratio:.2f}" if m.current_ratio else "N/A"} | {"Liquidez solida" if m.current_ratio and m.current_ratio > 1.5 else "-"} |
| Deuda/Equity | {f"{m.debt_to_equity:.2f}" if m.debt_to_equity else "N/A"} | {"Conservador" if m.debt_to_equity and m.debt_to_equity < 0.5 else "Moderado" if m.debt_to_equity else "-"} |

"""

        # Catalysts if news available
        if analysis.news and len(analysis.news) > 0:
            md += """---

## Catalizadores

"""
            for news in analysis.news[:3]:
                md += f"- **{news.source}:** {news.title}\n"
            md += "\n"

        # Risks
        md += """---

## Riesgos a Monitorear

"""
        for risk in risks[:3]:
            md += f"- {risk}\n"

        # Conclusion
        md += f"""
---

## Conclusion

{stock.symbol} ofrece una combinacion atractiva de {"crecimiento y valor" if ai_score.growth_score >= 6 and ai_score.valuation_score >= 6 else "fundamentos solidos"} que la posiciona favorablemente para inversores con horizonte de mediano plazo. {"La solidez del balance proporciona margen de seguridad." if m.debt_to_equity and m.debt_to_equity < 0.5 else ""}

**Score:** {ai_score.total_score:.1f}/10
**Horizonte sugerido:** 12-24 meses

---

*Este documento es informativo y no constituye recomendacion de compra o venta. Consulte a su asesor financiero antes de invertir.*
"""
        return md

    def _generate_plain_text(
        self,
        stock: Stock,
        analysis: StockAnalysis,
        ai_score: AIScoreBreakdown,
        recommendation: str,
        now: datetime,
    ) -> str:
        """Genera Trade Idea en texto plano."""
        m = stock.metrics

        txt = f"""
================================================================================
TRADE IDEA: {stock.symbol} - {recommendation}
================================================================================

{stock.name}
Sector: {stock.sector} | Industry: {analysis.industry}
Fecha: {now.strftime('%d/%m/%Y %H:%M')}

--------------------------------------------------------------------------------
RESUMEN EJECUTIVO
--------------------------------------------------------------------------------
Recomendación: {recommendation}
Score IA: {ai_score.total_score}/10
Precio: ${stock.price:.2f}
Market Cap: {format_currency(stock.market_cap)}

--------------------------------------------------------------------------------
METRICAS CLAVE
--------------------------------------------------------------------------------
P/E: {f"{m.pe_ratio:.1f}" if m.pe_ratio else "N/A"}
PEG: {f"{analysis.peg_finviz:.2f}" if analysis.peg_finviz else "N/A"}
ROE: {format_percent(m.roe)}
D/E: {f"{m.debt_to_equity:.2f}" if m.debt_to_equity else "N/A"}

--------------------------------------------------------------------------------
SCORE IA BREAKDOWN
--------------------------------------------------------------------------------
Fundamental:  {ai_score.fundamental_score:.1f}/10
Valuación:    {ai_score.valuation_score:.1f}/10 ({ai_score.valuation_vs_sector})
Crecimiento:  {ai_score.growth_score:.1f}/10 ({ai_score.growth_outlook})
Momentum:     {ai_score.momentum_score:.1f}/10 ({ai_score.momentum_trend})
Sentimiento:  {ai_score.sentiment_score:.1f}/10 ({ai_score.sentiment_summary})
Calidad:      {ai_score.quality_score:.1f}/10
-----------------------------------------
TOTAL:        {ai_score.total_score}/10

--------------------------------------------------------------------------------
BALANCE
--------------------------------------------------------------------------------
Revenue TTM: {format_currency(analysis.revenue_ttm)}
Net Income:  {format_currency(analysis.net_income_ttm)}
Free Cash Flow: {format_currency(analysis.free_cash_flow)}
Cash: {format_currency(analysis.total_cash)}
Debt: {format_currency(analysis.total_debt)}
"""
        if analysis.earnings and analysis.earnings.next_earnings_date:
            txt += f"""
--------------------------------------------------------------------------------
PRÓXIMO EARNINGS: {analysis.earnings.next_earnings_date}
--------------------------------------------------------------------------------
"""

        if ai_score.flags:
            txt += """
--------------------------------------------------------------------------------
SEÑALES
--------------------------------------------------------------------------------
"""
            for flag in ai_score.flags:
                txt += f"- {flag}\n"

        txt += """
================================================================================
DISCLAIMER: Esta idea es generada automáticamente. No constituye asesoramiento
financiero. Realice su propia investigación antes de invertir.
================================================================================
"""
        return txt

    def generate_quick_summary(
        self,
        stock: Stock,
        ai_score: AIScoreBreakdown,
    ) -> str:
        """Genera resumen rápido de una línea."""
        if ai_score.total_score >= 7.5:
            rec = "STRONG BUY"
        elif ai_score.total_score >= 6.5:
            rec = "BUY"
        elif ai_score.total_score >= 5.5:
            rec = "HOLD"
        else:
            rec = "WATCH"

        return f"{stock.symbol} | {rec} | Score: {ai_score.total_score}/10 | ${stock.price:.2f} | {stock.sector}"
