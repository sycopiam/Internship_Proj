from app.services.category_suggester import suggest_category


def test_network_keyword_suggestion():
    result = suggest_category("WiFi is not working in the main office")
    assert result["suggested_category"] == "Network"
    assert "wifi" in result["matched_keywords"]


def test_hardware_keyword_suggestion():
    result = suggest_category("Laptop screen is broken and flickering")
    assert result["suggested_category"] == "Hardware"
    assert "laptop" in result["matched_keywords"] or "screen" in result["matched_keywords"]


def test_account_keyword_suggestion():
    result = suggest_category("I forgot my password after returning from vacation")
    assert result["suggested_category"] == "Account"
    assert "password" in result["matched_keywords"] or "forgot" in result["matched_keywords"]


def test_email_keyword_suggestion():
    result = suggest_category("Outlook is not receiving emails with attachments")
    assert result["suggested_category"] == "Email"
    assert "outlook" in result["matched_keywords"] or "email" in result["matched_keywords"]


def test_software_keyword_suggestion():
    result = suggest_category("Application keeps crashing when launching Excel report export")
    assert result["suggested_category"] == "Software"
    assert "application" in result["matched_keywords"] or "crashing" in result["matched_keywords"]
