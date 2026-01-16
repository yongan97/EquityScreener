# Agente: Filter Optimizer

## Rol
Optimizar y ajustar filtros del screener según objetivos.

## Capacidades
1. Sugerir ajustes de filtros
2. Backtesting de criterios
3. Análisis de sensibilidad
4. Generación de configuraciones custom

## Input
- Objetivo de inversión (growth/value/balanced)
- Tolerancia al riesgo
- Número deseado de resultados
- Restricciones específicas

## Output
- Configuración optimizada (JSON)
- Impacto estimado de cambios
- Trade-offs identificados

## Estrategias Predefinidas

### Ultra Conservative
```json
{
  "pe_max": 20,
  "peg_max": 0.7,
  "roe_min": 20,
  "current_ratio_min": 2.5,
  "debt_equity_max": 0.2,
  "market_cap_min": 10e9
}
```

### Growth Focused
```json
{
  "pe_max": 40,
  "peg_max": 1.2,
  "eps_growth_5y_min": 15,
  "roe_min": 12,
  "debt_equity_max": 0.8
}
```

### Deep Value
```json
{
  "pe_max": 12,
  "pb_max": 1.5,
  "dividend_yield_min": 2,
  "roe_min": 10,
  "debt_equity_max": 0.4
}
```

## Prompts de Ejemplo

### Ajustar por Resultados
```
Tengo {N} resultados, quiero reducir a ~{M}.
Sugiere qué filtros ajustar manteniendo calidad.
Prioridad: {growth/value/quality}
```

### Crear Config Custom
```
Crea configuración para:
- Perfil: {descripción}
- Sectores preferidos: {lista}
- Rango de market cap: {min}-{max}
- Tolerancia a deuda: {baja/media/alta}
```

## Código de Soporte

```python
def optimize_filters(
    current_config: dict,
    target_results: int,
    current_results: int,
    priority: str = "balanced"
) -> dict:
    """Sugiere ajustes para alcanzar número objetivo de resultados."""
    
    adjustments = {
        "growth": {
            "loosen": ["pe_max", "peg_max", "debt_equity_max"],
            "tighten": ["eps_growth_5y_min"],
        },
        "value": {
            "loosen": ["roe_min", "current_ratio_min"],
            "tighten": ["pe_max", "peg_max"],
        },
        "quality": {
            "loosen": ["pe_max", "market_cap_min"],
            "tighten": ["roe_min", "current_ratio_min", "debt_equity_max"],
        },
        "balanced": {
            "loosen": ["peg_max", "current_ratio_min"],
            "tighten": ["roe_min"],
        },
    }
    
    suggestions = []
    ratio = target_results / current_results
    
    if ratio > 1:
        for metric in adjustments[priority]["loosen"]:
            suggestions.append({
                "metric": metric,
                "action": "loosen",
                "reason": "Aumentar pool de candidatos"
            })
    else:
        for metric in adjustments[priority]["tighten"]:
            suggestions.append({
                "metric": metric,
                "action": "tighten",
                "reason": "Filtrar a mayor calidad"
            })
    
    return {
        "current_results": current_results,
        "target_results": target_results,
        "priority": priority,
        "suggestions": suggestions,
    }
```
