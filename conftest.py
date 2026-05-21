from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import os


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="append",
        choices=["chrome", "firefox"],
        help="Browser for test run. Can be passed multiple times: --browser chrome --browser firefox",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        help="Run browsers in headless mode.",
    )


def pytest_generate_tests(metafunc):
    if "browser_name" in metafunc.fixturenames:
        browsers = metafunc.config.getoption("--browser") or ["chrome", "firefox"]
        metafunc.parametrize("browser_name", browsers)


def find_firefox_binary() -> str | None:
    candidates = [
        os.environ.get("FIREFOX_BINARY"),
        "/snap/firefox/current/usr/lib/firefox/firefox",
        "/usr/lib/firefox/firefox",
        "/usr/lib/firefox-esr/firefox-esr",
        "/opt/firefox/firefox",
        "/usr/bin/firefox",
        "/snap/bin/firefox",
    ]

    for candidate in candidates:
        if candidate and Path(candidate).exists() and os.access(candidate, os.X_OK):
            return candidate

    return None



@pytest.fixture
def driver(browser_name, request):
    headless = request.config.getoption("--headless")

    if browser_name == "chrome":
        options = ChromeOptions()
        options.add_argument("--window-size=1366,768")
        options.add_argument("--disable-notifications")
        options.add_argument("--remote-allow-origins=*")
        if headless:
            options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=options)


    elif browser_name == "firefox":
        options = FirefoxOptions()
        options.set_preference("dom.webnotifications.enabled", False)
        firefox_binary = find_firefox_binary()
        if firefox_binary:
            options.binary_location = firefox_binary
        else:
            raise RuntimeError("Firefox binary not found")
        if headless:
            options.add_argument("-headless")
        driver = webdriver.Firefox(options=options)

    else:
        raise ValueError(f"Unsupported browser: {browser_name}")

    driver.set_page_load_timeout(45)
    driver.set_script_timeout(20)
    driver.set_window_size(1366, 768)

    yield driver

    driver.quit()
