from backend.services.scraper import load_data, scrape_and_save

def test_load_data_returns_string():
    """Verify scraper loads fallback or live data as a string."""
    data = load_data()
    assert isinstance(data, str)
    assert len(data) > 0

def test_scrape_and_save_fallback():
    """Verify scrape_and_save gracefully handles bad URLs and returns fallback text."""
    data = scrape_and_save(urls=["https://this.is.a.bad.url.that.will.fail"])
    assert isinstance(data, str)
    assert "Voting is a fundamental right" in data or "SOURCE" in data
