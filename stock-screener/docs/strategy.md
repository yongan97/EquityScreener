# Estrategia GARP - Growth At Reasonable Price

## Concepto

GARP combina elementos de **Value Investing** y **Growth Investing**, buscando empresas con:
- Crecimiento de ganancias consistente
- Valuación razonable (no sobrepagar por el crecimiento)
- Fundamentos sólidos

Popularizada por **Peter Lynch** (Fidelity Magellan Fund).

---

## Criterios del Screener

### 1. Operabilidad (Filtros Básicos)

| Métrica | Criterio | Razón |
|---------|----------|-------|
| Market Cap | > $2B | Evitar small caps volátiles |
| Volumen Promedio | > 300K | Liquidez para entrar/salir |
| Precio | > $5 | Evitar penny stocks |

### 2. Valuación

| Métrica | Criterio | Razón |
|---------|----------|-------|
| P/E | > 0 | Empresa rentable |
| PEG | < 1 | Crecimiento justifica el precio |

**PEG Ratio**: P/E dividido por tasa de crecimiento esperada.
- PEG < 1: Subvaluada relativo al crecimiento
- PEG = 1: Valuación justa
- PEG > 1: Potencialmente cara

### 3. Crecimiento

| Métrica | Criterio | Razón |
|---------|----------|-------|
| EPS Growth 5Y | > 0% | Tendencia positiva de ganancias |

Idealmente buscar crecimiento de 10-20% anual.

### 4. Rentabilidad

| Métrica | Criterio | Razón |
|---------|----------|-------|
| ROE | > 15% | Alta eficiencia del capital |

ROE alto indica:
- Buenos márgenes
- Ventajas competitivas (moat)
- Management eficiente

### 5. Solidez Financiera

| Métrica | Criterio | Razón |
|---------|----------|-------|
| Current Ratio | > 1.5 | Liquidez holgada |
| Quick Ratio | > 1 | Liquidez sin inventarios |
| D/E | < 0.5 | Bajo apalancamiento |

---

## Cálculo del Score

El sistema asigna puntos (0-10) en 4 categorías:

### Valuación (25%)
- PEG ≤ 0.5: +3 puntos
- PEG ≤ 0.75: +2 puntos
- PEG ≤ 1: +1 punto
- P/E entre 10-20: +2 puntos

### Crecimiento (25%)
- EPS Growth ≥ 20%: +3 puntos
- EPS Growth ≥ 15%: +2 puntos
- EPS Growth ≥ 10%: +1 punto

### Rentabilidad (25%)
- ROE ≥ 25%: +3 puntos
- ROE ≥ 20%: +2 puntos
- ROE ≥ 15%: +1 punto
- Net Margin > 15%: +1 punto bonus

### Salud Financiera (25%)
- Current Ratio ≥ 2.5: +2 puntos
- Quick Ratio ≥ 1.5: +1.5 puntos
- D/E ≤ 0.2: +2 puntos
- D/E ≤ 0.3: +1.5 puntos

---

## Perfiles de Configuración

### Conservative
Para inversores aversos al riesgo:
- Market Cap > $5B
- P/E < 25
- PEG < 0.8
- ROE > 18%
- D/E < 0.3

### Standard (Default)
Balance entre growth y value:
- Market Cap > $2B
- PEG < 1
- ROE > 15%
- D/E < 0.5

### Aggressive
Mayor tolerancia al riesgo por más crecimiento:
- Market Cap > $1B
- P/E < 50
- PEG < 1.5
- EPS Growth > 15%
- D/E < 0.8

---

## Sectores y Consideraciones

### Sectores donde GARP funciona bien:
- **Technology**: Alto crecimiento, márgenes altos
- **Healthcare**: Crecimiento demográfico
- **Consumer Discretionary**: Ciclos de crecimiento
- **Industrials**: Beneficiarios de CapEx

### Sectores con cautela:
- **Utilities**: Crecimiento limitado (mejor para dividendos)
- **Real Estate**: Métricas diferentes (FFO, NAV)
- **Financials**: Ratios específicos (P/B, ROA)
- **Energy**: Alta volatilidad de commodities

---

## Limitaciones del Enfoque

1. **Backward-looking**: Proyecciones de crecimiento pueden fallar
2. **Sector bias**: Favorece ciertos sectores sobre otros
3. **Market conditions**: En bear markets, todo parece "value"
4. **Data quality**: Depende de datos precisos de analistas

---

## Checklist de Due Diligence

Después del screening, validar manualmente:

- [ ] ¿El crecimiento es sostenible?
- [ ] ¿Hay moat competitivo?
- [ ] ¿Management alineado con shareholders?
- [ ] ¿Tendencias del sector favorables?
- [ ] ¿Riesgos regulatorios?
- [ ] ¿Exposición geográfica?
- [ ] ¿Última conferencia de earnings?
- [ ] ¿Insider buying/selling?

---

## Referencias

- "One Up on Wall Street" - Peter Lynch
- "Beating the Street" - Peter Lynch
- Investopedia: GARP Investing
- CFA Institute: Growth vs Value
