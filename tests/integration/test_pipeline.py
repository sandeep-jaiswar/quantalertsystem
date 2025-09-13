"""Integration tests for the quantitative pipeline."""

import pytest
from unittest.mock import Mock, patch
from quantalertsystem.main import QuantAlertsPipeline


@pytest.mark.integration
def test_pipeline_initialization():
    """Test that the pipeline can be initialized."""
    pipeline = QuantAlertsPipeline()
    assert pipeline is not None
    assert hasattr(pipeline, 'settings')


@pytest.mark.integration  
@patch('services.ingest.yahoo_finance.YahooFinanceIngester.fetch_market_data')
def test_pipeline_end_to_end_mock(mock_fetch):
    """Test complete pipeline with mocked data."""
    # Mock the external data source
    mock_fetch.return_value = []
    
    pipeline = QuantAlertsPipeline()
    
    # This should not fail even with empty data
    try:
        # Simple test that pipeline can handle empty results
        result = pipeline.run(['AAPL'])
        assert result is not None
    except Exception as e:
        # Acceptable for integration test with minimal setup
        assert "No market data" in str(e) or "Empty" in str(e)