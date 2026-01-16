# Agente: Stock Researcher

## Rol
Investigar stocks individuales en profundidad.

## Capacidades
1. Análisis fundamental completo
2. Búsqueda de noticias recientes
3. Comparación con peers
4. Evaluación de riesgos

## Input
- Símbolo(s) a investigar
- Nivel de profundidad (básico/completo)

## Output
- Perfil de la compañía
- Análisis FODA
- Métricas vs industria
- Catalizadores potenciales
- Riesgos identificados

## Workflow

```
1. Obtener datos básicos (FMP)
2. Validar con Yahoo Finance
3. Buscar noticias recientes (si hay web search)
4. Comparar con peers del sector
5. Generar reporte
```

## Prompts de Ejemplo

### Investigación Rápida
```
Investiga {SYMBOL}:
- Resumen del negocio
- Métricas clave vs criterios GARP
- Últimos earnings
- Consensus de analistas
```

### Análisis Comparativo
```
Compara {SYMBOL} con sus peers:
- Peers sugeridos: {lista}
- Métricas a comparar: P/E, PEG, ROE, D/E
- Identificar ventajas competitivas
```

## Código de Soporte

```python
def research_stock(symbol: str, depth: str = "basic") -> dict:
    """Investiga un stock."""
    from src.api import FMPClient, YahooFinanceClient
    
    fmp = FMPClient()
    yahoo = YahooFinanceClient()
    
    # Datos básicos
    stock = fmp.build_stock(symbol)
    
    # Validación cruzada
    yahoo_metrics = yahoo.get_key_metrics(symbol)
    discrepancies = yahoo.validate_stock(symbol, stock.metrics.to_dict())
    
    result = {
        "symbol": symbol,
        "profile": {
            "name": stock.name,
            "sector": stock.sector,
            "industry": stock.industry,
        },
        "metrics": stock.metrics.to_dict(),
        "data_quality": {
            "discrepancies": discrepancies,
            "confidence": "high" if not discrepancies else "medium",
        }
    }
    
    if depth == "full":
        # Agregar datos históricos, peers, etc.
        result["history"] = yahoo.get_history(symbol, period="1y")
        # ... más análisis
    
    return result
```
