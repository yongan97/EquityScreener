"""Cliente para Yahoo Finance - alternativa gratuita."""

import time
from datetime import datetime
from typing import Optional
import pandas as pd
import yfinance as yf
from loguru import logger

from src.models.stock import Stock, StockMetrics


# Lista de símbolos del S&P 500 y NASDAQ 100 para screening
SP500_SYMBOLS = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "BRK-B", "UNH", "JNJ",
    "JPM", "V", "PG", "XOM", "HD", "CVX", "MA", "ABBV", "MRK", "LLY",
    "PEP", "KO", "COST", "AVGO", "MCD", "WMT", "CSCO", "TMO", "PFE", "ACN",
    "ABT", "DHR", "NKE", "CMCSA", "VZ", "ADBE", "TXN", "CRM", "PM", "NEE",
    "WFC", "BMY", "ORCL", "RTX", "UPS", "QCOM", "T", "MS", "INTC", "HON",
    "COP", "UNP", "LOW", "IBM", "GS", "CAT", "BA", "AMGN", "SPGI", "ELV",
    "DE", "SBUX", "INTU", "AMD", "GILD", "BLK", "AXP", "GE", "ISRG", "ADI",
    "MDLZ", "LMT", "CVS", "SYK", "BKNG", "REGN", "TJX", "MMC", "ZTS", "ADP",
    "CI", "VRTX", "MO", "SCHW", "LRCX", "C", "PGR", "CME", "CB", "NOW",
    "SO", "EOG", "DUK", "SLB", "BDX", "BSX", "NOC", "EQIX", "ITW", "MMM",
    "APD", "SNPS", "ICE", "CL", "CDNS", "MU", "HUM", "WM", "AON", "PNC",
    "MCK", "FCX", "FDX", "SHW", "CMG", "EMR", "USB", "ETN", "TGT", "PLD",
    "GD", "PSA", "ORLY", "MSI", "KLAC", "MAR", "DG", "ATVI", "AZO", "KMB",
    "NSC", "GM", "EW", "NXPI", "CTAS", "CCI", "AEP", "ADM", "ANET", "MCO",
    "HCA", "D", "MET", "MCHP", "ROP", "OXY", "TRV", "TFC", "PCAR", "AIG",
    "KDP", "SRE", "DOW", "APH", "CTVA", "NEM", "JCI", "A", "KHC", "PSX",
    "ECL", "GIS", "WELL", "PRU", "F", "TEL", "AFL", "IQV", "MNST", "SPG",
    "MSCI", "HLT", "DXCM", "PAYX", "LHX", "IDXX", "AMP", "FTNT", "O", "CMI",
    "CARR", "YUM", "EXC", "DHI", "BK", "WMB", "STZ", "HSY", "OTIS", "KEYS",
    "BIIB", "VRSK", "AME", "GWW", "ALL", "ED", "PEG", "ON", "KR", "VLO",
    "CTSH", "FAST", "XEL", "AJG", "CPRT", "DVN", "DLTR", "HAL", "IT", "GEHC",
    "ODFL", "MTD", "DD", "ROK", "RSG", "ALB", "WEC", "VICI", "CBRE", "RMD",
    "BKR", "EA", "EBAY", "EFX", "AWK", "PPG", "TSCO", "ANSS", "URI", "ABC",
    "CDW", "LEN", "IR", "SBAC", "HPQ", "FANG", "MLM", "WTW", "ACGL", "WAB",
    "EQR", "CSGP", "ZBH", "GPN", "ULTA", "DFS", "ROST", "AVB", "FIS", "TROW",
    "ARE", "APTV", "FTV", "GLW", "EXR", "WBD", "ILMN", "DAL", "MTB", "WY",
    "HIG", "INVH", "CHD", "IFF", "LVS", "STT", "NTRS", "BR", "TDY", "CE",
    "DTE", "LYB", "FE", "VMC", "AES", "MPWR", "ALGN", "BAX", "GRMN", "CNC",
    "STE", "MAA", "RF", "PFG", "CFG", "PKI", "TER", "CLX", "SYY", "COO",
    "HBAN", "CNP", "LDOS", "CAH", "MKC", "MAS", "J", "FITB", "CINF", "EXPD",
    "ES", "PPL", "ATO", "MOH", "L", "KEY", "K", "HOLX", "NTAP", "DGX",
    "TRMB", "CAG", "IP", "SWKS", "BALL", "OMC", "JBHT", "DRI", "AKAM", "WRB",
    "AMCR", "TXT", "LUV", "APA", "SEDG", "BBWI", "IEX", "HRL", "NVR", "POOL",
    "BRO", "CF", "TYL", "ROL", "KIM", "NDSN", "BIO", "EVRG", "UDR", "PEAK",
    "SWK", "SJM", "RCL", "JKHY", "WAT", "HST", "TPR", "ZBRA", "REG", "CBOE",
    "MGM", "PNR", "TECH", "EMN", "FLT", "CHRW", "BWA", "CCL", "LNT", "CRL",
    "IPG", "MTCH", "AAL", "NRG", "FMC", "AOS", "ALLE", "QRVO", "CPT", "NDAQ",
    "UAL", "HSIC", "WYNN", "VTR", "NI", "BXP", "PNW", "ETSY", "MOS", "CTLT",
    "BEN", "FFIV", "AIZ", "WHR", "AAP", "HAS", "CMA", "SEE", "TAP", "XRAY",
    "HII", "ALK", "PARA", "GNRC", "IVZ", "NWSA", "NWS", "DVA", "RL", "DISH",
    "FRT", "FOXA", "FOX", "LUMN", "ZION", "VFC", "DXC", "GL", "PVH", "CPB"
]


class YahooScreener:
    """Screener usando Yahoo Finance (gratis, sin API key)."""

    def __init__(self):
        self._request_count = 0

    def get_stock_universe(self) -> list[str]:
        """Retorna lista de símbolos para screening (S&P 500)."""
        return SP500_SYMBOLS.copy()

    def get_stock_info(self, symbol: str) -> Optional[dict]:
        """Obtiene información completa de un símbolo."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or info.get("regularMarketPrice") is None:
                return None

            return info
        except Exception as e:
            logger.debug(f"Error fetching {symbol}: {e}")
            return None

    def screen_stocks(
        self,
        market_cap_min: float = 2e9,
        price_min: float = 5,
        volume_min: int = 300000,
        exchange: list[str] = None,
    ) -> list[dict]:
        """
        Screening de stocks usando Yahoo Finance.

        Args:
            market_cap_min: Market cap mínimo
            price_min: Precio mínimo
            volume_min: Volumen promedio mínimo
            exchange: Exchanges permitidos (ignorado, usamos S&P 500)

        Returns:
            Lista de stocks que pasan filtros básicos
        """
        logger.info("Screening con Yahoo Finance...")
        symbols = self.get_stock_universe()
        logger.info(f"Procesando {len(symbols)} símbolos...")

        candidates = []

        for i, symbol in enumerate(symbols):
            try:
                info = self.get_stock_info(symbol)
                if not info:
                    continue

                mkt_cap = info.get("marketCap") or 0
                price = info.get("regularMarketPrice") or info.get("currentPrice") or 0
                volume = info.get("averageVolume") or info.get("volume") or 0

                if mkt_cap >= market_cap_min and price >= price_min and volume >= volume_min:
                    candidates.append({
                        "symbol": symbol,
                        "info": info
                    })

                # Rate limiting
                time.sleep(0.1)

                if (i + 1) % 50 == 0:
                    logger.info(f"Procesados {i + 1}/{len(symbols)}, candidatos: {len(candidates)}")

            except Exception as e:
                logger.debug(f"Error procesando {symbol}: {e}")
                continue

        logger.info(f"Candidatos después de filtros básicos: {len(candidates)}")
        return candidates

    def build_stock(self, symbol: str, basic_data: dict = None) -> Optional[Stock]:
        """
        Construye objeto Stock con datos de Yahoo Finance.

        Args:
            symbol: Símbolo de la acción
            basic_data: Datos de get_stock_info (opcional)

        Returns:
            Stock con métricas completas
        """
        try:
            if basic_data and "info" in basic_data:
                info = basic_data["info"]
            else:
                info = self.get_stock_info(symbol)

            if not info:
                return None

            # Construir métricas
            metrics = StockMetrics(
                # Valuación
                pe_ratio=info.get("trailingPE") or info.get("forwardPE"),
                peg_ratio=info.get("pegRatio"),
                pb_ratio=info.get("priceToBook"),
                ps_ratio=info.get("priceToSalesTrailing12Months"),

                # Crecimiento
                eps_growth_5y=info.get("earningsQuarterlyGrowth"),  # Aproximación
                revenue_growth_5y=info.get("revenueGrowth"),

                # Rentabilidad
                roe=info.get("returnOnEquity"),
                roa=info.get("returnOnAssets"),
                gross_margin=info.get("grossMargins"),
                operating_margin=info.get("operatingMargins"),
                net_margin=info.get("profitMargins"),

                # Liquidez
                current_ratio=info.get("currentRatio"),
                quick_ratio=info.get("quickRatio"),

                # Solvencia
                debt_to_equity=info.get("debtToEquity"),
                interest_coverage=None,  # No disponible directamente
            )

            # Convertir debt_to_equity de porcentaje a ratio si es necesario
            if metrics.debt_to_equity and metrics.debt_to_equity > 10:
                metrics.debt_to_equity = metrics.debt_to_equity / 100

            return Stock(
                symbol=symbol,
                name=info.get("shortName") or info.get("longName", ""),
                exchange=info.get("exchange", ""),
                sector=info.get("sector", ""),
                industry=info.get("industry", ""),
                price=info.get("regularMarketPrice") or info.get("currentPrice", 0),
                market_cap=info.get("marketCap", 0),
                avg_volume=info.get("averageVolume", 0),
                metrics=metrics,
                last_updated=datetime.now(),
                data_source="yahoo",
            )

        except Exception as e:
            logger.warning(f"Error building stock {symbol}: {e}")
            return None

    def close(self):
        """Cleanup (no-op for Yahoo)."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
