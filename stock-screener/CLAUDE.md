# CLAUDE.md - Instrucciones del Proyecto Stock Screener

## Contexto
Screener cuantitativo GARP (Growth At Reasonable Price) para acciones US.

## Stack
- **Lenguaje**: Python 3.11+
- **API Principal**: Financial Modeling Prep (FMP) - key en `.env`
- **Backup APIs**: Finviz (scraping), Yahoo Finance (yfinance)
- **DB**: SQLite para cache local
- **Output**: CSV, JSON, Excel

## Estructura
```
src/
├── api/          # Clientes de APIs (fmp.py, finviz.py, yahoo.py)
├── core/         # Lógica del screener (screener.py, filters.py)
├── models/       # Dataclasses (stock.py, criteria.py)
└── utils/        # Helpers (cache.py, export.py)
agents/           # Agentes especializados
config/           # Configuración de filtros
scripts/          # Scripts de ejecución
```

## Criterios del Screener
| Filtro | Valor | Tipo |
|--------|-------|------|
| Market Cap | >$2B | Operabilidad |
| Volumen | >300K | Operabilidad |
| Precio | >$5 | Operabilidad |
| P/E | >0 | Valuación |
| PEG | <1 | Valuación |
| EPS Growth 5Y | >0% | Crecimiento |
| ROE | >15% | Rentabilidad |
| Current Ratio | >1.5 | Liquidez |
| Quick Ratio | >1 | Liquidez |
| D/E | <0.5 | Solvencia |

## Comandos Frecuentes
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar screener
python scripts/run_screener.py

# Tests
pytest tests/ -v

# Lint
ruff check src/
```

## APIs - Endpoints Clave

### Financial Modeling Prep (Principal)
```
GET /api/v3/stock-screener?apikey={key}
    &marketCapMoreThan=2000000000
    &priceMoreThan=5
    &volumeMoreThan=300000
    &isActivelyTrading=true

GET /api/v3/ratios/{symbol}?apikey={key}
GET /api/v3/key-metrics/{symbol}?apikey={key}
```

### Finviz (Backup/Validación)
Scraping de screener con filtros equivalentes.

## Reglas para Claude
1. **No hardcodear API keys** - usar `.env`
2. **Cachear respuestas** - evitar rate limits
3. **Logging estructurado** - usar `loguru`
4. **Type hints** - obligatorios en todas las funciones
5. **Docstrings** - formato Google
6. **Errores** - manejar con excepciones custom

## Rate Limits
- FMP: 300 req/min (plan básico)
- Finviz: 1 req/5s (scraping responsable)
- Yahoo: Sin límite oficial, usar delays

## Output Esperado
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "total_matches": 45,
  "stocks": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "sector": "Technology",
      "metrics": {...},
      "score": 8.5
    }
  ]
}
```
