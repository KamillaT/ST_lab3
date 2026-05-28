from pathlib import Path
import json
import tempfile
import zipfile
from urllib.parse import urlparse

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.proxy import Proxy, ProxyType
import os
from datetime import datetime


def load_dotenv_file():
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value

    if os.getenv("email"):
        os.environ.setdefault("TUTU_EMAIL", os.environ["email"])
        os.environ.setdefault("TUTU_LOGIN", os.environ["email"])
    if os.getenv("password"):
        os.environ.setdefault("TUTU_PASSWORD", os.environ["password"])


load_dotenv_file()


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
    parser.addoption(
        "--proxy",
        default=os.environ.get("TUTU_PROXY"),
        help="Browser proxy, for example socks5://user:password@host:port",
    )


def pytest_generate_tests(metafunc):
    if "browser_name" in metafunc.fixturenames:
        browsers = metafunc.config.getoption("--browser") or ["chrome", "firefox"]
        metafunc.parametrize("browser_name", browsers, scope="session")


def find_firefox_binary() -> str | None:
    candidates = [
        os.environ.get("FIREFOX_BINARY"),
        "/snap/firefox/current/usr/lib/firefox/firefox",
        "/usr/lib/firefox/firefox",
        "/usr/lib/firefox-esr/firefox-esr",
        "/opt/firefox/firefox",
        "/usr/bin/firefox",
        "/snap/bin/firefox",
        "/Applications/Firefox.app/Contents/MacOS/firefox",
    ]

    for candidate in candidates:
        if candidate and Path(candidate).exists() and os.access(candidate, os.X_OK):
            return candidate

    return None


def parse_proxy(proxy_url: str | None) -> dict | None:
    if not proxy_url:
        return None

    parsed = urlparse(proxy_url)
    if parsed.scheme.lower() not in {"socks5", "socks"}:
        raise ValueError("Only socks5 proxy is supported by this test config")
    if not parsed.hostname or not parsed.port:
        raise ValueError("Proxy must include host and port")

    return {
        "scheme": "socks5",
        "host": parsed.hostname,
        "port": parsed.port,
        "username": parsed.username,
        "password": parsed.password,
    }


def build_selenium_proxy(proxy_config: dict | None, include_auth: bool = True) -> Proxy | None:
    if not proxy_config:
        return None

    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.socks_proxy = f"{proxy_config['host']}:{proxy_config['port']}"
    proxy.socks_version = 5
    if include_auth and proxy_config.get("username"):
        proxy.socks_username = proxy_config["username"]
    if include_auth and proxy_config.get("password"):
        proxy.socks_password = proxy_config["password"]
    return proxy


def ensure_webdriver_localhost_no_proxy():
    local_hosts = {"localhost", "127.0.0.1", "::1"}
    for name in ("NO_PROXY", "no_proxy"):
        current_values = {
            value.strip()
            for value in os.environ.get(name, "").split(",")
            if value.strip()
        }
        os.environ[name] = ",".join(sorted(current_values | local_hosts))


def create_chrome_proxy_extension(proxy_config: dict) -> tempfile.TemporaryDirectory:
    extension_dir = tempfile.TemporaryDirectory(prefix="tutu_proxy_")
    extension_path = Path(extension_dir.name) / "proxy_auth.zip"

    manifest = {
        "version": "1.0",
        "manifest_version": 2,
        "name": "Tutu Selenium Proxy Auth",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking",
        ],
        "background": {"scripts": ["background.js"]},
    }
    background = f"""
var config = {{
  mode: "fixed_servers",
  rules: {{
    singleProxy: {{
      scheme: "socks5",
      host: "{proxy_config['host']}",
      port: {proxy_config['port']}
    }},
    bypassList: ["localhost", "127.0.0.1", "::1"]
  }}
}};
chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
chrome.webRequest.onAuthRequired.addListener(
  function(details) {{
    return {{
      authCredentials: {{
        username: "{proxy_config.get('username') or ''}",
        password: "{proxy_config.get('password') or ''}"
      }}
    }};
  }},
  {{urls: ["<all_urls>"]}},
  ["blocking"]
);
"""

    with zipfile.ZipFile(extension_path, "w") as archive:
        archive.writestr("manifest.json", json.dumps(manifest))
        archive.writestr("background.js", background)

    return extension_dir



@pytest.fixture(scope="session")
def driver(browser_name, request):
    ensure_webdriver_localhost_no_proxy()
    headless = request.config.getoption("--headless")
    proxy_config = parse_proxy(request.config.getoption("--proxy"))
    chrome_proxy_extension = None

    if browser_name == "chrome":
        options = ChromeOptions()
        options.add_argument("--window-size=1366,768")
        options.add_argument("--disable-notifications")
        options.add_argument("--remote-allow-origins=*")
        if proxy_config and proxy_config.get("username"):
            chrome_proxy_extension = create_chrome_proxy_extension(proxy_config)
            options.add_extension(str(Path(chrome_proxy_extension.name) / "proxy_auth.zip"))
        elif proxy_config:
            options.add_argument(
                f"--proxy-server=socks5://{proxy_config['host']}:{proxy_config['port']}"
            )
        if headless:
            options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=options)


    elif browser_name == "firefox":
        options = FirefoxOptions()
        options.set_preference("dom.webnotifications.enabled", False)
        if proxy_config:
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.socks", proxy_config["host"])
            options.set_preference("network.proxy.socks_port", proxy_config["port"])
            options.set_preference("network.proxy.socks_version", 5)
            options.set_preference("network.proxy.socks_remote_dns", True)
            options.set_preference("signon.autologin.proxy", True)
            if proxy_config.get("username"):
                options.set_preference("network.proxy.socks_username", proxy_config["username"])
            if proxy_config.get("password"):
                options.set_preference("network.proxy.socks_password", proxy_config["password"])
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

    proxy_state = "on" if proxy_config else "off"
    print(f"\n[BROWSER START] browser={browser_name} | proxy={proxy_state}")

    yield driver

    try:
        current_url = driver.current_url
    except Exception as error:
        current_url = f"unavailable ({error.__class__.__name__})"
    print(f"[BROWSER STOP] browser={browser_name} | url={current_url}")
    try:
        driver.quit()
    except Exception as error:
        print(f"[BROWSER STOP] browser={browser_name} | quit failed: {error.__class__.__name__}")
    if chrome_proxy_extension:
        chrome_proxy_extension.cleanup()


@pytest.fixture(autouse=True)
def attach_driver_to_test(request):
    if "driver" not in request.fixturenames:
        yield
        return

    driver_instance = request.getfixturevalue("driver")
    browser_name = request.getfixturevalue("browser_name")
    request.node._driver = driver_instance
    request.node._browser_name = browser_name
    proxy_state = "on" if request.config.getoption("--proxy") else "off"
    print(f"\n[START] {request.node.name} | browser={browser_name} | proxy={proxy_state}")
    yield
    try:
        current_url = driver_instance.current_url
    except Exception as error:
        current_url = f"unavailable ({error.__class__.__name__})"
    print(f"[STOP] {request.node.name} | browser={browser_name} | url={current_url}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return

    browser_name = getattr(item, "_browser_name", "unknown")
    status = "PASSED" if report.passed else "FAILED" if report.failed else "SKIPPED"
    print(f"[RESULT] {item.name} | browser={browser_name} | {status}")

    driver = getattr(item, "_driver", None)
    if report.failed and driver:
        screenshots_dir = Path("artifacts/screenshots")
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = screenshots_dir / f"{timestamp}_{browser_name}_{item.name}.png"
        try:
            driver.save_screenshot(str(screenshot_path))
            print(f"[FAILURE] screenshot={screenshot_path}")
        except Exception as error:
            print(f"[FAILURE] screenshot=not saved ({error.__class__.__name__})")
        try:
            print(f"[FAILURE] url={driver.current_url}")
        except Exception as error:
            print(f"[FAILURE] url=unavailable ({error.__class__.__name__})")
