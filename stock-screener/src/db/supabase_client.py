"""Supabase client for persisting screener results."""

import os
from typing import Optional
from loguru import logger
from supabase import create_client, Client

from src.models.stock import ScreenerResult, Stock
from src.analysis.ai_scoring import AIScoreBreakdown
from src.analysis.analyzer import StockAnalysis


class SupabaseClient:
    """Client for interacting with Supabase database."""

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """Initialize Supabase client.

        Args:
            url: Supabase project URL. Defaults to SUPABASE_URL env var.
            key: Supabase service key. Defaults to SUPABASE_KEY env var.
        """
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")

        if not self.url or not self.key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set as environment variables "
                "or passed as arguments"
            )

        self.client: Client = create_client(self.url, self.key)
        logger.info("Supabase client initialized")

    def save_run(self, result: ScreenerResult) -> str:
        """Save screener result to database.

        Args:
            result: ScreenerResult object containing run metadata and stocks.

        Returns:
            The UUID of the created screener run.
        """
        logger.info(f"Saving screener run: {result.config_name}")

        # 1. Insert run metadata
        run_data = {
            "config_name": result.config_name,
            "total_scanned": result.total_scanned,
            "total_matches": result.total_matches,
            "execution_time_seconds": result.execution_time_seconds,
            "errors": result.errors if result.errors else None,
        }

        run_response = self.client.table("screener_runs").insert(run_data).execute()
        run_id = run_response.data[0]["id"]
        logger.info(f"Created screener run with id: {run_id}")

        # 2. Insert stocks in batches
        if result.stocks:
            stocks_data = [self._stock_to_dict(stock, run_id) for stock in result.stocks]

            # Supabase can handle batches, but let's be safe with chunks of 100
            batch_size = 100
            for i in range(0, len(stocks_data), batch_size):
                batch = stocks_data[i : i + batch_size]
                self.client.table("stocks").insert(batch).execute()
                logger.debug(f"Inserted batch {i // batch_size + 1} of stocks")

            logger.info(f"Saved {len(result.stocks)} stocks to database")

        return run_id

    def _stock_to_dict(self, stock: Stock, run_id: str) -> dict:
        """Convert Stock object to database row dictionary.

        Args:
            stock: Stock object to convert.
            run_id: UUID of the parent screener run.

        Returns:
            Dictionary ready for database insertion.
        """
        metrics = stock.metrics
        breakdown = stock.score_breakdown or {}

        return {
            "run_id": run_id,
            "symbol": stock.symbol,
            "name": stock.name,
            "exchange": stock.exchange,
            "sector": stock.sector,
            "industry": stock.industry,
            "price": stock.price,
            "market_cap": int(stock.market_cap) if stock.market_cap else None,
            "avg_volume": int(stock.avg_volume) if stock.avg_volume else None,
            # Valuation metrics
            "pe_ratio": metrics.pe_ratio,
            "peg_ratio": metrics.peg_ratio,
            "pb_ratio": metrics.pb_ratio,
            "ps_ratio": metrics.ps_ratio,
            # Growth metrics
            "eps_growth_5y": metrics.eps_growth_5y,
            "revenue_growth_5y": metrics.revenue_growth_5y,
            "eps_growth_ttm": metrics.eps_growth_ttm,
            # Profitability metrics
            "roe": metrics.roe,
            "roa": metrics.roa,
            "gross_margin": metrics.gross_margin,
            "operating_margin": metrics.operating_margin,
            "net_margin": metrics.net_margin,
            # Liquidity metrics
            "current_ratio": metrics.current_ratio,
            "quick_ratio": metrics.quick_ratio,
            # Solvency metrics
            "debt_to_equity": metrics.debt_to_equity,
            "interest_coverage": metrics.interest_coverage,
            # Scores
            "score": stock.score,
            "score_valuation": breakdown.get("score_valuation"),
            "score_growth": breakdown.get("score_growth"),
            "score_profitability": breakdown.get("score_profitability"),
            "score_financial_health": breakdown.get("score_financial_health"),
        }

    def get_latest_run(self) -> Optional[dict]:
        """Get the most recent screener run metadata.

        Returns:
            Dictionary with run metadata or None if no runs exist.
        """
        response = (
            self.client.table("screener_runs")
            .select("*")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None

    def get_latest_stocks(self, limit: int = 100) -> list[dict]:
        """Get stocks from the most recent screener run.

        Args:
            limit: Maximum number of stocks to return.

        Returns:
            List of stock dictionaries ordered by score descending.
        """
        response = (
            self.client.table("latest_stocks")
            .select("*")
            .order("score", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data

    def get_run_history(self, limit: int = 30) -> list[dict]:
        """Get history of screener runs.

        Args:
            limit: Maximum number of runs to return.

        Returns:
            List of run metadata dictionaries.
        """
        response = (
            self.client.table("screener_runs")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data

    def get_stocks_by_run(self, run_id: str, limit: int = 100) -> list[dict]:
        """Get stocks for a specific screener run.

        Args:
            run_id: UUID of the screener run.
            limit: Maximum number of stocks to return.

        Returns:
            List of stock dictionaries.
        """
        response = (
            self.client.table("stocks")
            .select("*")
            .eq("run_id", run_id)
            .order("score", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data

    def get_stock_history(self, symbol: str, limit: int = 30) -> list[dict]:
        """Get historical data for a specific stock symbol.

        Args:
            symbol: Stock ticker symbol.
            limit: Maximum number of records to return.

        Returns:
            List of stock records across different runs.
        """
        response = (
            self.client.table("stock_history")
            .select("*")
            .eq("symbol", symbol)
            .limit(limit)
            .execute()
        )
        return response.data

    def delete_old_runs(self, keep_count: int = 30) -> int:
        """Delete old screener runs, keeping the most recent ones.

        Args:
            keep_count: Number of recent runs to keep.

        Returns:
            Number of runs deleted.
        """
        # Get IDs of runs to keep
        keep_response = (
            self.client.table("screener_runs")
            .select("id")
            .order("created_at", desc=True)
            .limit(keep_count)
            .execute()
        )
        keep_ids = [r["id"] for r in keep_response.data]

        if not keep_ids:
            return 0

        # Delete runs not in keep list
        # Note: This cascades to delete associated stocks due to ON DELETE CASCADE
        delete_response = (
            self.client.table("screener_runs")
            .delete()
            .not_.in_("id", keep_ids)
            .execute()
        )

        deleted_count = len(delete_response.data) if delete_response.data else 0
        logger.info(f"Deleted {deleted_count} old screener runs")
        return deleted_count

    def cleanup_keep_one_per_day(self, keep_days: int = 30) -> int:
        """Delete duplicate runs keeping only the latest run per day.

        Args:
            keep_days: Number of days of history to keep.

        Returns:
            Number of runs deleted.
        """
        from datetime import datetime, timedelta
        from collections import defaultdict

        # Get all runs
        response = (
            self.client.table("screener_runs")
            .select("id, created_at")
            .order("created_at", desc=True)
            .execute()
        )

        if not response.data:
            return 0

        # Group runs by date
        runs_by_date = defaultdict(list)
        for run in response.data:
            # Parse date (assuming ISO format)
            created = run["created_at"][:10]  # YYYY-MM-DD
            runs_by_date[created].append(run["id"])

        # Identify runs to delete (keep only first/latest per day)
        ids_to_delete = []
        cutoff_date = (datetime.now() - timedelta(days=keep_days)).strftime("%Y-%m-%d")

        for date, run_ids in runs_by_date.items():
            # Delete runs older than keep_days
            if date < cutoff_date:
                ids_to_delete.extend(run_ids)
            # Keep only the first (latest) run per day
            elif len(run_ids) > 1:
                ids_to_delete.extend(run_ids[1:])  # Keep first, delete rest

        if not ids_to_delete:
            logger.info("No duplicate runs to clean up")
            return 0

        # Delete in batches
        deleted = 0
        batch_size = 50
        for i in range(0, len(ids_to_delete), batch_size):
            batch = ids_to_delete[i:i + batch_size]
            delete_response = (
                self.client.table("screener_runs")
                .delete()
                .in_("id", batch)
                .execute()
            )
            deleted += len(delete_response.data) if delete_response.data else 0

        logger.info(f"Cleaned up {deleted} duplicate runs, keeping 1 per day")
        return deleted

    def save_stock_analysis(
        self,
        run_id: str,
        stock: Stock,
        analysis: StockAnalysis,
        ai_score: AIScoreBreakdown,
        trade_idea_md: str,
    ) -> None:
        """Save complete stock analysis with AI score and trade idea.

        Args:
            run_id: UUID of the screener run.
            stock: Stock object.
            analysis: Complete analysis.
            ai_score: AI score breakdown.
            trade_idea_md: Trade idea in markdown format.
        """
        data = {
            "run_id": run_id,
            "symbol": stock.symbol,
            "name": stock.name,
            "exchange": stock.exchange,
            "sector": stock.sector,
            "industry": analysis.industry,
            "price": stock.price,
            "market_cap": int(stock.market_cap) if stock.market_cap else None,
            # Basic metrics
            "pe_ratio": stock.metrics.pe_ratio,
            "peg_ratio": stock.metrics.peg_ratio,
            "peg_finviz": analysis.peg_finviz,
            "fwd_pe": analysis.fwd_pe,
            "roe": stock.metrics.roe,
            "roa": stock.metrics.roa,
            "current_ratio": stock.metrics.current_ratio,
            "quick_ratio": stock.metrics.quick_ratio,
            "debt_to_equity": stock.metrics.debt_to_equity,
            "gross_margin": stock.metrics.gross_margin,
            "net_margin": stock.metrics.net_margin,
            "eps_growth_5y": stock.metrics.eps_growth_5y,
            # Finviz growth estimates
            "eps_this_year": analysis.eps_this_year,
            "eps_next_year": analysis.eps_next_year,
            # Balance
            "revenue_ttm": analysis.revenue_ttm,
            "net_income_ttm": analysis.net_income_ttm,
            "free_cash_flow": analysis.free_cash_flow,
            "total_cash": analysis.total_cash,
            "total_debt": analysis.total_debt,
            # AI Score
            "score": stock.score,
            "ai_score": ai_score.total_score,
            "ai_fundamental": ai_score.fundamental_score,
            "ai_valuation": ai_score.valuation_score,
            "ai_growth": ai_score.growth_score,
            "ai_momentum": ai_score.momentum_score,
            "ai_sentiment": ai_score.sentiment_score,
            "ai_quality": ai_score.quality_score,
            # Analysis details
            "momentum_trend": ai_score.momentum_trend,
            "sentiment_summary": ai_score.sentiment_summary,
            "growth_outlook": ai_score.growth_outlook,
            "valuation_vs_sector": ai_score.valuation_vs_sector,
            # Flags and news
            "flags": ai_score.flags if ai_score.flags else None,
            "news": [{"title": n.title, "date": n.date, "source": n.source} for n in analysis.news[:5]] if analysis.news else None,
            "related_assets": [
                {"symbol": a.symbol, "name": a.name, "price": a.price, "change": a.change_percent, "type": a.relevance}
                for a in analysis.related_assets[:5]
            ] if analysis.related_assets else None,
            # Earnings
            "next_earnings_date": str(analysis.earnings.next_earnings_date) if analysis.earnings and analysis.earnings.next_earnings_date else None,
            # Trade idea
            "trade_idea": trade_idea_md,
        }

        # Insert stock analysis
        self.client.table("stocks").insert(data).execute()
        logger.debug(f"Saved analysis for {stock.symbol}")

    def save_run_with_analysis(
        self,
        result: ScreenerResult,
        analyses: dict[str, tuple[StockAnalysis, AIScoreBreakdown, str]],
    ) -> str:
        """Save screener run with complete analysis for each stock.

        Args:
            result: ScreenerResult with run metadata.
            analyses: Dict mapping symbol to (analysis, ai_score, trade_idea_md).

        Returns:
            Run ID.
        """
        logger.info(f"Saving screener run with analysis: {result.config_name}")

        # 1. Insert run metadata
        run_data = {
            "config_name": result.config_name,
            "total_scanned": result.total_scanned,
            "total_matches": result.total_matches,
            "execution_time_seconds": result.execution_time_seconds,
            "errors": result.errors if result.errors else None,
        }

        run_response = self.client.table("screener_runs").insert(run_data).execute()
        run_id = run_response.data[0]["id"]
        logger.info(f"Created screener run: {run_id}")

        # 2. Save stocks with analysis
        for stock in result.stocks:
            if stock.symbol in analyses:
                analysis, ai_score, trade_idea = analyses[stock.symbol]
                self.save_stock_analysis(run_id, stock, analysis, ai_score, trade_idea)
            else:
                # Fallback: save basic data
                self.client.table("stocks").insert(
                    self._stock_to_dict(stock, run_id)
                ).execute()

        logger.info(f"Saved {len(result.stocks)} stocks with analysis")
        return run_id
