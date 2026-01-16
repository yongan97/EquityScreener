#!/usr/bin/env python3
"""Script para ejecutar el screener y guardar resultados en Supabase.

Este script está diseñado para ejecutarse en GitHub Actions como cron job.
Ejecuta el screener y persiste los resultados en Supabase para que el
frontend de Vercel pueda mostrarlos.

Uso:
    python scripts/run_screener_web.py [--config CONFIG] [--cleanup]

Variables de entorno requeridas:
    - FMP_API_KEY: API key de Financial Modeling Prep
    - SUPABASE_URL: URL del proyecto Supabase
    - SUPABASE_KEY: Service key de Supabase (con permisos de escritura)
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from loguru import logger
from dotenv import load_dotenv

from src.core import StockScreener
from src.db import SupabaseClient

# Cargar variables de entorno
load_dotenv()

app = typer.Typer(help="Stock Screener Web - Guarda resultados en Supabase")


@app.command()
def run(
    config: str = typer.Option(
        "config/default.json",
        "--config", "-c",
        help="Archivo de configuración del screener"
    ),
    cleanup: bool = typer.Option(
        False,
        "--cleanup",
        help="Eliminar corridas antiguas (mantiene las últimas 30)"
    ),
    keep_runs: int = typer.Option(
        30,
        "--keep-runs",
        help="Número de corridas a mantener al hacer cleanup"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Output detallado"
    ),
):
    """Ejecuta el screener y guarda los resultados en Supabase."""

    # Configurar logging
    log_level = "DEBUG" if verbose else "INFO"
    logger.remove()
    logger.add(sys.stderr, level=log_level, format="{time:HH:mm:ss} | {level} | {message}")

    logger.info("=" * 50)
    logger.info("Stock Screener Web - Iniciando")
    logger.info("=" * 50)
    logger.info(f"Config: {config}")

    try:
        # 1. Ejecutar screener
        logger.info("Ejecutando screener...")
        with StockScreener(config_path=config) as screener:
            result = screener.run()

        logger.info(f"Screener completado:")
        logger.info(f"  - Stocks escaneados: {result.total_scanned}")
        logger.info(f"  - Stocks que pasan filtros: {result.total_matches}")
        logger.info(f"  - Tiempo de ejecución: {result.execution_time_seconds:.1f}s")

        if result.errors:
            logger.warning(f"  - Errores: {len(result.errors)}")

        # 2. Guardar en Supabase
        logger.info("Conectando a Supabase...")
        db = SupabaseClient()

        logger.info("Guardando resultados en Supabase...")
        run_id = db.save_run(result)

        logger.info(f"Guardado exitoso!")
        logger.info(f"  - Run ID: {run_id}")
        logger.info(f"  - Stocks guardados: {result.total_matches}")

        # 3. Cleanup opcional
        if cleanup:
            logger.info(f"Ejecutando cleanup (manteniendo últimas {keep_runs} corridas)...")
            deleted = db.delete_old_runs(keep_count=keep_runs)
            logger.info(f"  - Corridas eliminadas: {deleted}")

        # 4. Mostrar top 5 stocks
        if result.stocks:
            logger.info("")
            logger.info("Top 5 stocks:")
            for i, stock in enumerate(result.stocks[:5], 1):
                score = f"{stock.score:.1f}" if stock.score else "-"
                logger.info(f"  {i}. {stock.symbol:6} | {stock.name[:25]:25} | Score: {score}")

        logger.info("")
        logger.info("=" * 50)
        logger.info("Screener Web completado exitosamente")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"Error: {e}")
        logger.exception("Stack trace:")
        raise typer.Exit(1)


@app.command()
def test_connection():
    """Prueba la conexión a Supabase."""
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")

    logger.info("Probando conexión a Supabase...")

    try:
        db = SupabaseClient()

        # Intentar obtener la última corrida
        latest = db.get_latest_run()

        if latest:
            logger.info(f"Conexión exitosa!")
            logger.info(f"Última corrida:")
            logger.info(f"  - ID: {latest['id']}")
            logger.info(f"  - Config: {latest['config_name']}")
            logger.info(f"  - Fecha: {latest['created_at']}")
            logger.info(f"  - Matches: {latest['total_matches']}")
        else:
            logger.info("Conexión exitosa! (No hay corridas previas)")

    except Exception as e:
        logger.error(f"Error de conexión: {e}")
        raise typer.Exit(1)


@app.command()
def cleanup(
    keep_runs: int = typer.Option(
        30,
        "--keep-runs", "-k",
        help="Número de corridas a mantener"
    ),
):
    """Elimina corridas antiguas de la base de datos."""
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")

    logger.info(f"Ejecutando cleanup (manteniendo últimas {keep_runs} corridas)...")

    try:
        db = SupabaseClient()
        deleted = db.delete_old_runs(keep_count=keep_runs)
        logger.info(f"Corridas eliminadas: {deleted}")

    except Exception as e:
        logger.error(f"Error: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
