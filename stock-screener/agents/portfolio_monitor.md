# Agente: Portfolio Monitor

## Rol
Monitorear watchlist y alertar sobre cambios relevantes.

## Capacidades
1. Tracking de precios
2. Alertas de métricas
3. Detección de cambios en fundamentos
4. Rebalanceo sugerido

## Input
- Watchlist (lista de símbolos)
- Umbrales de alerta
- Frecuencia de monitoreo

## Output
- Status de cada posición
- Alertas activas
- Cambios desde último check
- Recomendaciones

## Configuración de Alertas

```json
{
  "price_alerts": {
    "drop_pct": -5,
    "rise_pct": 10
  },
  "metric_alerts": {
    "pe_max": 30,
    "peg_max": 1.5,
    "roe_min": 12,
    "debt_equity_max": 0.6
  },
  "fundamental_alerts": {
    "earnings_miss": true,
    "guidance_change": true
  }
}
```

## Prompts de Ejemplo

### Check Diario
```
Revisa mi watchlist: {symbols}
- Cambios de precio significativos
- Alertas de métricas disparadas
- Noticias relevantes
```

### Evaluación de Salida
```
Evalúa si debo salir de {SYMBOL}:
- Razón original de entrada
- Métricas actuales vs entrada
- Cambios en tesis de inversión
```

## Código de Soporte

```python
def monitor_watchlist(symbols: list[str], alerts_config: dict) -> dict:
    """Monitorea watchlist y genera alertas."""
    from src.api import FMPClient
    
    fmp = FMPClient()
    alerts = []
    status = {}
    
    for symbol in symbols:
        try:
            stock = fmp.build_stock(symbol)
            
            stock_alerts = []
            
            # Check métricas
            if stock.metrics.pe_ratio and stock.metrics.pe_ratio > alerts_config["metric_alerts"]["pe_max"]:
                stock_alerts.append(f"P/E alto: {stock.metrics.pe_ratio:.1f}")
            
            if stock.metrics.peg_ratio and stock.metrics.peg_ratio > alerts_config["metric_alerts"]["peg_max"]:
                stock_alerts.append(f"PEG alto: {stock.metrics.peg_ratio:.2f}")
            
            if stock.metrics.roe and stock.metrics.roe < alerts_config["metric_alerts"]["roe_min"] / 100:
                stock_alerts.append(f"ROE bajo: {stock.metrics.roe*100:.1f}%")
            
            status[symbol] = {
                "price": stock.price,
                "metrics": stock.metrics.to_dict(),
                "alerts": stock_alerts,
            }
            
            if stock_alerts:
                alerts.extend([(symbol, a) for a in stock_alerts])
        
        except Exception as e:
            status[symbol] = {"error": str(e)}
    
    return {
        "status": status,
        "alerts": alerts,
        "total_alerts": len(alerts),
    }
```
