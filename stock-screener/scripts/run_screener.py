#!/usr/bin/env python3
"""Script principal para ejecutar el screener."""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from rich.console import Console
from rich.table import Table
from loguru import logger
from dotenv import load_dotenv

from src.core import StockScreener
from src.utils.export import Exporter

# Cargar variables de entorno
load_dotenv()

# CLI
app = typer.Typer(help="Stock Screener GARP")
console = Console()


@app.command()
def run(
    config: str = typer.Option(
        "config/default.json",
        "--config", "-c",
        help="Archivo de configuración"
    ),
    output: str = typer.Option(
        None,
        "--output", "-o",
        help="Archivo de salida (extensión determina formato)"
    ),
    format: str = typer.Option(
        "json",
        "--format", "-f",
        help="Formato de salida: json, csv, xlsx"
    ),
    limit: int = typer.Option(
        None,
        "--limit", "-l",
        help="Limitar número de stocks a procesar (para testing)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Output detallado"
    ),
):
    """Ejecuta el screener con la configuración especificada."""
    
    # Configurar logging
    log_level = "DEBUG" if verbose else "INFO"
    logger.remove()
    logger.add(sys.stderr, level=log_level)
    
    console.print(f"[bold blue]Stock Screener GARP[/bold blue]")
    console.print(f"Config: {config}")
    
    try:
        with StockScreener(config_path=config) as screener:
            # Ejecutar
            with console.status("[bold green]Ejecutando screener..."):
                result = screener.run(limit=limit)
            
            # Mostrar resumen
            console.print(f"\n[bold]Resultados:[/bold]")
            console.print(f"  Scanned: {result.total_scanned}")
            console.print(f"  Matches: {result.total_matches}")
            console.print(f"  Time: {result.execution_time_seconds}s")
            
            # Mostrar top 10 en tabla
            if result.stocks:
                table = Table(title="Top 10 Stocks")
                table.add_column("Symbol", style="cyan")
                table.add_column("Name", style="white")
                table.add_column("Score", style="green")
                table.add_column("P/E", style="yellow")
                table.add_column("PEG", style="yellow")
                table.add_column("ROE", style="magenta")
                
                for stock in result.stocks[:10]:
                    table.add_row(
                        stock.symbol,
                        stock.name[:30],
                        f"{stock.score:.1f}" if stock.score else "-",
                        f"{stock.metrics.pe_ratio:.1f}" if stock.metrics.pe_ratio else "-",
                        f"{stock.metrics.peg_ratio:.2f}" if stock.metrics.peg_ratio else "-",
                        f"{stock.metrics.roe*100:.1f}%" if stock.metrics.roe else "-",
                    )
                
                console.print(table)
            
            # Exportar
            if output:
                # Detectar formato por extensión
                ext = Path(output).suffix.lower()
                if ext in [".json", ".csv", ".xlsx"]:
                    format = ext[1:]
                
                exporter = Exporter()
                path = exporter.export(result, format=format, filename=Path(output).stem)
                console.print(f"\n[green]Exportado a: {path}[/green]")
            else:
                # Exportar a JSON por defecto
                exporter = Exporter()
                path = exporter.export(result, format=format)
                console.print(f"\n[green]Exportado a: {path}[/green]")
            
            # Errores
            if result.errors:
                console.print(f"\n[yellow]Warnings: {len(result.errors)}[/yellow]")
                if verbose:
                    for err in result.errors[:10]:
                        console.print(f"  - {err}")
    
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Error ejecutando screener")
        raise typer.Exit(1)


@app.command()
def validate(
    symbol: str = typer.Argument(..., help="Símbolo a validar"),
):
    """Valida un símbolo específico contra los criterios."""
    load_dotenv()
    
    from src.api import FMPClient
    from src.core.filters import FilterEngine
    import json
    
    console.print(f"[bold]Validando {symbol}...[/bold]")
    
    with open("config/default.json") as f:
        config = json.load(f)
    
    fmp = FMPClient()
    filter_engine = FilterEngine(config)
    
    try:
        stock = fmp.build_stock(symbol)
        
        # Mostrar métricas
        console.print(f"\n[cyan]{stock.name}[/cyan]")
        console.print(f"Sector: {stock.sector}")
        console.print(f"Price: ${stock.price:.2f}")
        console.print(f"Market Cap: ${stock.market_cap/1e9:.2f}B")
        
        console.print(f"\n[bold]Métricas:[/bold]")
        for key, value in stock.metrics.to_dict().items():
            console.print(f"  {key}: {value}")
        
        # Evaluar filtros
        console.print(f"\n[bold]Filtros:[/bold]")
        evaluation = filter_engine.evaluate(stock)
        
        for filter_name, passed in evaluation.items():
            status = "[green]✓[/green]" if passed else "[red]✗[/red]"
            console.print(f"  {status} {filter_name}")
        
        # Resultado final
        passes = filter_engine.passes_all(stock)
        if passes:
            console.print(f"\n[green bold]✓ PASA todos los filtros[/green bold]")
        else:
            failing = filter_engine.get_failing_filters(stock)
            console.print(f"\n[red bold]✗ NO PASA ({len(failing)} filtros)[/red bold]")
    
    finally:
        fmp.close()


@app.command()
def list_configs():
    """Lista configuraciones disponibles."""
    config_dir = Path("config")
    
    console.print("[bold]Configuraciones disponibles:[/bold]")
    
    for f in sorted(config_dir.glob("*.json")):
        import json
        with open(f) as fp:
            config = json.load(fp)
        
        console.print(f"\n[cyan]{f.name}[/cyan]")
        console.print(f"  Name: {config.get('name', '-')}")
        console.print(f"  Description: {config.get('description', '-')}")


if __name__ == "__main__":
    app()
