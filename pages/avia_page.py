from time import sleep
import random

from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class AviaPage(BasePage):
    FROM_FIELD = "(//input[@data-ti='input' and not(@disabled)])[1]"
    TO_FIELD = "(//input[@data-ti='input' and not(@disabled)])[2]"
    DEPARTURE_DATE_FIELD = "//input[@data-ti='trip-dates']"
    RETURN_DATE_FIELD = "//input[@data-ti='trip-second-date']"
    PASSENGERS_FIELD = "//input[@data-ti='passengers_input']"
    ADD_ADULT_BUTTON = "//*[@data-ti='plus_button' or @aria-label='Добавить пассажира']"
    HOTEL_EXTENSION_SWITCH = "//input[@data-ti='switch']"
    SEARCH_BUTTON = "//button[@data-ti='submit-button']"
    FIRST_RESULT_BUTTON = (
        "//*[self::button or self::a or @role='button']"
        "[contains(normalize-space(.), 'Выбрать билет') or contains(normalize-space(.), 'Купить')]"
    )
    TARIFF_BUTTON = "//*[self::button or @role='button'][normalize-space(.)='Выбрать']"
    OPEN_CHECKOUT_BUTTON = (
        "//*[self::button or @role='button']"
        "[contains(normalize-space(.), 'Оформить') or contains(normalize-space(.), 'Продолжить')]"
    )
    CONTINUE_BUTTON = "//*[self::button or @role='button'][contains(normalize-space(.), 'Продолжить')]"
    VALIDATION_ERROR = (
        "//*[contains(@class, 'error') and ("
        "@data-ti='input-root' or @data-ti='trip-dates-root' or @data-ti='input-label' or @data-ti='trip-dates-label'"
        ")]"
    )

    def open_avia_page(self):
        self.log_step("открываю раздел авиабилетов")
        self.open("https://avia.tutu.ru/")
        self.wait_body_contains_any("Авиа", "авиа", "Самол", "Откуда", "Куда", "билет")
        self.close_cookie_notice()
        return self

    def fill_route(self, from_city: str | None = None, to_city: str | None = None):
        self.log_step(f"заполняю маршрут: {from_city or '[пусто]'} -> {to_city or '[пусто]'}")
        if from_city is not None:
            self.type_avia_city(self.FROM_FIELD, from_city)
        if to_city is not None:
            self.type_avia_city(self.TO_FIELD, to_city)
        return self

    def type_avia_city(self, xpath: str, city: str):
        self.close_cookie_notice()
        element = self.visible_xpath(xpath)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        sleep(1)
        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].focus(); arguments[0].click();", element)
        element.send_keys(Keys.COMMAND, "a")
        element.send_keys(Keys.BACKSPACE)
        element.send_keys(city)
        self.wait.until(lambda driver: city.lower() in element.get_attribute("value").lower())
        sleep(1)
        element.send_keys(Keys.ARROW_DOWN)
        element.send_keys(Keys.ENTER)
        sleep(1)
        return self

    def disable_hotel_search_extension(self):
        switch = self.first_present_xpath(self.HOTEL_EXTENSION_SWITCH)
        if switch.is_selected():
            self.click_xpath(self.HOTEL_EXTENSION_SWITCH)
        return self

    def fill_round_trip_dates(self):
        self.log_step("выбираю даты туда и обратно")
        self.click_xpath("(//button[normalize-space(.)='Завтра'])[1]")
        self.click_xpath("(//button[normalize-space(.)='Послезавтра'])[1]")
        self.wait.until(lambda driver: self.visible_xpath(self.DEPARTURE_DATE_FIELD).get_attribute("value"))
        self.wait.until(lambda driver: self.visible_xpath(self.RETURN_DATE_FIELD).get_attribute("value"))
        return self

    def fill_departure_date_only(self):
        self.log_step("выбираю только дату туда для негативного сценария")
        self.click_xpath("(//button[normalize-space(.)='Завтра'])[1]")
        self.wait.until(lambda driver: self.visible_xpath(self.DEPARTURE_DATE_FIELD).get_attribute("value"))
        return self

    def set_adults_count(self, adults_count: int):
        self.log_step(f"устанавливаю пассажиров: взрослых {adults_count}")
        if adults_count <= 1:
            return self

        passenger_input = self.first_visible_xpath(self.PASSENGERS_FIELD)
        passenger_input.click()
        for _ in range(adults_count - 1):
            self.click_first_available_xpath(self.ADD_ADULT_BUTTON)
        self.driver.find_element("xpath", "//body").send_keys(Keys.ESCAPE)
        self.wait.until(
            lambda driver: any(
                element.is_displayed() and str(adults_count) in element.get_attribute("value")
                for element in driver.find_elements("xpath", self.PASSENGERS_FIELD)
            )
        )
        return self

    def search_route(self, from_city: str, to_city: str, adults_count: int = 2):
        self.log_step("запускаю позитивный поиск авиабилетов")
        self.disable_hotel_search_extension()
        self.fill_route(from_city, to_city)
        self.fill_round_trip_dates()
        self.set_adults_count(adults_count)
        self.driver.execute_script("document.activeElement.blur();")
        current_url = self.driver.current_url
        self.click_xpath(self.SEARCH_BUTTON)
        self.wait.until(
            lambda driver: (
                driver.current_url != current_url
                and (
                    "avia.tutu.ru/f/" in driver.current_url
                    or "avia.tutu.ru/offers" in driver.current_url
                )
            )
            or "выбрать билет" in driver.find_element("xpath", "//body").text.lower()
        )
        self.wait_body_contains_all("Выбрать билет", "₽")
        return self

    def assert_results_loaded(self):
        self.log_step("проверяю, что авиа-выдача загружена")
        self.assert_body_contains_any("Выбрать билет", "рейс", "авиа", "пересад")
        self.assert_body_contains_any("₽", "руб")
        self.assert_body_contains_any("Выбрать билет", "Купить")
        return self

    def assert_result_cards_have_info(self):
        self.log_step("проверяю основную информацию в карточках авиабилетов")
        self.assert_body_contains_any("Москва", "Внуково", "Шереметьево", "Домодедово")
        self.assert_body_contains_any("Санкт-Петербург", "Пулково")
        self.assert_body_contains_any("в пути", "пересад", "багаж")
        return self

    def apply_sort(self):
        self.log_step("проверяю сортировку в авиа-выдаче")
        self.click_first_available_xpath(
            "//*[self::button or @role='button'][contains(normalize-space(.), 'Сначала')]",
            "//*[self::button or @role='button'][contains(normalize-space(.), 'дешев')]",
            "//*[self::button or @role='button'][contains(normalize-space(.), 'быстр')]",
        )
        self.wait_body_contains_any("Выбрать билет", "рейс", "авиа", "₽")
        return self

    def apply_filter(self):
        self.log_step("проверяю фильтр в авиа-выдаче")
        self.click_first_available_xpath(
            "//*[self::label or self::button or @role='button'][contains(normalize-space(.), 'Без пересадок')]",
            "//*[self::label or self::button or @role='button'][contains(normalize-space(.), 'Багаж')]",
            "//*[self::label or self::button or @role='button'][contains(normalize-space(.), 'Авиакомп')]",
        )
        self.wait_body_contains_any("Выбрать билет", "рейс", "авиа", "₽")
        return self

    def open_first_result_details(self):
        self.log_step("открываю подробности первого авиаварианта")
        self.click_first_available_xpath(
            "(//*[self::button or @role='button'][contains(normalize-space(.), 'Подробнее')])[1]",
            "(//*[self::button or @role='button'][contains(normalize-space(.), 'Детали')])[1]",
            "(//*[self::button or @role='button'][contains(normalize-space(.), 'рейс')])[1]",
        )
        self.wait_body_contains_any("рейс", "багаж", "пересад", "авиа", "Выбрать билет")
        return self

    def go_to_checkout(self):
        self.log_step("перехожу к оформлению авиабилета без оплаты")
        for _ in range(3):
            self.click_first_available_xpath(self.FIRST_RESULT_BUTTON)
            try:
                self.wait_body_contains_any("Выберите тариф", "Оформить билеты")
                break
            except TimeoutException:
                continue

        self.click_first_available_xpath(self.TARIFF_BUTTON)
        self.wait_body_contains_any("Оформить билеты", "Оформить")
        self.click_first_available_xpath(self.OPEN_CHECKOUT_BUTTON)
        checkout_wait = WebDriverWait(self.driver, 45)
        checkout_wait.until(lambda driver: "checkout.tutu.ru/cart" in driver.current_url)
        checkout_wait.until(
            lambda driver: any(
                word in driver.find_element("xpath", "//body").text
                for word in ("Заполните данные", "Пассажир 1", "Покупатель")
            )
        )
        return self

    def fill_checkout_to_payment(self):
        self.log_step("заполняю пассажиров и покупателя случайными данными")
        self.click_xpath_if_present("//*[self::button or @role='button'][contains(normalize-space(.), 'Соглашаюсь')]")
        suffix = random.randint(10000, 99999)
        name_values = ["IVANOV", "IVAN", "IVANOVICH", "PETROV", "PETR", "PETROVICH"]
        name_fields = [
            element
            for element in self.visible_text_inputs()
            if element.get_attribute("data-ti") == "suggestField"
            and element.get_attribute("placeholder") != "name@site.ru"
        ][:6]
        for element, value in zip(name_fields, name_values, strict=False):
            self.set_element_text(element, value)

        gender_fields = [
            element
            for element in self.visible_text_inputs()
            if element.get_attribute("data-ti") == "selectField"
            and not element.get_attribute("value")
        ][:2]
        for element in gender_fields:
            self.set_element_text(element, "Мужской")
            element.send_keys(Keys.ENTER)

        for element, value in zip(
            self.visible_text_inputs_by_placeholder("ДД.ММ.ГГГГ")[:2],
            ("01.01.1990", "02.02.1991"),
            strict=False,
        ):
            self.set_element_text(element, value)

        for element, value in zip(
            self.visible_text_inputs_by_placeholder("0000 000000")[:2],
            ("4512 345678", "4513 345679"),
            strict=False,
        ):
            self.set_element_text(element, value)

        self.fill_buyer_data(f"tutu-test-{suffix}@example.ru")

        self.click_first_available_xpath(
            "//input[@name='agreements[0].value' and @type='checkbox']"
        )

        payment_words = ("оплата картой", "к оплате", "оплатить", "банковской картой")
        services_words = ("страхование", "выберите услуги", "багаж", "места в самолете")

        self.click_first_available_xpath(self.CONTINUE_BUTTON)
        WebDriverWait(self.driver, 90).until(
            lambda driver: any(
                word in driver.find_element("xpath", "//body").text.lower()
                for word in payment_words + services_words
            )
        )

        if any(word in self.body_text().lower() for word in services_words):
            self.log_step("прохожу экран услуг без оплаты")
            self.click_first_available_xpath(self.CONTINUE_BUTTON)
            WebDriverWait(self.driver, 90).until(
                lambda driver: any(
                    word in driver.find_element("xpath", "//body").text.lower()
                    for word in payment_words
                )
            )

        self.log_step("дошёл до шага оплаты, оплату не выполняю")
        self.assert_body_contains_any("Оплата картой", "К оплате", "Оплатить", "Банковской картой")
        return self

    def fill_buyer_data(self, email: str):
        inputs = self.visible_text_inputs()
        email_index = next(
            index
            for index, element in enumerate(inputs)
            if element.get_attribute("placeholder") == "name@site.ru"
        )

        self.set_element_text(inputs[email_index - 2], "SIDOROV")
        self.set_element_text(inputs[email_index - 1], "SIDOR")
        self.set_element_text(inputs[email_index], email)

        phone = self.first_visible_xpath("//input[@name='customer.contactInfo.phone']")
        self.set_element_text(phone, "+7 999 123-45-67")
        return self

    def visible_text_inputs(self):
        return [
            element
            for element in self.driver.find_elements(
                "xpath",
                "//input[not(@type='hidden') and not(@disabled)]",
            )
            if element.is_displayed() and (element.get_attribute("type") or "text") == "text"
        ]

    def visible_text_inputs_by_placeholder(self, placeholder: str):
        return [
            element
            for element in self.visible_text_inputs()
            if element.get_attribute("placeholder") == placeholder
        ]

    def set_visible_text_input(self, number_from_one: int, value: str):
        inputs = self.visible_text_inputs()
        element = inputs[number_from_one - 1]
        return self.set_element_text(element, value)

    def set_element_text(self, element, value: str):
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        sleep(0.5)
        element.click()
        element.send_keys(Keys.COMMAND, "a")
        element.send_keys(Keys.BACKSPACE)
        element.send_keys(value)
        self.driver.execute_script(
            """
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new InputEvent('input', {bubbles: true}));
            arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
            """,
            element,
            value,
        )
        sleep(0.3)
        return self

    def assert_form_has_round_trip_and_passengers(self, adults_count: int = 2):
        assert self.visible_xpath(self.DEPARTURE_DATE_FIELD).get_attribute("value"), "Дата туда не заполнена"
        assert self.visible_xpath(self.RETURN_DATE_FIELD).get_attribute("value"), "Дата обратно не заполнена"
        assert any(
            element.is_displayed() and str(adults_count) in element.get_attribute("value")
            for element in self.driver.find_elements("xpath", self.PASSENGERS_FIELD)
        ), (
            "Количество пассажиров не изменилось"
        )
        return self

    def empty_search_validation(self):
        self.reset_search_state()
        return self.submit_incomplete_form()

    def origin_only_validation(self, from_city: str):
        self.reset_search_state()
        self.fill_route(from_city=from_city)
        return self.submit_incomplete_form()

    def destination_only_validation(self, to_city: str):
        self.reset_search_state()
        self.fill_route(to_city=to_city)
        return self.submit_incomplete_form()

    def route_without_dates_validation(self, from_city: str, to_city: str):
        self.reset_search_state()
        self.fill_route(from_city, to_city)
        return self.submit_incomplete_form()

    def route_with_departure_only_validation(self, from_city: str, to_city: str):
        self.reset_search_state()
        self.fill_route(from_city, to_city)
        self.fill_departure_date_only()
        return self.submit_incomplete_form()

    def submit_incomplete_form(self):
        self.log_step("отправляю неполную авиа-форму и жду валидацию")
        self.disable_hotel_search_extension()
        current_url = self.driver.current_url
        self.click_xpath(self.SEARCH_BUTTON)
        sleep(2)
        assert "avia.tutu.ru/f/" not in self.driver.current_url, (
            "Негативный авиа-сценарий неожиданно открыл полноценную выдачу"
        )
        self.assert_body_contains_any("Откуда", "Куда", "Когда", "Дата", "Найти")
        return self

    def reset_search_state(self):
        self.log_step("сбрасываю сохранённое состояние авиа-формы")
        try:
            self.driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
            self.driver.delete_all_cookies()
        except Exception:
            pass
        self.open("https://avia.tutu.ru/")
        self.wait_body_contains_any("Авиа", "авиа", "Самол", "Откуда", "Куда", "билет")
        self.close_cookie_notice()
        return self

    def close_cookie_notice(self):
        self.click_xpath_if_present(
            "//*[self::button or @role='button'][contains(normalize-space(.), 'Соглашаюсь')]"
        )
        return self
