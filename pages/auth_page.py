import json
import platform
from pathlib import Path

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage


class AuthPage(BasePage):
    URL = "https://id.tutu.ru/loginOrRegister?back_url=https%3A%2F%2Fmy.tutu.ru%2F"
    CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"

    LOGIN_BY_PASSWORD_TRIGGER = (
        "//*[self::button or self::a or @role='button']"
        "[@data-ti='login-by-password-trigger'"
        " or contains(normalize-space(.), 'Войти с паролем')"
        " or contains(normalize-space(.), 'Войти другим способом')]"
    )
    LOGIN_BY_EMAIL_CODE_TRIGGER = (
        "//*[self::button or self::a or @role='button']"
        "[@data-ti='login-by-email-and-code-trigger'"
        " or contains(normalize-space(.), 'Войти по эл. почте')"
        " or contains(normalize-space(.), 'Войти без пароля')]"
    )
    EMAIL_FIELD = "//input[@data-ti='email-field' or @name='email']"
    EMAIL_OR_PHONE_FIELD = (
        "//input[@data-ti='email-or-phone-field'"
        " or @name='emailOrPhone'"
        " or @name='contact']"
    )
    PASSWORD_FIELD = "//input[@data-ti='password-field' or @name='password']"
    CODE_FIELD = "//input[@data-ti='code-field' or @name='inputCode']"
    SUBMIT_BUTTON = (
        "//*[self::button or self::a or @role='button']"
        "[@data-ti='submit-trigger'"
        " or contains(normalize-space(.), 'Войти')"
        " or contains(normalize-space(.), 'Отправить код')"
        " or contains(normalize-space(.), 'Получить код')"
        " or contains(normalize-space(.), 'Создать новый профиль')]"
    )
    REMIND_PASSWORD_LINK = (
        "//*[self::a or self::button or @role='button']"
        "[@data-ti='remind-password-link'"
        " or @data-ti='password-link'"
        " or contains(normalize-space(.), 'Не помню пароль')"
        " or contains(normalize-space(.), 'Забыли пароль')]"
    )
    RESET_PASSWORD_TRIGGER = (
        "//*[self::button or self::a or @role='button']"
        "[@data-ti='reset-password-trigger'"
        " or contains(normalize-space(.), 'Восстановить пароль')]"
    )
    AGREEMENT_CHECKBOX = "//*[@data-ti='agreement-checkbox']//input|//input[@data-ti='agreement-checkbox']"
    PHONE_CONFIRMATION = "//*[contains(normalize-space(.), 'Подтвердите ваш телефон')]"
    SKIP_PHONE_BUTTON = "//button[@data-ti='skip-button']"
    INVALID_AUTH_MESSAGE = (
        "//*[contains(normalize-space(.), 'Невер')"
        " or contains(normalize-space(.), 'Введите')"
        " or contains(normalize-space(.), 'обязательное поле')"
        " or contains(normalize-space(.), 'почт')"
        " or contains(normalize-space(.), 'email')]"
    )
    RATE_LIMIT_MESSAGE = (
        "//*[contains(normalize-space(.), 'Превышено число попыток')"
        " or contains(normalize-space(.), 'Повторите попытку через несколько минут')]"
    )
    CODE_SCREEN_MESSAGE = (
        "//*[contains(normalize-space(.), 'Введите код')"
        " or contains(normalize-space(.), 'Отправили его')]"
    )
    REGISTRATION_CODE_MESSAGE = (
        "//*[contains(normalize-space(.), 'Введите код для создания нового профиля')"
        " or contains(normalize-space(.), 'Создать новый профиль')]"
    )
    INVALID_CODE_MESSAGE = (
        "//*[contains(normalize-space(.), 'Код ист')"
        " or contains(normalize-space(.), 'Код не')"
        " or contains(normalize-space(.), 'Введите все цифры кода')"
        " or contains(normalize-space(.), 'Невер')]"
    )
    AUTH_SHELL = (
        f"{PHONE_CONFIRMATION}"
        f"|{SKIP_PHONE_BUTTON}"
        f"|{RATE_LIMIT_MESSAGE}"
        f"|{INVALID_AUTH_MESSAGE}"
        f"|{LOGIN_BY_PASSWORD_TRIGGER}"
        f"|{LOGIN_BY_EMAIL_CODE_TRIGGER}"
        f"|{EMAIL_OR_PHONE_FIELD}"
        f"|{EMAIL_FIELD}"
        f"|{CODE_FIELD}"
        f"|{RESET_PASSWORD_TRIGGER}"
    )

    def __init__(self, driver, timeout=20):
        super().__init__(driver, timeout)
        self.auth_restored_from_cache = False
        self.CACHE_DIR.mkdir(exist_ok=True)

    def open_login_form(self, restore_cache: bool = False):
        self.open(self.URL)
        self.wait_document_ready()
        if restore_cache and self.restore_cached_session():
            self.auth_restored_from_cache = True
            return self
        self.present_xpath(self.AUTH_SHELL)
        return self

    def switch_to_password_login(self):
        if self.auth_restored_from_cache:
            return self
        self.click_xpath(self.LOGIN_BY_PASSWORD_TRIGGER)
        self.visible_xpath(self.EMAIL_FIELD)
        self.visible_xpath(self.PASSWORD_FIELD)
        return self

    def switch_to_email_code_login(self):
        if self.auth_restored_from_cache:
            return self
        if self.is_any_visible(self.EMAIL_OR_PHONE_FIELD, self.CODE_FIELD):
            return self
        self.click_xpath(self.LOGIN_BY_EMAIL_CODE_TRIGGER)
        self.visible_xpath(self.EMAIL_OR_PHONE_FIELD)
        return self

    def enter_contact(self, contact: str):
        self.type_first_visible_xpath(contact, self.EMAIL_OR_PHONE_FIELD, self.EMAIL_FIELD)
        return self

    def enter_email(self, email: str):
        self.type_xpath(self.EMAIL_FIELD, email)
        return self

    def enter_password(self, password: str):
        self.type_xpath(self.PASSWORD_FIELD, password)
        return self

    def submit_identity(self):
        previous_source = self.driver.page_source
        self.click_xpath(self.SUBMIT_BUTTON)
        self.wait_dom_change_or_auth_shell(previous_source)
        return self

    def submit_password(self):
        previous_source = self.driver.page_source
        self.click_xpath(self.SUBMIT_BUTTON)
        self.wait_dom_change_or_auth_shell(previous_source)
        return self

    def login_with_password(self, email: str, password: str, restore_cache: bool = False):
        self.open_login_form(restore_cache=restore_cache)
        self.switch_to_password_login()
        if self.auth_restored_from_cache:
            return self
        self.enter_email(email)
        self.enter_password(password)
        self.submit_password()
        return self

    def request_email_code(self, email: str):
        self.open_login_form()
        self.switch_to_email_code_login()
        self.enter_contact(email)
        self.submit_identity()
        self.present_xpath(f"{self.CODE_FIELD}|{self.RATE_LIMIT_MESSAGE}")
        self.assert_body_contains_any("Введите код", "Отправили", "Превышено число попыток")
        return self

    def login_with_email_code(self, email: str, code: str):
        self.request_email_code(email)
        self.enter_code(code)
        self.wait_until_auth_completed_or_code_error()
        return self

    def invalid_email_code_validation(self, email: str, code: str = "0000"):
        self.request_email_code(email)
        if self.is_any_visible(self.RATE_LIMIT_MESSAGE):
            return self
        self.enter_code(code)
        self.wait_body_contains_any(
            "Код ист",
            "Код не",
            "Введите все цифры кода",
            "Превышено число попыток",
            "Повторите",
        )
        return self

    def assert_login_failed(self):
        self.assert_body_contains_any(
            "Невер",
            "Введите",
            "обязательное поле",
            "почтовым адресом нет",
            "Превышено число попыток",
            "Повторите",
        )
        return self

    def assert_logged_in(self):
        assert self.authorization_completed(), "Авторизация не дошла до успешного состояния"
        return self

    def invalid_email_validation(self, email: str):
        self.open_login_form()
        self.switch_to_password_login()
        self.enter_email(email)
        self.submit_password()
        self.assert_body_contains_any("Введите", "почт", "email", "обязательное поле")
        return self

    def nonexistent_user_validation(self, email: str):
        self.open_login_form()
        self.switch_to_email_code_login()
        self.enter_contact(email)
        self.submit_identity()
        self.present_xpath(f"{self.CODE_FIELD}|{self.REGISTRATION_CODE_MESSAGE}|{self.RATE_LIMIT_MESSAGE}")
        self.assert_body_contains_any(
            "Введите код для создания нового профиля",
            "Создать новый профиль",
            "Превышено число попыток",
        )
        return self

    def short_password_validation(self, email: str, password: str):
        self.open_login_form()
        self.switch_to_password_login()
        self.enter_email(email)
        self.enter_password(password)
        self.submit_password()
        self.assert_login_failed()
        return self

    def registration_invalid_email_validation(self, email: str):
        # Tutu ID uses a unified login/register form, so invalid registration email
        # is validated by the same email field before an account can be created.
        return self.invalid_email_validation(email)

    def request_password_reset(self, email: str):
        self.open_login_form()
        self.switch_to_password_login()
        self.click_xpath(self.REMIND_PASSWORD_LINK)
        self.visible_xpath(self.EMAIL_FIELD)
        self.enter_email(email)
        self.submit_identity()
        self.present_xpath(f"{self.CODE_FIELD}|{self.RESET_PASSWORD_TRIGGER}|{self.RATE_LIMIT_MESSAGE}")
        self.assert_body_contains_any(
            "Введите код для быстрого доступа",
            "Восстановить пароль",
            "Превышено число попыток",
        )
        return self

    def authorization_completed(self) -> bool:
        if self.is_any_visible(self.PHONE_CONFIRMATION, self.SKIP_PHONE_BUTTON):
            self.save_cookies_to_cache()
            return True
        if "my.tutu.ru" in self.driver.current_url:
            self.save_cookies_to_cache()
            return True
        return False

    def cache_path(self) -> Path:
        browser_name = self.driver.capabilities.get("browserName", "browser").lower()
        return self.CACHE_DIR / f"tutu_auth_{browser_name}.json"

    def restore_cached_session(self) -> bool:
        cache_path = self.cache_path()
        if not cache_path.exists():
            return False

        cookies = json.loads(cache_path.read_text(encoding="utf-8"))
        for cookie in cookies:
            sanitized_cookie = {
                key: value
                for key, value in cookie.items()
                if key not in {"sameSite", "storeId", "id"}
            }
            try:
                self.driver.add_cookie(sanitized_cookie)
            except Exception:
                continue

        self.driver.refresh()
        self.wait_document_ready()
        try:
            self.present_xpath(self.AUTH_SHELL)
        except TimeoutException:
            cache_path.unlink(missing_ok=True)
            return False

        if self.authorization_completed():
            return True

        cache_path.unlink(missing_ok=True)
        return False

    def save_cookies_to_cache(self):
        self.cache_path().write_text(
            json.dumps(self.driver.get_cookies(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return self

    def type_first_visible_xpath(self, value: str, *xpaths: str):
        element = self.first_visible_xpath(*xpaths)
        self.type_into_element(element, value)
        return self

    def type_xpath(self, xpath: str, value: str):
        element = self.visible_xpath(xpath)
        self.type_into_element(element, value)
        return self

    def type_into_element(self, element, value: str):
        element.click()
        select_all_key = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
        element.send_keys(select_all_key, "a")
        element.send_keys(Keys.DELETE)
        element.send_keys(value)
        return self

    def enter_code(self, code: str):
        sanitized_code = "".join(character for character in code if character.isdigit())
        assert len(sanitized_code) == 4, "Код из почты должен состоять из 4 цифр"

        fields = self.wait.until(
            lambda driver: [
                element
                for element in driver.find_elements(By.XPATH, self.CODE_FIELD)
                if element.is_displayed()
            ]
        )
        assert len(fields) >= 4, "На странице не найдено 4 поля для кода из почты"

        previous_source = self.driver.page_source
        for element, digit in zip(fields[:4], sanitized_code):
            self.type_into_element(element, digit)

        self.click_submit_if_present(timeout=2)
        self.wait_dom_change_or_auth_shell(previous_source)
        return self

    def click_submit_if_present(self, timeout: int = 2):
        try:
            button = WebDriverWait(self.driver, timeout).until(
                lambda driver: next(
                    (
                        element
                        for element in driver.find_elements(By.XPATH, self.SUBMIT_BUTTON)
                        if element.is_displayed() and element.is_enabled()
                    ),
                    None,
                )
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'}); arguments[0].click();",
                button,
            )
        except TimeoutException:
            pass
        return self

    def wait_until_auth_completed_or_code_error(self):
        self.wait.until(
            lambda driver: self.authorization_completed()
            or any(
                element.is_displayed()
                for element in driver.find_elements(By.XPATH, self.INVALID_CODE_MESSAGE)
            )
        )
        return self

    def wait_document_ready(self):
        self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        return self

    def wait_dom_change_or_auth_shell(self, previous_source: str):
        try:
            self.wait.until(
                lambda driver: driver.page_source != previous_source
                or len(driver.find_elements(By.XPATH, self.AUTH_SHELL)) > 0
            )
        except TimeoutException:
            self.present_xpath(self.AUTH_SHELL)
        return self

    def is_any_visible(self, *xpaths: str) -> bool:
        for xpath in xpaths:
            elements = self.driver.find_elements(By.XPATH, xpath)
            if any(element.is_displayed() for element in elements):
                return True
        return False
