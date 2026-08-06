from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "src" / "didyoulearn" / "web"


def test_local_lab_has_no_external_runtime_dependencies():
    html = (WEB / "index.html").read_text(encoding="utf-8")
    css = (WEB / "styles.css").read_text(encoding="utf-8")
    javascript = (WEB / "app.js").read_text(encoding="utf-8")

    assert 'src="http' not in html
    assert 'rel="stylesheet" href="http' not in html
    assert "@import" not in css
    assert "url(http" not in css
    assert "fetch(" not in javascript
    assert "XMLHttpRequest" not in javascript
    assert "WebSocket" not in javascript


def test_local_lab_declares_a_closed_content_security_policy():
    html = (WEB / "index.html").read_text(encoding="utf-8")

    assert "default-src 'self'" in html
    assert "connect-src 'none'" in html
    assert "object-src 'none'" in html
    assert "base-uri 'none'" in html


def test_local_lab_explains_the_evidence_boundary():
    html = (WEB / "index.html").read_text(encoding="utf-8")
    normalized = " ".join(html.split())

    assert "does not prove which provider generated" in normalized
    assert "Not a public model result yet." in normalized
    assert "community-submitted" in normalized


def test_readme_figures_exist_and_are_not_placeholders():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    figures = ["hero.svg", "protocol.svg", "scorecard.svg"]

    for name in figures:
        assert f"docs/assets/{name}" in readme
        text = (ROOT / "docs" / "assets" / name).read_text(encoding="utf-8")
        assert "<title" in text
        assert "<desc" in text
        assert "placeholder" not in text.lower()
