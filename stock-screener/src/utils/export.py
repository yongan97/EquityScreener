"""Utilidades de exportación de resultados."""

import json
from pathlib import Path
from datetime import datetime
from typing import Union

import pandas as pd
from loguru import logger

from src.models.stock import ScreenerResult


class Exporter:
    """Exportador de resultados del screener."""
    
    def __init__(self, output_dir: str = "data/outputs"):
        """
        Inicializa el exportador.
        
        Args:
            output_dir: Directorio para guardar outputs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(
        self,
        result: ScreenerResult,
        format: str = "json",
        filename: str = None,
    ) -> Path:
        """
        Exporta resultado en el formato especificado.
        
        Args:
            result: Resultado del screener
            format: Formato (json, csv, xlsx)
            filename: Nombre de archivo (auto-genera si no se especifica)
        
        Returns:
            Path al archivo generado
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screener_{result.config_name}_{timestamp}"
        
        if format == "json":
            return self._export_json(result, filename)
        elif format == "csv":
            return self._export_csv(result, filename)
        elif format == "xlsx":
            return self._export_xlsx(result, filename)
        else:
            raise ValueError(f"Formato no soportado: {format}")
    
    def _export_json(self, result: ScreenerResult, filename: str) -> Path:
        """Exporta a JSON."""
        path = self.output_dir / f"{filename}.json"
        
        with open(path, "w") as f:
            json.dump(result.to_dict(), f, indent=2)
        
        logger.info(f"Exportado a {path}")
        return path
    
    def _export_csv(self, result: ScreenerResult, filename: str) -> Path:
        """Exporta a CSV (solo stocks, aplanado)."""
        path = self.output_dir / f"{filename}.csv"
        
        df = self._result_to_dataframe(result)
        df.to_csv(path, index=False)
        
        logger.info(f"Exportado a {path}")
        return path
    
    def _export_xlsx(self, result: ScreenerResult, filename: str) -> Path:
        """Exporta a Excel con múltiples hojas."""
        path = self.output_dir / f"{filename}.xlsx"
        
        df = self._result_to_dataframe(result)
        
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            # Hoja principal con stocks
            df.to_excel(writer, sheet_name="Stocks", index=False)
            
            # Hoja de resumen
            summary = pd.DataFrame([{
                "Timestamp": result.timestamp.isoformat(),
                "Config": result.config_name,
                "Total Scanned": result.total_scanned,
                "Total Matches": result.total_matches,
                "Execution Time (s)": result.execution_time_seconds,
            }])
            summary.to_excel(writer, sheet_name="Summary", index=False)
            
            # Hoja de errores si hay
            if result.errors:
                errors_df = pd.DataFrame({"Error": result.errors})
                errors_df.to_excel(writer, sheet_name="Errors", index=False)
        
        logger.info(f"Exportado a {path}")
        return path
    
    def _result_to_dataframe(self, result: ScreenerResult) -> pd.DataFrame:
        """Convierte resultado a DataFrame aplanado."""
        rows = []
        
        for stock in result.stocks:
            row = {
                "Symbol": stock.symbol,
                "Name": stock.name,
                "Sector": stock.sector,
                "Industry": stock.industry,
                "Exchange": stock.exchange,
                "Price": stock.price,
                "Market Cap": stock.market_cap,
                "Avg Volume": stock.avg_volume,
                "Score": stock.score,
            }
            
            # Agregar métricas
            metrics = stock.metrics.to_dict()
            for key, value in metrics.items():
                # Convertir nombre de snake_case a Title Case
                col_name = key.replace("_", " ").title()
                row[col_name] = value
            
            # Agregar score breakdown
            for key, value in stock.score_breakdown.items():
                row[f"Score {key.title()}"] = value
            
            rows.append(row)
        
        return pd.DataFrame(rows)


def quick_export(result: ScreenerResult, format: str = "json") -> Path:
    """Helper para exportación rápida."""
    exporter = Exporter()
    return exporter.export(result, format)
