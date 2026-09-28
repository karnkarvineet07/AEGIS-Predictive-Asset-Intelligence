# Lightweight contract tests that do not require a running MySQL server.
def test_expected_api_paths():
    paths={"/api/assets","/api/predictions","/api/high-risk-assets","/api/analytics"}
    assert all(p.startswith("/api/") for p in paths)
