# Stock Screener GARP

Screener cuantitativo para identificar acciones de calidad con crecimiento a precio razonable.

## Instalación

```bash
# Clonar y entrar al directorio
cd stock-screener

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar API key
cp .env.example .env
# Editar .env con tu API key de Financial Modeling Prep
```

## Uso Rápido

```bash
# Ejecutar screener con configuración default
python scripts/run_screener.py

# Con configuración custom
python scripts/run_screener.py --config config/aggressive.json

# Exportar a Excel
python scripts/run_screener.py --output results.xlsx
```

## Criterios de Filtrado

### Operabilidad
- Market Cap > $2B
- Volumen Promedio > 300K
- Precio > $5

### Valuación y Crecimiento
- P/E > 0 (rentable)
- PEG < 1
- EPS Growth 5Y > 0%

### Calidad
- ROE > 15%
- Current Ratio > 1.5
- Quick Ratio > 1
- Debt/Equity < 0.5

## Estructura del Proyecto

```
stock-screener/
├── CLAUDE.md           # Instrucciones para Claude
├── README.md           # Este archivo
├── requirements.txt    # Dependencias Python
├── .env.example        # Template de configuración
├── agents/             # Agentes especializados
├── config/             # Archivos de configuración
├── data/               # Cache y datos descargados
├── docs/               # Documentación adicional
├── scripts/            # Scripts de ejecución
├── src/                # Código fuente
│   ├── api/            # Clientes de APIs
│   ├── core/           # Lógica principal
│   ├── models/         # Modelos de datos
│   └── utils/          # Utilidades
└── tests/              # Tests unitarios
```

## APIs Utilizadas

| API | Uso | Costo |
|-----|-----|-------|
| Financial Modeling Prep | Principal | Free tier: 250 req/día |
| Finviz | Backup/Validación | Gratis (scraping) |
| Yahoo Finance | Datos históricos | Gratis |

## Licencia

MIT
