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
            recommendation = "STRONG BUY"
            rec_color = "🟢"
        elif ai_score.total_score >= 6.5:
            recommendation = "BUY"
            rec_color = "🟢"
        elif ai_score.total_score >= 5.5:
            recommendation = "HOLD"
            rec_color = "🟡"
        else:
            recommendation = "WATCH"
            rec_color = "🟠"

        # Generar markdown
        markdown = self._generate_markdown(
            stock, analysis, ai_score, recommendation, rec_color, now
        )

        # Generar texto plano
        plain_text = self._generate_plain_text(
            stock, analysis, ai_score, recommendation, now
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
        rec_color: str,
        now: datetime,
    ) -> str:
        """Genera Trade Idea en formato Markdown."""
        m = stock.metrics

        # Header
        md = f"""# {rec_color} Trade Idea: {stock.symbol}

**{stock.name}**
Sector: {stock.sector} | Industry: {analysis.industry}
Fecha: {now.strftime('%d/%m/%Y %H:%M')}

---

## 📊 Resumen Ejecutivo

| Métrica | Valor |
|---------|-------|
| **Recomendación** | **{recommendation}** |
| **Score IA** | **{ai_score.total_score}/10** |
| **Precio Actual** | ${stock.price:.2f} |
| **Market Cap** | {format_currency(stock.market_cap)} |

---

## 🎯 Por Qué Comprar {stock.symbol}

"""
        # Razones basadas en scores
        reasons = []

        if ai_score.fundamental_score >= 8:
            reasons.append(f"✅ **Fundamentos sólidos** (Score: {ai_score.fundamental_score}/10) - ROE del {format_percent(m.roe)}, márgenes saludables")

        if ai_score.valuation_score >= 7:
            peg_str = f"PEG de {analysis.peg_finviz:.2f}" if analysis.peg_finviz else "valuación atractiva"
            reasons.append(f"✅ **Valuación atractiva** (Score: {ai_score.valuation_score}/10) - {peg_str}, {ai_score.valuation_vs_sector}")

        if ai_score.growth_score >= 7:
            reasons.append(f"✅ **Crecimiento proyectado** (Score: {ai_score.growth_score}/10) - Outlook: {ai_score.growth_outlook}")

        if ai_score.momentum_score >= 7:
            reasons.append(f"✅ **Momentum técnico positivo** (Score: {ai_score.momentum_score}/10) - {ai_score.momentum_trend}")

        if ai_score.sentiment_score >= 7:
            reasons.append(f"✅ **Sentimiento positivo** (Score: {ai_score.sentiment_score}/10) - {ai_score.sentiment_summary}")

        if ai_score.quality_score >= 8:
            fcf_str = format_currency(analysis.free_cash_flow) if analysis.free_cash_flow else "sólido"
            reasons.append(f"✅ **Calidad del negocio** (Score: {ai_score.quality_score}/10) - FCF: {fcf_str}")

        if not reasons:
            reasons.append(f"✅ Pasa todos los filtros GARP con Score: {ai_score.total_score}/10")

        md += "\n".join(reasons)

        # Métricas clave
        md += f"""

---

## 📈 Métricas Fundamentales

### Valuación
| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| P/E Ratio | {f"{m.pe_ratio:.1f}" if m.pe_ratio else "N/A"} | {"Atractivo" if m.pe_ratio and m.pe_ratio < 20 else "Elevado" if m.pe_ratio and m.pe_ratio > 30 else "Razonable"} |
| PEG (Finviz) | {f"{analysis.peg_finviz:.2f}" if analysis.peg_finviz else "N/A"} | {"Muy atractivo" if analysis.peg_finviz and analysis.peg_finviz < 1 else "Razonable"} |
| Forward P/E | {f"{analysis.fwd_pe:.1f}" if analysis.fwd_pe else "N/A"} | - |
| P/B | {f"{m.pb_ratio:.2f}" if m.pb_ratio else "N/A"} | - |

### Rentabilidad
| Métrica | Valor |
|---------|-------|
| ROE | {format_percent(m.roe)} |
| ROA | {format_percent(m.roa)} |
| Margen Neto | {format_percent(m.net_margin)} |
| Margen Bruto | {format_percent(m.gross_margin)} |

### Crecimiento
| Métrica | Valor |
|---------|-------|
| EPS Growth (5Y) | {format_percent(m.eps_growth_5y)} |
| EPS Este Año | {format_percent(analysis.eps_this_year)} |
| EPS Próximo Año | {format_percent(analysis.eps_next_year)} |

### Salud Financiera
| Métrica | Valor | Status |
|---------|-------|--------|
| Current Ratio | {f"{m.current_ratio:.2f}" if m.current_ratio else "N/A"} | {"Solido" if m.current_ratio and m.current_ratio > 1.5 else "Ajustado"} |
| Quick Ratio | {f"{m.quick_ratio:.2f}" if m.quick_ratio else "N/A"} | {"Solido" if m.quick_ratio and m.quick_ratio > 1 else "Ajustado"} |
| D/E Ratio | {f"{m.debt_to_equity:.2f}" if m.debt_to_equity else "N/A"} | {"Bajo" if m.debt_to_equity and m.debt_to_equity < 0.5 else "Moderado"} |

---

## 💰 Balance Highlights

| Concepto | Valor |
|----------|-------|
| Revenue (TTM) | {format_currency(analysis.revenue_ttm)} |
| Net Income (TTM) | {format_currency(analysis.net_income_ttm)} |
| Free Cash Flow | {format_currency(analysis.free_cash_flow)} |
| Cash Total | {format_currency(analysis.total_cash)} |
| Deuda Total | {format_currency(analysis.total_debt)} |

"""
        # Posición neta de caja
        if analysis.total_cash and analysis.total_debt:
            net_cash = analysis.total_cash - analysis.total_debt
            if net_cash > 0:
                md += f"\n**Posición neta de caja:** {format_currency(net_cash)} ✅\n"
            else:
                md += f"\n**Deuda neta:** {format_currency(abs(net_cash))}\n"

        # Earnings
        if analysis.earnings and analysis.earnings.next_earnings_date:
            md += f"""
---

## 📅 Próximo Earnings

**Fecha:** {analysis.earnings.next_earnings_date}
"""
            if analysis.earnings.eps_estimate:
                md += f"**EPS Estimado:** ${analysis.earnings.eps_estimate:.2f}\n"

        # Score breakdown
        md += f"""
---

## 🤖 Score IA - Breakdown

| Componente | Score | Peso | Detalle |
|------------|-------|------|---------|
| Fundamental | {ai_score.fundamental_score:.1f}/10 | 20% | ROE, márgenes, ratios |
| Valuación | {ai_score.valuation_score:.1f}/10 | 25% | {ai_score.valuation_vs_sector} |
| Crecimiento | {ai_score.growth_score:.1f}/10 | 20% | {ai_score.growth_outlook} |
| Momentum | {ai_score.momentum_score:.1f}/10 | 15% | {ai_score.momentum_trend} |
| Sentimiento | {ai_score.sentiment_score:.1f}/10 | 10% | {ai_score.sentiment_summary} |
| Calidad | {ai_score.quality_score:.1f}/10 | 10% | FCF, eficiencia |
| **TOTAL** | **{ai_score.total_score}/10** | 100% | |

"""
        # Flags
        if ai_score.flags:
            md += "---\n\n## 🚩 Señales\n\n"
            for flag in ai_score.flags:
                if "OPPORTUNITY" in flag:
                    md += f"🟢 {flag}\n"
                elif "RISK" in flag:
                    md += f"🔴 {flag}\n"
                else:
                    md += f"🟡 {flag}\n"

        # Noticias
        if analysis.news:
            md += "\n---\n\n## 📰 Noticias Recientes\n\n"
            for news in analysis.news[:5]:
                date_str = f"[{news.date}] " if news.date else ""
                md += f"- {date_str}{news.title}\n"

        # Activos relacionados
        if analysis.related_assets:
            md += "\n---\n\n## 🔗 Activos Relacionados\n\n"
            md += "| Activo | Precio | Cambio | Tipo |\n"
            md += "|--------|--------|--------|------|\n"
            for asset in analysis.related_assets[:5]:
                change_emoji = "🟢" if asset.change_percent >= 0 else "🔴"
                md += f"| {asset.name} | ${asset.price:.2f} | {change_emoji} {asset.change_percent:+.2f}% | {asset.relevance} |\n"

        # Disclaimer
        md += """
---

## ⚠️ Disclaimer

Esta idea de trading es generada automáticamente basada en análisis cuantitativo y cualitativo.
**No constituye asesoramiento financiero.** Realice su propia investigación antes de invertir.

*Generado por Stock Screener GARP - Score IA*
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
