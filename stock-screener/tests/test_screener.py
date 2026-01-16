"""Tests para el stock screener."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.models.stock import Stock, StockMetrics, ScreenerResult
from src.core.filters import FilterEngine
from src.core.scoring import ScoringEngine


# === Fixtures ===

@pytest.fixture
def sample_config():
    """Configuración de prueba."""
    return {
        "name": "Test Config",
        "valuation": {
            "pe_ratio": {"min": 0, "max": None},
            "peg_ratio": {"min": None, "max": 1},
        },
        "growth": {
            "eps_growth_5y": {"min": 0, "max": None},
        },
        "profitability": {
            "roe": {"min": 0.15, "max": None},
        },
        "liquidity": {
            "current_ratio": {"min": 1.5, "max": None},
            "quick_ratio": {"min": 1, "max": None},
        },
        "solvency": {
            "debt_to_equity": {"min": None, "max": 0.5},
        },
        "operability": {},
        "scoring": {
            "enabled": True,
            "weights": {
                "valuation": 0.25,
                "growth": 0.25,
                "profitability": 0.25,
                "financial_health": 0.25,
            }
        }
    }


@pytest.fixture
def passing_stock():
    """Stock que pasa todos los filtros."""
    return Stock(
        symbol="PASS",
        name="Passing Company",
        exchange="NYSE",
        sector="Technology",
        industry="Software",
        price=100,
        market_cap=5e9,
        avg_volume=500000,
        metrics=StockMetrics(
            pe_ratio=15,
            peg_ratio=0.8,
            eps_growth_5y=0.12,
            roe=0.20,
            current_ratio=2.0,
            quick_ratio=1.5,
            debt_to_equity=0.3,
        ),
    )


@pytest.fixture
def failing_stock():
    """Stock que no pasa filtros."""
    return Stock(
        symbol="FAIL",
        name="Failing Company",
        exchange="NYSE",
        sector="Technology",
        industry="Software",
        price=50,
        market_cap=3e9,
        avg_volume=400000,
        metrics=StockMetrics(
            pe_ratio=25,
            peg_ratio=1.5,  # Falla: > 1
            eps_growth_5y=0.05,
            roe=0.10,  # Falla: < 15%
            current_ratio=1.2,  # Falla: < 1.5
            quick_ratio=0.8,  # Falla: < 1
            debt_to_equity=0.8,  # Falla: > 0.5
        ),
    )


# === Tests de Modelos ===

class TestStockMetrics:
    def test_to_dict_excludes_none(self):
        metrics = StockMetrics(pe_ratio=15, roe=0.20)
        result = metrics.to_dict()
        
        assert "pe_ratio" in result
        assert "roe" in result
        assert "peg_ratio" not in result  # None
    
    def test_all_fields_serializable(self):
        metrics = StockMetrics(
            pe_ratio=15,
            peg_ratio=0.8,
            pb_ratio=2.5,
            ps_ratio=3.0,
            eps_growth_5y=0.12,
            roe=0.20,
            current_ratio=2.0,
            debt_to_equity=0.3,
        )
        result = metrics.to_dict()
        
        assert all(isinstance(v, (int, float)) for v in result.values())


class TestStock:
    def test_to_dict(self, passing_stock):
        result = passing_stock.to_dict()
        
        assert result["symbol"] == "PASS"
        assert result["name"] == "Passing Company"
        assert "metrics" in result
        assert "last_updated" in result
    
    def test_passes_filter_with_bounds(self, passing_stock):
        criteria = {"pe_ratio": {"min": 0, "max": 20}}
        assert passing_stock.passes_filter(criteria) is True
        
        criteria = {"pe_ratio": {"min": 0, "max": 10}}
        assert passing_stock.passes_filter(criteria) is False


# === Tests de Filtros ===

class TestFilterEngine:
    def test_passes_all_with_valid_stock(self, sample_config, passing_stock):
        engine = FilterEngine(sample_config)
        assert engine.passes_all(passing_stock) is True
    
    def test_fails_with_invalid_stock(self, sample_config, failing_stock):
        engine = FilterEngine(sample_config)
        assert engine.passes_all(failing_stock) is False
    
    def test_get_failing_filters(self, sample_config, failing_stock):
        engine = FilterEngine(sample_config)
        failing = engine.get_failing_filters(failing_stock)
        
        assert len(failing) > 0
        assert any("peg_ratio" in f for f in failing)
        assert any("roe" in f for f in failing)
    
    def test_evaluate_returns_all_filters(self, sample_config, passing_stock):
        engine = FilterEngine(sample_config)
        evaluation = engine.evaluate(passing_stock)
        
        assert isinstance(evaluation, dict)
        assert all(isinstance(v, bool) for v in evaluation.values())


# === Tests de Scoring ===

class TestScoringEngine:
    def test_score_returns_tuple(self, sample_config, passing_stock):
        engine = ScoringEngine(sample_config["scoring"])
        score, breakdown = engine.score(passing_stock)
        
        assert isinstance(score, float)
        assert isinstance(breakdown, dict)
        assert 0 <= score <= 10
    
    def test_breakdown_has_all_categories(self, sample_config, passing_stock):
        engine = ScoringEngine(sample_config["scoring"])
        _, breakdown = engine.score(passing_stock)
        
        expected = ["valuation", "growth", "profitability", "financial_health"]
        for cat in expected:
            assert cat in breakdown
    
    def test_better_metrics_higher_score(self, sample_config, passing_stock, failing_stock):
        engine = ScoringEngine(sample_config["scoring"])
        
        good_score, _ = engine.score(passing_stock)
        bad_score, _ = engine.score(failing_stock)
        
        assert good_score > bad_score


# === Tests de Integración ===

class TestScreenerResult:
    def test_to_dict(self, passing_stock):
        result = ScreenerResult(
            timestamp=datetime.now(),
            config_name="Test",
            total_scanned=100,
            total_matches=10,
            stocks=[passing_stock],
            execution_time_seconds=5.5,
        )
        
        data = result.to_dict()
        
        assert data["config_name"] == "Test"
        assert data["total_scanned"] == 100
        assert data["total_matches"] == 10
        assert len(data["stocks"]) == 1


# === Tests de API (Mocked) ===

class TestFMPClient:
    @patch("src.api.fmp.httpx.Client")
    def test_screen_stocks_returns_list(self, mock_client):
        from src.api.fmp import FMPClient
        
        mock_response = Mock()
        mock_response.json.return_value = [
            {"symbol": "AAPL", "companyName": "Apple"},
            {"symbol": "MSFT", "companyName": "Microsoft"},
        ]
        mock_response.raise_for_status = Mock()
        
        mock_client.return_value.get.return_value = mock_response
        
        with patch.dict("os.environ", {"FMP_API_KEY": "test_key"}):
            client = FMPClient()
            results = client.screen_stocks()
        
        assert isinstance(results, list)
        assert len(results) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
