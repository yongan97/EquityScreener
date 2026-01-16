#!/usr/bin/env python3
"""Script completo: Screener + Análisis IA + Trade Ideas → Supabase."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger
from dotenv import load_dotenv

from src.core import StockScreener
from src.analysis.analyzer import StockAnalyzer
from src.analysis.ai_scoring import AIScorer
from src.analysis.trade_idea import TradeIdeaGenerator
from src.db import SupabaseClient

load_dotenv()

app = typer.Typer(help="Stock Screener con Análisis IA completo")
console = Console()


@app.command()
def run(
    config: str = typer.Option(
        "config/default.json",
        "--config", "-c",
        help="Archivo de configuración"
    ),
    cleanup: bool = typer.Option(
        False,
        "--cleanup",
        help="Eliminar corridas antiguas"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Output detallado"
    ),
):
    """Ejecuta screener completo con análisis IA y guarda en Supabase."""

    log_level = "DEBUG" if verbose else "INFO"
    logger.remove()
    logger.add(sys.stderr, level=log_level, format="{time:HH:mm:ss} | {level} | {message}")

    console.print("[bold blue]====================================================[/bold blue]")
    console.print("[bold blue]  Stock Screener GARP - AI Analysis[/bold blue]")
    console.print("[bold blue]====================================================[/bold blue]")
    console.print()

    try:
        # 1. Ejecutar screener
        console.print("[cyan]Paso 1/4:[/cyan] Ejecutando screener...")
        with StockScreener(config_path=config) as screener:
            result = screener.run()

        console.print(f"  [green]OK[/green] {result.total_matches} stocks encontrados de {result.total_scanned} escaneados")

        if not result.stocks:
            console.print("[yellow]No se encontraron stocks que pasen los filtros[/yellow]")
            return

        # 2. Analizar cada stock con IA
        console.print(f"\n[cyan]Paso 2/4:[/cyan] Analizando {len(result.stocks)} stocks con Score IA...")

        analyzer = StockAnalyzer()
        scorer = AIScorer()
        idea_gen = TradeIdeaGenerator()

        analyses = {}  # symbol -> (analysis, ai_score, trade_idea_md)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analizando...", total=len(result.stocks))

            for stock in result.stocks:
                try:
                    progress.update(task, description=f"Analizando {stock.symbol}...")

                    # Análisis completo
                    analysis = analyzer.analyze(stock.symbol)

                    # Score IA
                    ai_score = scorer.score(stock, analysis)

                    # Trade Idea
                    trade_idea = idea_gen.generate(stock, analysis, ai_score)

                    analyses[stock.symbol] = (analysis, ai_score, trade_idea.markdown)

                    progress.advance(task)

                except Exception as e:
                    logger.warning(f"Error analizando {stock.symbol}: {e}")
                    progress.advance(task)
                    continue

        analyzer.close()
        console.print(f"  [green]OK[/green] {len(analyses)} stocks analizados exitosamente")

        # 3. Guardar en Supabase
        console.print(f"\n[cyan]Paso 3/4:[/cyan] Guardando en Supabase...")

        db = SupabaseClient()
        run_id = db.save_run_with_analysis(result, analyses)

        console.print(f"  [green]OK[/green] Guardado con Run ID: {run_id}")

        # 4. Cleanup opcional
        if cleanup:
            console.print(f"\n[cyan]Paso 4/4:[/cyan] Limpiando corridas antiguas...")
            deleted = db.delete_old_runs(keep_count=30)
            console.print(f"  [green]OK[/green] {deleted} corridas eliminadas")

        # Resumen final
        console.print()
        console.print("[bold green]====================================================[/bold green]")
        console.print("[bold green]  Analysis Complete![/bold green]")
        console.print("[bold green]====================================================[/bold green]")
        console.print()

        # Mostrar top 5
        console.print("[bold]Top 5 Stocks por Score IA:[/bold]")
        console.print()

        sorted_stocks = sorted(
            [(s, analyses.get(s.symbol)) for s in result.stocks if s.symbol in analyses],
            key=lambda x: x[1][1].total_score if x[1] else 0,
            reverse=True
        )

        for i, (stock, data) in enumerate(sorted_stocks[:5], 1):
            if data:
                analysis, ai_score, _ = data
                rec = "[green]BUY[/green]" if ai_score.total_score >= 6.5 else "[yellow]HOLD[/yellow]" if ai_score.total_score >= 5.5 else "[orange3]WATCH[/orange3]"
                console.print(
                    f"  {i}. [cyan]{stock.symbol:6}[/cyan] | "
                    f"Score IA: [bold]{ai_score.total_score:.1f}[/bold] | "
                    f"{rec} | "
                    f"${stock.price:.2f}"
                )

        console.print()
        console.print(f"[dim]Ver resultados en el frontend: http://localhost:3005[/dim]")
        console.print()

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Error en análisis completo")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
