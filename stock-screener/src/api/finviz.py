"""Cliente para Finviz (scraping como backup)."""

import time
from typing import Optional

import httpx
from bs4 import BeautifulSoup
from loguru import logger


class FinvizClient:
    """
    Cliente para scraping de Finviz.
    Usar con moderación - respetar rate limits.
    """
    
    BASE_URL = "https://finviz.com/screener.ashx"
    DELAY_SECONDS = 5  # Delay entre requests
    
    # Mapeo de filtros a parámetros Finviz
    FILTER_MAP = {
        "market_cap_min_2b": "cap_largeover",
        "market_cap_min_10b": "cap_mega",
        "pe_positive": "fa_pe_profitable",
        "peg_under_1": "fa_peg_low",
        "roe_over_15": "fa_roe_o15",
        "current_ratio_over_1.5": "fa_curratio_o1.5",
        "quick_ratio_over_1": "fa_quickratio_o1",
        "debt_equity_under_0.5": "fa_debteq_u0.5",
    }
    
    def __init__(self, delay: float = None):
        self.delay = delay or self.DELAY_SECONDS
        self.last_request = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.client = httpx.Client(timeout=30, headers=self.headers)
    
    def _wait(self):
        """Espera entre requests para no saturar."""
        elapsed = time.time() - self.last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request = time.time()
    
    def screen(self, filters: list[str] = None, max_pages: int = 10, view: str = "121") -> list[dict]:
        """
        Ejecuta screener en Finviz con paginación.

        Args:
            filters: Lista de filtros (ver FILTER_MAP)
            max_pages: Máximo de páginas a recorrer (20 resultados por página)
            view: Vista de Finviz (111=Overview, 121=Valuation con PEG, 161=Financial)

        Returns:
            Lista de diccionarios con datos
        """
        all_results = []
        filter_str = ",".join(filters or [])

        logger.info(f"Finviz scraping con filtros: {filter_str} (view={view})")

        for page in range(max_pages):
            self._wait()

            # Finviz usa 'r' para offset (r=1 es página 1, r=21 es página 2, etc)
            offset = page * 20 + 1
            params = {"v": view, "f": filter_str, "r": offset}

            response = self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()

            # Usar parser según vista
            if view == "121":
                page_results = self._parse_valuation_table(response.text)
            else:
                page_results = self._parse_table(response.text)

            if not page_results:
                break

            all_results.extend(page_results)
            logger.info(f"Finviz página {page + 1}: {len(page_results)} resultados (total: {len(all_results)})")

            if len(page_results) < 20:
                break

        logger.info(f"Finviz total: {len(all_results)} resultados")
        return all_results

    def _parse_valuation_table(self, html: str) -> list[dict]:
        """Parsea tabla de valuación (v=121) con PEG."""
        soup = BeautifulSoup(html, "lxml")

        table = soup.find("table", {"class": "screener_table"})
        if not table:
            return []

        results = []
        rows = table.find_all("tr")[1:]  # Skip header

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 12:
                continue

            try:
                ticker_cell = cols[1]
                ticker_link = ticker_cell.find("a")
                symbol = ticker_link.text.strip() if ticker_link else cols[1].text.strip()

                results.append({
                    "symbol": symbol,
                    "market_cap": self._parse_market_cap(cols[2].text),
                    "pe": self._parse_float(cols[3].text),
                    "fwd_pe": self._parse_float(cols[4].text),
                    "peg": self._parse_float(cols[5].text),
                    "ps": self._parse_float(cols[6].text),
                    "pb": self._parse_float(cols[7].text),
                    "pc": self._parse_float(cols[8].text),
                    "pfcf": self._parse_float(cols[9].text),
                    "eps_this_y": self._parse_percent(cols[10].text),
                    "eps_next_y": self._parse_percent(cols[11].text),
                })
            except (IndexError, ValueError) as e:
                logger.debug(f"Error parseando fila valuación: {e}")
                continue

        return results

    def _parse_percent(self, text: str) -> Optional[float]:
        """Parsea porcentaje (ej: '92.60%' -> 0.926)."""
        text = text.strip().replace("%", "").replace(",", "")
        if not text or text == "-":
            return None
        try:
            return float(text) / 100
        except ValueError:
            return None
    
    def _parse_table(self, html: str) -> list[dict]:
        """Parsea tabla de resultados."""
        soup = BeautifulSoup(html, "lxml")

        # Buscar tabla de resultados (nueva estructura 2024+)
        table = soup.find("table", {"class": "screener_table"})
        if not table:
            # Fallback: buscar por id antiguo
            table = soup.find("table", {"id": "screener-content"})
        if not table:
            logger.warning("No se encontró tabla de resultados")
            return []

        results = []
        rows = table.find_all("tr")[1:]  # Skip header

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 10:
                continue

            try:
                # Extraer ticker del link
                ticker_cell = cols[1]
                ticker_link = ticker_cell.find("a")
                symbol = ticker_link.text.strip() if ticker_link else cols[1].text.strip()

                results.append({
                    "symbol": symbol,
                    "name": cols[2].text.strip(),
                    "sector": cols[3].text.strip(),
                    "industry": cols[4].text.strip(),
                    "country": cols[5].text.strip(),
                    "market_cap": self._parse_market_cap(cols[6].text),
                    "pe": self._parse_float(cols[7].text),
                    "price": self._parse_float(cols[8].text),
                    "change": cols[9].text.strip(),
                    "volume": self._parse_int(cols[10].text),
                })
            except (IndexError, ValueError) as e:
                logger.debug(f"Error parseando fila: {e}")
                continue

        logger.info(f"Finviz: {len(results)} resultados")
        return results
    
    def _parse_market_cap(self, text: str) -> Optional[float]:
        """Parsea market cap (ej: '2.5B' -> 2500000000)."""
        text = text.strip().upper()
        if not text or text == "-":
            return None
        
        multipliers = {"K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}
        
        for suffix, mult in multipliers.items():
            if text.endswith(suffix):
                return float(text[:-1]) * mult
        
        return float(text)
    
    def _parse_float(self, text: str) -> Optional[float]:
        """Parsea float, retorna None si inválido."""
        text = text.strip().replace(",", "")
        if not text or text == "-":
            return None
        try:
            return float(text)
        except ValueError:
            return None
    
    def _parse_int(self, text: str) -> Optional[int]:
        """Parsea int, retorna None si inválido."""
        text = text.strip().replace(",", "")
        if not text or text == "-":
            return None
        try:
            return int(text)
        except ValueError:
            return None
    
    def get_garp_filters(self) -> list[str]:
        """Retorna filtros predefinidos para estrategia GARP."""
        return [
            "cap_largeover",      # Market Cap > $2B
            "fa_pe_profitable",   # P/E positivo
            "fa_peg_low",         # PEG < 1
            "fa_roe_o15",         # ROE > 15%
            "fa_curratio_o1.5",   # Current Ratio > 1.5
            "fa_quickratio_o1",   # Quick Ratio > 1
            "fa_debteq_u0.5",     # D/E < 0.5
        ]
    
    def close(self):
        """Cierra el cliente HTTP."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
