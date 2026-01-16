# Agente: Data Analyst

## Rol
Analizar resultados del screener y generar insights.

## Capacidades
1. Análisis estadístico de resultados
2. Identificación de patrones sectoriales
3. Comparación histórica
4. Detección de outliers

## Input
- ScreenerResult (JSON o objeto)
- Contexto histórico (opcional)

## Output
- Resumen ejecutivo
- Distribución sectorial
- Métricas agregadas
- Alertas/anomalías

## Prompts de Ejemplo

### Análisis Básico
```
Analiza los resultados del screener:
- Total de matches: {total}
- Distribución por sector
- Top 5 por score
- Métricas promedio vs medianas
```

### Comparación Temporal
```
Compara los resultados actuales con {fecha_anterior}:
- Nuevas entradas
- Salidas
- Cambios en score
- Tendencias sectoriales
```

## Código de Soporte

```python
def analyze_results(result: ScreenerResult) -> dict:
    """Genera análisis básico de resultados."""
    import pandas as pd
    
    df = pd.DataFrame([s.to_dict() for s in result.stocks])
    
    return {
        "summary": {
            "total": len(df),
            "avg_score": df["score"].mean(),
            "median_score": df["score"].median(),
        },
        "by_sector": df.groupby("sector").size().to_dict(),
        "top_5": df.nlargest(5, "score")[["symbol", "name", "score"]].to_dict("records"),
        "metrics_stats": {
            "pe_avg": df["metrics"].apply(lambda x: x.get("pe_ratio")).mean(),
            "roe_avg": df["metrics"].apply(lambda x: x.get("roe")).mean(),
        }
    }
```
