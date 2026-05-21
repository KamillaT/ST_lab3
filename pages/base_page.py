from datetime import datetime, timedelta

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    JavascriptException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    BASE_URL = "https://www.tutu.ru"

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url: str):
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

    def click_xpath(self, xpath: str):
        element = self.clickable_xpath(xpath)
        try:
            element.click()
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

    def visible_input_xpath(self, number_from_one: int) -> str:
        return f"(//*[self::input or self::textarea][not(@type='hidden') and not(@disabled)])[{number_from_one}]"

    def set_visible_input(self, number_from_one: int, value: str):
        return self.set_value_by_xpath(self.visible_input_xpath(number_from_one), value)

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

    def wait_body_contains_any(self, *words: str):
        self.wait.until(
            lambda driver: any(
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
