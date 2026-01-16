# APIs Financieras - Guía de Referencia

## 1. Financial Modeling Prep (FMP) - Principal

**Sitio**: https://financialmodelingprep.com/developer  
**Pricing**: Free tier (250 req/día), Starter ($15/mes), Pro ($50/mes)

### Endpoints Clave

#### Stock Screener
```
GET /api/v3/stock-screener
```

Parámetros:
| Param | Tipo | Descripción |
|-------|------|-------------|
| marketCapMoreThan | int | Market cap mínimo |
| marketCapLowerThan | int | Market cap máximo |
| priceMoreThan | float | Precio mínimo |
| priceLowerThan | float | Precio máximo |
| volumeMoreThan | int | Volumen mínimo |
| dividendMoreThan | float | Dividend yield mínimo |
| isEtf | bool | Filtrar ETFs |
| isFund | bool | Filtrar fondos |
| isActivelyTrading | bool | Solo activas |
| sector | string | Filtrar por sector |
| industry | string | Filtrar por industria |
| exchange | string | NYSE,NASDAQ,etc |

#### Ratios Financieros
```
GET /api/v3/ratios/{symbol}
```

Retorna: P/E, PEG, P/B, ROE, ROA, Current Ratio, Quick Ratio, D/E, etc.

#### Key Metrics
```
GET /api/v3/key-metrics/{symbol}
```

Retorna: Market Cap, Enterprise Value, Revenue per Share, etc.

#### Financial Growth
```
GET /api/v3/financial-growth/{symbol}
```

Retorna: Revenue Growth, EPS Growth, Net Income Growth, etc.

#### Company Profile
```
GET /api/v3/profile/{symbol}
```

Retorna: Nombre, Sector, Industry, Description, CEO, etc.

### Ejemplo de Uso
```python
import requests

API_KEY = "tu_api_key"
BASE = "https://financialmodelingprep.com/api/v3"

# Screener básico
params = {
    "apikey": API_KEY,
    "marketCapMoreThan": 2000000000,
    "priceMoreThan": 5,
    "volumeMoreThan": 300000,
    "isActivelyTrading": "true",
}
response = requests.get(f"{BASE}/stock-screener", params=params)
stocks = response.json()
```

---

## 2. Finviz - Backup (Scraping)

**Sitio**: https://finviz.com/screener.ashx  
**Pricing**: Gratis (con limitaciones), Elite ($24.96/mes)

### Filtros Disponibles

| Filtro | Código | Valores |
|--------|--------|---------|
| Market Cap | cap_ | nano, micro, small, mid, large, mega |
| P/E | fa_pe_ | low, profitable, high, u5, u10, etc |
| PEG | fa_peg_ | low, u1, u2, o1, etc |
| ROE | fa_roe_ | pos, neg, o5, o10, o15, o20, etc |
| Current Ratio | fa_curratio_ | o1, o1.5, o2, etc |
| Quick Ratio | fa_quickratio_ | o1, o1.5, etc |
| Debt/Equity | fa_debteq_ | u0.5, u1, o1, etc |

### Ejemplo de URL
```
https://finviz.com/screener.ashx?v=111&f=cap_largeover,fa_pe_profitable,fa_peg_low,fa_roe_o15
```

### Notas de Scraping
- Usar delays entre requests (5+ segundos)
- Respetar robots.txt
- User-Agent apropiado
- Parsear con BeautifulSoup

---

## 3. Yahoo Finance (yfinance) - Validación

**Librería**: `pip install yfinance`  
**Pricing**: Gratis (uso responsable)

### Uso Básico
```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

# Info general
info = ticker.info

# Métricas clave
pe = info.get("trailingPE")
peg = info.get("pegRatio")
roe = info.get("returnOnEquity")

# Historial de precios
hist = ticker.history(period="1y")

# Financials
financials = ticker.financials
balance = ticker.balance_sheet
```

### Campos Útiles de `info`
- `trailingPE`, `forwardPE`
- `pegRatio`
- `priceToBook`
- `returnOnEquity`, `returnOnAssets`
- `currentRatio`, `quickRatio`
- `debtToEquity`
- `marketCap`
- `averageVolume`

---

## 4. Comparación de APIs

| Característica | FMP | Finviz | Yahoo |
|---------------|-----|--------|-------|
| Screener nativo | ✓ | ✓ | ✗ |
| Datos en tiempo real | ✓ | ✓ | ~ |
| Historial de precios | ✓ | ✗ | ✓ |
| Ratios financieros | ✓ | Parcial | ✓ |
| Rate limit | 250/día (free) | ~1/5s | Flexible |
| Facilidad de uso | Alta | Media | Alta |
| Costo | $$$ | Free/$$$ | Free |

---

## 5. Estrategia de Uso Recomendada

1. **FMP como fuente principal**
   - Screener inicial con filtros básicos
   - Obtener ratios y métricas detalladas

2. **Yahoo Finance para validación**
   - Cruzar datos de FMP
   - Obtener historial de precios
   - Backup si FMP falla

3. **Finviz como backup del screener**
   - Si FMP está caído o excede rate limit
   - Validación cruzada de resultados

4. **Caching agresivo**
   - Cachear todo por 24h mínimo
   - Ratios y métricas cambian poco día a día
   - Reducir costos y rate limits
