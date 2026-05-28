from datetime import datetime, timedelta
from time import sleep

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    JavascriptException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    BASE_URL = "https://www.tutu.ru"

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def log_step(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[STEP {timestamp}] {self.__class__.__name__}: {message}", flush=True)
        return self

    def open(self, url: str):
        self.log_step(f"открываю страницу: {url}")
        try:
            self.driver.get(url)
        except TimeoutException:
            # Не sleep: останавливаем долгую загрузку и дальше ждём DOM через WebDriverWait.
            self.driver.execute_script("window.stop();")
        self.wait_body()
        return self

    def open_relative(self, path: str):
        return self.open(self.BASE_URL + path)

    def wait_body(self):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//body")))
        return self

    def visible_xpath(self, xpath: str):
        return self.wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))

    def present_xpath(self, xpath: str):
        return self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

    def clickable_xpath(self, xpath: str):
        return self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

    def first_present_xpath(self, *xpaths: str):
        last_error = None
        for xpath in xpaths:
            try:
                return self.present_xpath(xpath)
            except TimeoutException as error:
                last_error = error
        raise last_error or TimeoutException("No XPath candidates were provided")

    def first_visible_xpath(self, *xpaths: str):
        last_error = None
        for xpath in xpaths:
            try:
                self.wait.until(
                    lambda driver: any(
                        element.is_displayed()
                        for element in driver.find_elements(By.XPATH, xpath)
                    )
                )
                for element in self.driver.find_elements(By.XPATH, xpath):
                    if element.is_displayed():
                        return element
            except TimeoutException as error:
                last_error = error
        raise last_error or TimeoutException("No XPath candidates were provided")

    def click_first_xpath(self, *xpaths: str):
        last_error = None
        for xpath in xpaths:
            try:
                return self.click_xpath(xpath)
            except TimeoutException as error:
                last_error = error
        raise last_error or TimeoutException("No clickable XPath candidates were found")

    def click_xpath(self, xpath: str):
        element = self.clickable_xpath(xpath)
        sleep(1)
        try:
            element.click()
        except TimeoutException:
            self.driver.execute_script("window.stop();")
        except (ElementClickInterceptedException, JavascriptException):
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'}); arguments[0].click();",
                element,
            )
        return self

    def click_xpath_if_present(self, xpath: str):
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'}); arguments[0].click();",
                element,
            )
        except NoSuchElementException:
            pass
        return self

    def set_value_by_xpath(self, xpath: str, value: str):
        element = self.visible_xpath(xpath)
        self.driver.execute_script(
            """
            arguments[0].focus();
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new InputEvent('input', {
                bubbles: true,
                inputType: 'insertText',
                data: arguments[1]
            }));
            arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
            """,
            element,
            value,
        )
        return self

    def type_value_by_xpath(self, xpath: str, value: str, submit: bool = False):
        element = self.visible_xpath(xpath)
        element.click()
        element.send_keys(Keys.COMMAND, "a")
        element.send_keys(value)
        if submit:
            element.send_keys(Keys.ENTER)
        return self

    def future_date(self, days: int = 1, fmt: str = "%d.%m.%Y") -> str:
        return (datetime.now() + timedelta(days=days)).strftime(fmt)

    def visible_input_xpath(self, number_from_one: int) -> str:
        return f"(//*[self::input or self::textarea][not(@type='hidden') and not(@disabled)])[{number_from_one}]"

    def set_visible_input(self, number_from_one: int, value: str):
        return self.set_value_by_xpath(self.visible_input_xpath(number_from_one), value)

    def set_first_visible_xpath(self, value: str, *xpaths: str):
        element = self.first_visible_xpath(*xpaths)
        self.driver.execute_script(
            """
            arguments[0].focus();
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new InputEvent('input', {
                bubbles: true,
                inputType: 'insertText',
                data: arguments[1]
            }));
            arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
            """,
            element,
            value,
        )
        return self

    def clear_first_visible_inputs(self, count: int = 3):
        for index in range(1, count + 1):
            try:
                self.set_visible_input(index, "")
            except TimeoutException:
                break
        return self

    def set_tomorrow_date_if_possible(self):
        tomorrow = datetime.now() + timedelta(days=1)
        date_value = tomorrow.strftime("%d.%m.%Y")

        date_xpaths = [
            "(//input[not(@type='hidden') and not(@disabled) and contains(@placeholder, 'Дата')])[1]",
            "(//input[not(@type='hidden') and not(@disabled) and contains(@placeholder, 'Когда')])[1]",
            "(//input[not(@type='hidden') and not(@disabled) and contains(@aria-label, 'Дата')])[1]",
            "(//input[not(@type='hidden') and not(@disabled) and contains(@name, 'date')])[1]",
            self.visible_input_xpath(3),
        ]

        for xpath in date_xpaths:
            try:
                self.set_value_by_xpath(xpath, date_value)
                return self
            except TimeoutException:
                continue

        return self

    def body_text(self) -> str:
        return self.driver.find_element(By.XPATH, "//body").text

    def close_obstructive_popups(self):
        close_buttons = [
            "//*[self::button or @role='button'][@aria-label='Закрыть' or @title='Закрыть']",
            "//*[self::button or @role='button'][contains(normalize-space(.), 'Закрыть')]",
            "//*[self::button or @role='button'][contains(normalize-space(.), 'Понятно')]",
            "//*[self::button or @role='button'][contains(normalize-space(.), 'Не сейчас')]",
        ]
        for xpath in close_buttons:
            self.click_xpath_if_present(xpath)
        return self

    def wait_body_contains_any(self, *words: str):
        self.wait.until(
            lambda driver: any(
                word.lower() in driver.find_element(By.XPATH, "//body").text.lower()
                for word in words
            )
        )
        return self

    def wait_body_contains_all(self, *words: str):
        self.wait.until(
            lambda driver: all(
                word.lower() in driver.find_element(By.XPATH, "//body").text.lower()
                for word in words
            )
        )
        return self

    def assert_body_contains_any(self, *words: str):
        text = self.body_text().lower()
        assert any(word.lower() in text for word in words), (
            "На странице не найден ни один из ожидаемых фрагментов: "
            + ", ".join(words)
        )
        return self

    def assert_body_contains_all(self, *words: str):
        text = self.body_text().lower()
        missing = [word for word in words if word.lower() not in text]
        assert not missing, "На странице не найдены ожидаемые фрагменты: " + ", ".join(missing)
        return self

    def assert_has_visible_xpath(self, xpath: str, message: str):
        elements = self.driver.find_elements(By.XPATH, xpath)
        assert any(element.is_displayed() for element in elements), message
        return self

    def wait_results_page_loaded(self, *words: str):
        self.wait_body_contains_any(*words)
        self.wait.until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        return self

    def click_first_available_xpath(self, *xpaths: str):
        for xpath in xpaths:
            try:
                self.wait.until(
                    lambda driver: any(
                        element.is_displayed()
                        for element in driver.find_elements(By.XPATH, xpath)
                    )
                )
            except TimeoutException:
                continue

            for _ in range(3):
                for element in self.driver.find_elements(By.XPATH, xpath):
                    try:
                        if not element.is_displayed():
                            continue
                        sleep(1)
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block:'center'}); arguments[0].click();",
                            element,
                        )
                        return self
                    except StaleElementReferenceException:
                        break
        return self
