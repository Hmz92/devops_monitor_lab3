from api.metrics import get_system_metrics

def test_get_system_metrics():
    """Test that system metrics are formatted correctly and have valid ranges."""
    metrics = get_system_metrics()
    
    assert isinstance(metrics, dict)
    assert "cpu_percent" in metrics
    assert "memory_percent" in metrics
    assert "disk_percent" in metrics
    assert "memory_used_gb" in metrics
    
    # Percentages must be between 0 and 100
    assert 0 <= metrics["cpu_percent"] <= 100
    assert 0 <= metrics["memory_percent"] <= 100
    assert 0 <= metrics["disk_percent"] <= 100
    assert metrics["memory_used_gb"] >= 0
