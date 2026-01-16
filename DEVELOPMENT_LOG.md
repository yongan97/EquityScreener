# Development Log - Equity Screener Project

**Fecha:** 16 de Enero de 2026
**Proyecto:** Stock Screener GARP con AI Analysis
**Repositorio:** https://github.com/yongan97/EquityScreener

---

## Resumen Ejecutivo

Sistema completo de screening de acciones basado en la estrategia GARP (Growth At Reasonable Price) con scoring mediante IA, desplegado en Vercel con automatizacion diaria via GitHub Actions.

---

## 1. Arquitectura del Proyecto

### Estructura de Carpetas

```
C:/c/Equities/
├── stock-screener/              # Backend Python
│   ├── src/
│   │   ├── api/                 # Clientes de APIs (Finviz, Yahoo, FMP)
│   │   ├── core/                # Logica del screener y filtros
│   │   ├── models/              # Dataclasses (Stock, Metrics)
│   │   ├── analysis/            # AI Scoring, Trade Ideas, Analyzer
│   │   ├── db/                  # Cliente Supabase
│   │   └── utils/               # Cache y exportacion
│   ├── scripts/                 # Scripts de ejecucion
│   ├── config/                  # Configuraciones JSON
│   └── database/                # Migraciones SQL
│
├── stock-screener-web/          # Frontend Next.js
│   ├── app/                     # Rutas App Router
│   ├── components/              # Componentes React
│   │   ├── ui/                  # shadcn/ui components
│   │   ├── charts/              # TradingView widgets
│   │   └── auth/                # Autenticacion
│   ├── lib/                     # Utilidades y queries
│   └── types/                   # TypeScript types
│
└── .github/workflows/           # GitHub Actions
```

---

## 2. Backend Python - Modulos Principales

### 2.1 Sistema de Scoring IA

**Archivo:** `stock-screener/src/analysis/ai_scoring.py`

Motor de scoring avanzado con 6 componentes ponderados:

| Componente | Peso | Descripcion |
|------------|------|-------------|
| Fundamental | 20% | ROE, margenes, ratios de liquidez |
| Valuation | 25% | PEG, P/E vs sector, Forward P/E |
| Growth | 20% | EPS growth historico y proyectado |
| Momentum | 15% | SMA 20/50, RSI, posicion 52W |
| Sentiment | 10% | Analisis de keywords en noticias |
| Quality | 10% | ROA, FCF, cash vs debt |

```python
class AIScoreBreakdown:
    fundamental_score: float  # 0-10
    valuation_score: float    # 0-10
    growth_score: float       # 0-10
    momentum_score: float     # 0-10
    sentiment_score: float    # 0-10
    quality_score: float      # 0-10
    total_score: float        # Ponderado

    # Detalles adicionales
    momentum_trend: str       # "bullish", "neutral", "bearish"
    sentiment_summary: str    # "Positive (5+ / 2-)"
    growth_outlook: str       # "accelerating", "stable"
    valuation_vs_sector: str  # "cheap", "fair", "expensive"
    flags: list[str]          # Oportunidades y riesgos
```

### 2.2 Generador de Trade Ideas

**Archivo:** `stock-screener/src/analysis/trade_idea.py`

Genera documentos profesionales en Markdown con:
- Tesis de inversion
- Razones para comprar (basadas en scores)
- Tabla de metricas clave
- Catalizadores (noticias recientes)
- Riesgos a monitorear
- Conclusion y horizonte sugerido

**Recomendaciones basadas en score:**
- >= 7.5: COMPRA FUERTE
- >= 6.5: COMPRA
- >= 5.5: MANTENER
- < 5.5: OBSERVAR

### 2.3 Analizador de Stocks

**Archivo:** `stock-screener/src/analysis/analyzer.py`

Obtiene datos enriquecidos de cada stock:
- Datos financieros de Yahoo Finance
- Noticias de Finviz (scraping)
- Fechas de earnings
- Activos relacionados (commodities, ETFs, indices)
- Balance highlights (FCF, cash, debt)

### 2.4 Price Performance

**Archivo:** `stock-screener/src/analysis/price_performance.py`

Calcula variaciones de precio:
- 1 dia
- 1 semana
- 1 mes
- YTD
- 52 semanas

### 2.5 Cliente Supabase

**Archivo:** `stock-screener/src/db/supabase_client.py`

Metodos principales:
- `save_run_with_analysis()`: Guarda corrida completa con analisis IA
- `save_stock_analysis()`: Guarda analisis individual
- `cleanup_keep_one_per_day()`: Mantiene solo 1 corrida por dia
- `get_latest_stocks()`: Obtiene stocks de la ultima corrida

### 2.6 Script Principal

**Archivo:** `stock-screener/scripts/run_full_analysis.py`

Flujo de ejecucion:
1. Ejecutar screener con filtros GARP
2. Analizar cada stock con AI Score
3. Generar Trade Ideas
4. Calcular Price Performance
5. Guardar en Supabase
6. (Opcional) Cleanup de corridas duplicadas

```bash
python scripts/run_full_analysis.py --cleanup --verbose
```

---

## 3. Frontend Next.js

### 3.1 Stock Detail Page

**Archivo:** `stock-screener-web/app/stock/[symbol]/page.tsx`

Caracteristicas:
- Integracion TradingView (chart + technical analysis)
- Score Card con AI scores
- Metricas organizadas por categoria
- Balance Highlights
- News y Related Assets
- Historial de scores
- Boton Trade Idea con modal

**Fix importante (Next.js 16):**
```typescript
// Params ahora son Promise en Next.js 16
interface StockPageProps {
  params: Promise<{ symbol: string }>;
}

export default function StockPage({ params }: StockPageProps) {
  const { symbol } = use(params);  // use() hook
  // ...
}
```

### 3.2 TradeIdeaModal

**Archivo:** `stock-screener-web/components/TradeIdeaModal.tsx`

Modal para mostrar Trade Ideas con:
- Renderizado Markdown (ReactMarkdown)
- Boton copiar al clipboard
- Toast de confirmacion

### 3.3 ScoreCard

**Archivo:** `stock-screener-web/components/ScoreCard.tsx`

Muestra:
- Score total (AI o basico)
- Breakdown por componente con barras de progreso
- Recomendacion (STRONG BUY/BUY/HOLD/WATCH)
- Insights (momentum, growth, valuation)
- Flags de oportunidad/riesgo

### 3.4 Types

**Archivo:** `stock-screener-web/types/stock.ts`

Interfaces TypeScript completas:
- `Stock`: Todos los campos incluyendo AI scores, news, flags
- `ScreenerRun`: Metadata de corridas
- `NewsItem`, `RelatedAsset`: Tipos JSON
- `StockHistory`: Para graficos historicos
- `StockFilters`, `SectorStats`: Utilidades

---

## 4. Base de Datos (Supabase)

### 4.1 Migracion AI Analysis

**Archivo:** `database/migrations/002_add_ai_analysis.sql`

Nuevos campos agregados a la tabla `stocks`:
- AI Score components (ai_score, ai_fundamental, ai_valuation, etc.)
- Analysis details (momentum_trend, sentiment_summary, etc.)
- JSON fields (flags, news, related_assets)
- Trade idea (texto Markdown)
- Indices optimizados

### 4.2 Migracion Price Performance

**Archivo:** `database/migrations/003_add_price_changes.sql`

Campos de variacion de precio:
- perf_1d, perf_1w, perf_1m, perf_ytd, perf_52w
- Indices para ordenamiento

---

## 5. Automatizacion (GitHub Actions)

### 5.1 Workflow Principal

**Archivo:** `.github/workflows/daily-screener.yml`

**Schedule:** Lunes a Viernes, 6:00 AM EST (11:00 UTC)

**Jobs:**

1. **run-screener**
   - Setup Python 3.11
   - Test conexion Supabase
   - Ejecutar screener con analisis IA
   - Notificar por email si falla

2. **distribute-content**
   - Post a Bluesky (si configurado)
   - Post a Discord (si configurado)
   - Generar RSS Feed
   - Enviar Newsletter (Premium)

3. **cleanup** (solo manual)
   - Limpieza de corridas antiguas

### 5.2 Secrets Requeridos

| Secret | Descripcion |
|--------|-------------|
| SUPABASE_URL | URL del proyecto Supabase |
| SUPABASE_SERVICE_KEY | Service role key |
| FMP_API_KEY | Financial Modeling Prep |
| RESEND_API_KEY | Email notifications |
| BLUESKY_HANDLE | (Opcional) Usuario Bluesky |
| BLUESKY_APP_PASSWORD | (Opcional) Password Bluesky |
| DISCORD_WEBHOOK_URL | (Opcional) Webhook Discord |

### 5.3 Notificaciones de Error

En caso de fallo, envia email a `juangandolfog@gmail.com` con:
- Fecha del error
- Run ID
- Link a los logs

---

## 6. Deployment

### 6.1 Vercel

**URL:** https://stock-screener-web.vercel.app

Configuracion:
- Framework: Next.js
- Build command: `npm run build`
- Output directory: `.next`
- Environment variables configuradas en dashboard

### 6.2 Variables de Entorno (Frontend)

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

---

## 7. Fixes Realizados

### 7.1 Next.js 16 Params Promise

**Problema:** En Next.js 16, `params` es ahora un Promise.

**Solucion:**
```typescript
const { symbol } = use(params);
```

### 7.2 Unicode en Windows

**Problema:** Caracteres especiales causaban errores de encoding.

**Solucion:** Reemplazar caracteres como `═`, `✓` con equivalentes ASCII o Rich markup.

### 7.3 Format Strings en Python

**Problema:** f-strings con condicionales y format specifiers.

**Error:**
```python
{m.pe_ratio:.1f if m.pe_ratio else 'N/A'}  # Error
```

**Solucion:**
```python
{f"{m.pe_ratio:.1f}" if m.pe_ratio else "N/A"}  # Correcto
```

### 7.4 GitHub Workflow Command

**Problema:** Typer CLI sin subcomandos no acepta `run`.

**Solucion:** Cambiar de:
```bash
python scripts/run_full_analysis.py run --cleanup
```
A:
```bash
python scripts/run_full_analysis.py --cleanup
```

### 7.5 Upsert sin Constraint

**Problema:** Upsert requiere unique constraint.

**Solucion:** Cambiar `upsert()` por `insert()`.

---

## 8. APIs Utilizadas

| API | Uso | Riesgo |
|-----|-----|--------|
| Finviz | Screening + Noticias (scraping) | Medio |
| Yahoo Finance (yfinance) | Metricas detalladas + Momentum | Medio |
| FMP | Backup (configurado, no activo) | Bajo |
| Supabase | Base de datos | Bajo |
| Resend | Email notifications | Bajo |

---

## 9. Proximos Pasos Sugeridos

1. **Monitoreo:** Revisar logs del workflow diario
2. **Bluesky/Discord:** Configurar secrets para publicacion automatica
3. **Newsletter:** Configurar lista de suscriptores premium
4. **Testing:** Agregar tests unitarios para scoring IA
5. **Alertas:** Configurar alertas de stock especificos

---

## 10. Comandos Utiles

```bash
# Ejecutar screener local
cd stock-screener
python scripts/run_full_analysis.py --verbose

# Con cleanup
python scripts/run_full_analysis.py --cleanup --verbose

# Frontend development
cd stock-screener-web
npm run dev

# Git
git status
git add .
git commit -m "mensaje"
git push origin main

# Trigger manual del workflow
gh workflow run daily-screener.yml
```

---

*Documentacion generada automaticamente - 16 de Enero de 2026*
