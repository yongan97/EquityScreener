#!/usr/bin/env python3
"""Script para analizar stocks con Score IA completo."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from loguru import logger
from dotenv import load_dotenv

from src.core import StockScreener
from src.analysis.analyzer import StockAnalyzer
from src.analysis.ai_scoring import AIScorer

load_dotenv()

app = typer.Typer(help="Análisis de stocks con Score IA")
console = Console()


def format_currency(value: float) -> str:
    """Formatea valores en billones/millones."""
    if value is None:
        return "-"
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
        return "-"
    return f"{value*100:.1f}%" if abs(value) < 1 else f"{value:.1f}%"


@app.command()
def analyze(
    symbol: str = typer.Argument(None, help="Símbolo a analizar (o 'all' para top del screener)"),
    top: int = typer.Option(5, "--top", "-t", help="Número de stocks a analizar"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Output detallado"),
):
    """Analiza un stock o los top del screener con Score IA."""

    log_level = "DEBUG" if verbose else "INFO"
    logger.remove()
    logger.add(sys.stderr, level=log_level)

    analyzer = StockAnalyzer()
    scorer = AIScorer()

    try:
        if symbol and symbol.lower() != "all":
            # Analizar un solo stock
            _analyze_single(symbol.upper(), analyzer, scorer)
        else:
            # Analizar top stocks del screener
            _analyze_top(top, analyzer, scorer)

    finally:
        analyzer.close()


def _analyze_single(symbol: str, analyzer: StockAnalyzer, scorer: AIScorer):
    """Analiza un solo stock."""
    console.print(f"\n[bold blue]Analizando {symbol}...[/bold blue]\n")

    # Obtener datos básicos con yfinance
    import yfinance as yf
    from src.models.stock import Stock, StockMetrics

    ticker = yf.Ticker(symbol)
    info = ticker.info or {}

    # Crear Stock con métricas
    metrics = StockMetrics(
        pe_ratio=info.get("trailingPE"),
        peg_ratio=info.get("pegRatio"),
        roe=info.get("returnOnEquity"),
        roa=info.get("returnOnAssets"),
        current_ratio=info.get("currentRatio"),
        quick_ratio=info.get("quickRatio"),
        debt_to_equity=info.get("debtToEquity", 0) / 100 if info.get("debtToEquity") else None,
        eps_growth_5y=info.get("earningsGrowth"),
        gross_margin=info.get("grossMargins"),
        net_margin=info.get("profitMargins"),
    )

    stock = Stock(
        symbol=symbol,
        name=info.get("shortName", symbol),
        sector=info.get("sector", "Unknown"),
        industry=info.get("industry", "Unknown"),
        exchange=info.get("exchange", "NASDAQ"),
        price=info.get("currentPrice", 0),
        market_cap=info.get("marketCap", 0),
        avg_volume=info.get("averageVolume", 0),
        metrics=metrics,
    )

    # Análisis completo
    analysis = analyzer.analyze(symbol)

    # Score IA
    ai_score = scorer.score(stock, analysis)

    # Mostrar resultados
    _display_analysis(stock, analysis, ai_score)


def _analyze_top(top: int, analyzer: StockAnalyzer, scorer: AIScorer):
    """Analiza los top stocks del screener."""
    console.print(f"\n[bold blue]Ejecutando screener y analizando top {top}...[/bold blue]\n")

    # Ejecutar screener
    with StockScreener() as screener:
        result = screener.run()

    if not result.stocks:
        console.print("[yellow]No se encontraron stocks que pasen los filtros[/yellow]")
        return

    # Tomar top stocks
    stocks_to_analyze = result.stocks[:top]

    console.print(f"[green]Encontrados {result.total_matches} stocks. Analizando top {len(stocks_to_analyze)}...[/green]\n")

    # Tabla resumen
    summary_table = Table(
        title="Score IA - Resumen",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )

    summary_table.add_column("Symbol", style="cyan", width=8)
    summary_table.add_column("Name", width=25)
    summary_table.add_column("Score IA", justify="center", width=10)
    summary_table.add_column("Fund", justify="center", width=6)
    summary_table.add_column("Value", justify="center", width=6)
    summary_table.add_column("Growth", justify="center", width=6)
    summary_table.add_column("Mom", justify="center", width=6)
    summary_table.add_column("Sent", justify="center", width=6)
    summary_table.add_column("PEG", justify="center", width=6)
    summary_table.add_column("Outlook", width=15)

    for stock in stocks_to_analyze:
        try:
            analysis = analyzer.analyze(stock.symbol)
            ai_score = scorer.score(stock, analysis)

            # Color del score
            score_color = "green" if ai_score.total_score >= 7 else "yellow" if ai_score.total_score >= 5 else "red"

            summary_table.add_row(
                stock.symbol,
                stock.name[:25],
                f"[{score_color}]{ai_score.total_score:.1f}[/{score_color}]",
                f"{ai_score.fundamental_score:.1f}",
                f"{ai_score.valuation_score:.1f}",
                f"{ai_score.growth_score:.1f}",
                f"{ai_score.momentum_score:.1f}",
                f"{ai_score.sentiment_score:.1f}",
                f"{analysis.peg_finviz:.2f}" if analysis.peg_finviz else "-",
                ai_score.growth_outlook,
            )

        except Exception as e:
            logger.warning(f"Error analizando {stock.symbol}: {e}")
            continue

    console.print(summary_table)
    console.print()

    # Mostrar detalle del #1
    if stocks_to_analyze:
        console.print("[bold]Detalle del #1:[/bold]\n")
        top_stock = stocks_to_analyze[0]
        analysis = analyzer.analyze(top_stock.symbol)
        ai_score = scorer.score(top_stock, analysis)
        _display_analysis(top_stock, analysis, ai_score)


def _display_analysis(stock, analysis, ai_score):
    """Muestra análisis completo de un stock."""

    # Header
    score_color = "green" if ai_score.total_score >= 7 else "yellow" if ai_score.total_score >= 5 else "red"
    header = f"[bold]{stock.symbol}[/bold] - {stock.name}\n"
    header += f"Sector: {stock.sector} | Industry: {stock.industry}\n"
    header += f"[{score_color}]Score IA: {ai_score.total_score}/10[/{score_color}]"

    console.print(Panel(header, title="Stock Analysis", box=box.DOUBLE))

    # Score breakdown
    score_table = Table(title="Score IA Breakdown", box=box.SIMPLE)
    score_table.add_column("Component", style="cyan")
    score_table.add_column("Score", justify="center")
    score_table.add_column("Weight", justify="center")
    score_table.add_column("Details")

    score_table.add_row("Fundamental", f"{ai_score.fundamental_score:.1f}/10", "20%", "ROE, margins, ratios")
    score_table.add_row("Valuation", f"{ai_score.valuation_score:.1f}/10", "25%", ai_score.valuation_vs_sector)
    score_table.add_row("Growth", f"{ai_score.growth_score:.1f}/10", "20%", ai_score.growth_outlook)
    score_table.add_row("Momentum", f"{ai_score.momentum_score:.1f}/10", "15%", ai_score.momentum_trend)
    score_table.add_row("Sentiment", f"{ai_score.sentiment_score:.1f}/10", "10%", ai_score.sentiment_summary)
    score_table.add_row("Quality", f"{ai_score.quality_score:.1f}/10", "10%", "FCF, efficiency")

    console.print(score_table)

    # Finviz data
    if analysis.peg_finviz or analysis.fwd_pe:
        console.print("\n[bold cyan]Finviz Valuation:[/bold cyan]")
        console.print(f"  PEG: {analysis.peg_finviz:.2f}" if analysis.peg_finviz else "  PEG: -")
        console.print(f"  Forward P/E: {analysis.fwd_pe:.1f}" if analysis.fwd_pe else "  Forward P/E: -")
        console.print(f"  EPS This Year: {format_percent(analysis.eps_this_year)}")
        console.print(f"  EPS Next Year: {format_percent(analysis.eps_next_year)}")

    # Balance highlights
    console.print("\n[bold cyan]Balance Highlights:[/bold cyan]")
    console.print(f"  Revenue TTM: {format_currency(analysis.revenue_ttm)}")
    console.print(f"  Net Income: {format_currency(analysis.net_income_ttm)}")
    console.print(f"  Free Cash Flow: {format_currency(analysis.free_cash_flow)}")
    console.print(f"  Total Cash: {format_currency(analysis.total_cash)}")
    console.print(f"  Total Debt: {format_currency(analysis.total_debt)}")

    # Earnings
    if analysis.earnings and analysis.earnings.next_earnings_date:
        console.print("\n[bold cyan]Earnings:[/bold cyan]")
        console.print(f"  Next Earnings: {analysis.earnings.next_earnings_date}")
        if analysis.earnings.eps_estimate:
            console.print(f"  EPS Estimate: ${analysis.earnings.eps_estimate:.2f}")

    # News
    if analysis.news:
        console.print("\n[bold cyan]Recent News:[/bold cyan]")
        for i, news in enumerate(analysis.news[:5], 1):
            date_str = f"[{news.date}]" if news.date else ""
            console.print(f"  {i}. {date_str} {news.title[:70]}...")

    # Related assets
    if analysis.related_assets:
        console.print("\n[bold cyan]Related Assets:[/bold cyan]")
        for asset in analysis.related_assets[:5]:
            change_color = "green" if asset.change_percent >= 0 else "red"
            console.print(
                f"  {asset.name}: ${asset.price:.2f} "
                f"[{change_color}]({asset.change_percent:+.2f}%)[/{change_color}] "
                f"[dim]({asset.relevance})[/dim]"
            )

    # Flags
    if ai_score.flags:
        console.print("\n[bold cyan]Flags:[/bold cyan]")
        for flag in ai_score.flags:
            if "OPPORTUNITY" in flag:
                console.print(f"  [green]{flag}[/green]")
            elif "RISK" in flag:
                console.print(f"  [red]{flag}[/red]")
            else:
                console.print(f"  [yellow]{flag}[/yellow]")

    console.print()


if __name__ == "__main__":
    app()
