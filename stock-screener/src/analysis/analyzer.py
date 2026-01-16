"""Analizador completo de stocks con noticias, earnings y datos relacionados."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
import yfinance as yf
import httpx
from bs4 import BeautifulSoup
from loguru import logger


@dataclass
class NewsItem:
    """Noticia de un stock."""
    title: str
    link: str
    source: str
    date: Optional[str] = None


@dataclass
class EarningsInfo:
    """Información de earnings."""
    next_earnings_date: Optional[date] = None
    eps_estimate: Optional[float] = None
    eps_actual: Optional[float] = None
    revenue_estimate: Optional[float] = None
    earnings_history: list = field(default_factory=list)


@dataclass
class RelatedAsset:
    """Activo relacionado (commodity, índice, etc)."""
    symbol: str
    name: str
    price: float
    change_percent: float
    relevance: str  # "commodity", "index", "peer", "etf"


@dataclass
class StockAnalysis:
    """Análisis completo de un stock."""
    symbol: str
    name: str
    sector: str
    industry: str

    # Datos de Finviz
    peg_finviz: Optional[float] = None
    fwd_pe: Optional[float] = None
    eps_this_year: Optional[float] = None
    eps_next_year: Optional[float] = None

    # Noticias
    news: list[NewsItem] = field(default_factory=list)

    # Earnings
    earnings: Optional[EarningsInfo] = None

    # Activos relacionados
    related_assets: list[RelatedAsset] = field(default_factory=list)

    # Balance highlights
    revenue_ttm: Optional[float] = None
    net_income_ttm: Optional[float] = None
    free_cash_flow: Optional[float] = None
    total_debt: Optional[float] = None
    total_cash: Optional[float] = None

    analyzed_at: datetime = field(default_factory=datetime.now)


# Mapeo de sectores/industrias a activos relacionados
SECTOR_RELATED_ASSETS = {
    "Basic Materials": {
        "commodities": ["GC=F", "SI=F", "HG=F"],  # Gold, Silver, Copper
        "etfs": ["GLD", "SLV", "XME"],
        "indices": ["^GSPC"],
    },
    "Gold": {
        "commodities": ["GC=F", "SI=F"],  # Gold, Silver
        "etfs": ["GLD", "GDX", "GDXJ"],
        "indices": ["^HUI"],  # Gold BUGS Index
    },
    "Technology": {
        "commodities": [],
        "etfs": ["QQQ", "XLK", "SMH"],
        "indices": ["^IXIC", "^SOX"],  # Nasdaq, Semiconductor
    },
    "Semiconductors": {
        "commodities": [],
        "etfs": ["SMH", "SOXX"],
        "indices": ["^SOX"],
    },
    "Energy": {
        "commodities": ["CL=F", "NG=F"],  # Crude Oil, Natural Gas
        "etfs": ["XLE", "USO"],
        "indices": ["^GSPC"],
    },
    "Financial": {
        "commodities": [],
        "etfs": ["XLF", "KRE"],
        "indices": ["^GSPC", "^TNX"],  # S&P, 10Y Treasury
    },
}

ASSET_NAMES = {
    "GC=F": "Gold Futures",
    "SI=F": "Silver Futures",
    "HG=F": "Copper Futures",
    "CL=F": "Crude Oil WTI",
    "NG=F": "Natural Gas",
    "GLD": "SPDR Gold Trust ETF",
    "SLV": "iShares Silver Trust",
    "GDX": "VanEck Gold Miners ETF",
    "GDXJ": "VanEck Junior Gold Miners",
    "XME": "SPDR Metals & Mining ETF",
    "QQQ": "Invesco QQQ Trust",
    "XLK": "Technology Select SPDR",
    "SMH": "VanEck Semiconductor ETF",
    "SOXX": "iShares Semiconductor ETF",
    "XLE": "Energy Select SPDR",
    "USO": "United States Oil Fund",
    "XLF": "Financial Select SPDR",
    "KRE": "SPDR Regional Banking ETF",
    "^GSPC": "S&P 500",
    "^IXIC": "Nasdaq Composite",
    "^SOX": "Philadelphia Semiconductor",
    "^HUI": "NYSE Arca Gold BUGS",
    "^TNX": "10-Year Treasury Yield",
}


class StockAnalyzer:
    """Analizador completo de stocks."""

    FINVIZ_BASE = "https://finviz.com/quote.ashx"

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.client = httpx.Client(timeout=30, headers=self.headers)

    def analyze(self, symbol: str, finviz_data: dict = None) -> StockAnalysis:
        """
        Realiza análisis completo de un stock.

        Args:
            symbol: Ticker del stock
            finviz_data: Datos ya obtenidos de Finviz (opcional)

        Returns:
            StockAnalysis con todos los datos
        """
        logger.info(f"Analizando {symbol}...")

        # Obtener datos base de Yahoo
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}

        analysis = StockAnalysis(
            symbol=symbol,
            name=info.get("shortName", info.get("longName", symbol)),
            sector=info.get("sector", "Unknown"),
            industry=info.get("industry", "Unknown"),
        )

        # Datos de Finviz si los tenemos
        if finviz_data:
            analysis.peg_finviz = finviz_data.get("peg")
            analysis.fwd_pe = finviz_data.get("fwd_pe")
            analysis.eps_this_year = finviz_data.get("eps_this_y")
            analysis.eps_next_year = finviz_data.get("eps_next_y")

        # Noticias
        analysis.news = self._get_news(symbol)

        # Earnings
        analysis.earnings = self._get_earnings(ticker, info)

        # Balance highlights
        analysis.revenue_ttm = info.get("totalRevenue")
        analysis.net_income_ttm = info.get("netIncomeToCommon")
        analysis.free_cash_flow = info.get("freeCashflow")
        analysis.total_debt = info.get("totalDebt")
        analysis.total_cash = info.get("totalCash")

        # Activos relacionados
        analysis.related_assets = self._get_related_assets(
            analysis.sector, analysis.industry
        )

        return analysis

    def _get_news(self, symbol: str, limit: int = 5) -> list[NewsItem]:
        """Obtiene noticias de Finviz."""
        try:
            url = f"{self.FINVIZ_BASE}?t={symbol}"
            response = self.client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            news_table = soup.find("table", {"id": "news-table"})

            if not news_table:
                return []

            news = []
            rows = news_table.find_all("tr")[:limit]

            current_date = None
            for row in rows:
                cells = row.find_all("td")
                if len(cells) < 2:
                    continue

                # Primera celda: fecha/hora
                date_cell = cells[0].text.strip()
                if len(date_cell) > 10:  # Es una fecha completa
                    current_date = date_cell.split()[0]

                # Segunda celda: título y link
                link_tag = cells[1].find("a")
                if link_tag:
                    news.append(NewsItem(
                        title=link_tag.text.strip(),
                        link=link_tag.get("href", ""),
                        source=cells[1].find("span").text.strip() if cells[1].find("span") else "",
                        date=current_date,
                    ))

            return news

        except Exception as e:
            logger.warning(f"Error obteniendo noticias para {symbol}: {e}")
            return []

    def _get_earnings(self, ticker: yf.Ticker, info: dict) -> EarningsInfo:
        """Obtiene información de earnings."""
        earnings = EarningsInfo()

        try:
            # Próximo earnings
            calendar = ticker.calendar
            if calendar is not None and not calendar.empty:
                if "Earnings Date" in calendar.index:
                    earnings_dates = calendar.loc["Earnings Date"]
                    if hasattr(earnings_dates, '__iter__') and len(earnings_dates) > 0:
                        next_date = earnings_dates.iloc[0] if hasattr(earnings_dates, 'iloc') else earnings_dates[0]
                        if hasattr(next_date, 'date'):
                            earnings.next_earnings_date = next_date.date()

                if "EPS Estimate" in calendar.index:
                    earnings.eps_estimate = calendar.loc["EPS Estimate"]
                if "Revenue Estimate" in calendar.index:
                    earnings.revenue_estimate = calendar.loc["Revenue Estimate"]

            # Historial de earnings
            earnings_hist = ticker.earnings_history
            if earnings_hist is not None and not earnings_hist.empty:
                earnings.earnings_history = earnings_hist.to_dict("records")[:4]

        except Exception as e:
            logger.debug(f"Error obteniendo earnings: {e}")

        return earnings

    def _get_related_assets(self, sector: str, industry: str) -> list[RelatedAsset]:
        """Obtiene activos relacionados al sector/industria."""
        related = []

        # Buscar por industria primero, luego sector
        config = SECTOR_RELATED_ASSETS.get(industry) or SECTOR_RELATED_ASSETS.get(sector, {})

        symbols_to_fetch = []
        relevance_map = {}

        for commodity in config.get("commodities", []):
            symbols_to_fetch.append(commodity)
            relevance_map[commodity] = "commodity"

        for etf in config.get("etfs", [])[:2]:  # Limitar ETFs
            symbols_to_fetch.append(etf)
            relevance_map[etf] = "etf"

        for index in config.get("indices", [])[:2]:  # Limitar índices
            symbols_to_fetch.append(index)
            relevance_map[index] = "index"

        # Obtener precios
        for symbol in symbols_to_fetch:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")

                if hist.empty:
                    continue

                current_price = hist["Close"].iloc[-1]
                if len(hist) > 1:
                    prev_price = hist["Close"].iloc[-2]
                    change_pct = ((current_price - prev_price) / prev_price) * 100
                else:
                    change_pct = 0

                related.append(RelatedAsset(
                    symbol=symbol,
                    name=ASSET_NAMES.get(symbol, symbol),
                    price=round(current_price, 2),
                    change_percent=round(change_pct, 2),
                    relevance=relevance_map.get(symbol, "related"),
                ))

            except Exception as e:
                logger.debug(f"Error obteniendo {symbol}: {e}")
                continue

        return related

    def close(self):
        """Cierra conexiones."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
