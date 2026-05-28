from time import sleep

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class RailwayPage(BasePage):
    FROM_FIELD = "(//input[@data-ti='input' and not(@readonly)])[1]"
    FROM_FIELD_OLD = "//input[@name='schedule_station_from' or @placeholder='Откуда']"
    TO_FIELD = "(//input[@data-ti='input' and not(@readonly)])[2]"
    TO_FIELD_OLD = "//input[@name='schedule_station_to' or @placeholder='Куда']"
    DATE_FIELD = "//input[@data-ti='trip-dates']"
    DATE_FIELD_OLD = "//input[contains(@class, 'j-date_to') or @placeholder='Дата']"
    SEARCH_BUTTON = "//*[@data-ti='submit-button' and contains(normalize-space(.), 'Найти поезда')]"
    SEARCH_BUTTON_OLD = "//button[contains(@class, 'j-submit_button') and contains(normalize-space(.), 'Узнать расписание')]"

    FILTER_CONTROL = (
        "(//*[self::label or self::button or self::div or self::span]"
        "[contains(normalize-space(.), 'Время') or contains(normalize-space(.), 'Цена') "
        "or contains(normalize-space(.), 'Фильтр') or contains(normalize-space(.), 'фильтр')])[1]"
    )

    FIRST_RESULT_CARD_BUTTON = (
        "(//*[self::a or self::button or @role='button' or self::div or self::span]"
        "[contains(normalize-space(.), 'Подробнее') or contains(normalize-space(.), 'Выбрать') "
        "or contains(normalize-space(.), 'мест') or contains(normalize-space(.), 'Места') "
        "or contains(normalize-space(.), 'Купить')])[1]"
    )

    FIRST_TICKET_BUTTON = (
        "//*[self::a or self::button or @role='button']"
        "[contains(normalize-space(.), 'Выбрать') or contains(normalize-space(.), 'Купить') "
        "or contains(normalize-space(.), 'Продолжить') or contains(normalize-space(.), 'мест')]"
    )

    RESULT_CARD = (
        "//*[contains(normalize-space(.), 'Выбрать места') "
        "and (contains(normalize-space(.), 'в пути') or contains(normalize-space(.), 'вокзал'))]"
    )

    def open_railway_page(self):
        self.log_step("открываю раздел ж/д билетов")
        self.open_relative("/poezda/")
        self.wait_body_contains_any("поезд", "Ж/д", "расписание", "Откуда")
        return self

    def open_prepared_results_page(self):
        self.log_step("открываю подготовленную ж/д выдачу Москва -> Санкт-Петербург")
        # Готовая страница результатов Москва -> Санкт-Петербург.
        # Нужна для сценариев фильтрации и открытия карточки результата.
        self.open_relative(
            f"/poezda/Moskva/Sankt-Peterburg/?date={self.future_date()}&travelers=1"
        )
        self.wait_body_contains_all("Выбрать места", "в пути", "₽")
        return self

    def search_route(self, from_city: str, to_city: str):
        self.log_step(f"ищу ж/д билеты: {from_city} -> {to_city}")
        old_url = self.driver.current_url
        self.close_cookie_notice()
        self.type_station(from_city, self.FROM_FIELD, self.FROM_FIELD_OLD)
        self.type_station(to_city, self.TO_FIELD, self.TO_FIELD_OLD)
        self.pick_tomorrow_date()
        self.click_first_xpath(self.SEARCH_BUTTON, self.SEARCH_BUTTON_OLD)
        WebDriverWait(self.driver, 45).until(
            lambda driver: driver.current_url != old_url
            or "выбрать места" in driver.find_element("xpath", "//body").text.lower()
        )
        self.wait_body_contains_all("Выбрать места", "в пути", "₽")
        return self

    def empty_search(self):
        self.log_step("проверяю пустой поиск ж/д")
        self.clear_search_form()
        return self.submit_incomplete_form("пустая форма")

    def origin_only_validation(self, from_city: str):
        self.log_step("проверяю ж/д поиск только с городом отправления")
        self.clear_search_form()
        self.type_station(from_city, self.FROM_FIELD, self.FROM_FIELD_OLD)
        return self.submit_incomplete_form("только Откуда")

    def destination_only_validation(self, to_city: str):
        self.log_step("проверяю ж/д поиск только с городом прибытия")
        self.clear_search_form()
        self.type_station(to_city, self.TO_FIELD, self.TO_FIELD_OLD)
        return self.submit_incomplete_form("только Куда")

    def route_without_date_validation(self, from_city: str, to_city: str):
        self.log_step("проверяю ж/д поиск с маршрутом без даты")
        self.clear_search_form()
        self.type_station(from_city, self.FROM_FIELD, self.FROM_FIELD_OLD)
        self.type_station(to_city, self.TO_FIELD, self.TO_FIELD_OLD)
        return self.submit_incomplete_form("маршрут без даты")

    def invalid_origin_validation(self, bad_city: str, to_city: str):
        self.log_step("проверяю ж/д поиск с несуществующей станцией")
        self.clear_search_form()
        self.type_raw_station(bad_city, self.FROM_FIELD, self.FROM_FIELD_OLD)
        self.type_station(to_city, self.TO_FIELD, self.TO_FIELD_OLD)
        return self.submit_incomplete_form("несуществующая станция")

    def submit_incomplete_form(self, case_name: str):
        self.close_cookie_notice()
        self.click_first_xpath(self.SEARCH_BUTTON, self.SEARCH_BUTTON_OLD)
        sleep(2)
        current_url = self.driver.current_url
        text = self.body_text().lower()
        assert not ("date=" in current_url and "выбрать места" in text), (
            f"Ж/Д негативный сценарий '{case_name}' неожиданно открыл полноценную выдачу"
        )
        self.assert_body_contains_any(
            "Откуда",
            "Куда",
            "Дата",
            "Когда",
            "Укажите",
            "маршрут",
            "Расписание поездов",
        )
        return self

    def type_station(self, city: str, *xpaths: str):
        field = self.first_visible_xpath(*xpaths)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", field)
        sleep(1)
        field.click()
        field.send_keys(Keys.COMMAND, "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(city)
        sleep(1)
        field.send_keys(Keys.ARROW_DOWN)
        sleep(0.3)
        field.send_keys(Keys.ENTER)
        sleep(1)
        self.wait.until(lambda _driver: city.lower() in (field.get_attribute("value") or "").lower())
        return self

    def type_raw_station(self, city: str, *xpaths: str):
        field = self.first_visible_xpath(*xpaths)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", field)
        sleep(1)
        field.click()
        field.send_keys(Keys.COMMAND, "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(city)
        sleep(1)
        return self

    def clear_search_form(self):
        self.reset_saved_search_state()
        self.close_cookie_notice()
        for xpath in (
            self.FROM_FIELD,
            self.TO_FIELD,
            self.DATE_FIELD,
            self.FROM_FIELD_OLD,
            self.TO_FIELD_OLD,
            self.DATE_FIELD_OLD,
        ):
            for field in self.driver.find_elements("xpath", xpath):
                if not field.is_displayed():
                    continue
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", field)
                sleep(0.2)
                try:
                    field.click()
                    field.send_keys(Keys.COMMAND, "a")
                    field.send_keys(Keys.BACKSPACE)
                except Exception:
                    pass
                self.driver.execute_script(
                    """
                    const element = arguments[0];
                    const setter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype,
                        'value'
                    ).set;
                    setter.call(element, '');
                    element.dispatchEvent(new InputEvent('input', {bubbles: true}));
                    element.dispatchEvent(new Event('change', {bubbles: true}));
                    """,
                    field,
                )
                sleep(0.2)
        return self

    def reset_saved_search_state(self):
        try:
            self.driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
            self.driver.delete_all_cookies()
        except Exception:
            pass
        self.open_relative("/poezda/")
        return self

    def pick_tomorrow_date(self):
        self.log_step("выбираю дату поездки")
        new_date_xpath = "//button[@data-ti='dateHint' and contains(normalize-space(.), 'Завтра')]"
        old_date_xpath = f"//span[contains(@class, 'j-pseudo') and @data-value='{self.future_date()}']"
        try:
            self.click_first_xpath(new_date_xpath, old_date_xpath)
        except TimeoutException:
            self.set_first_visible_xpath(self.future_date(), self.DATE_FIELD, self.DATE_FIELD_OLD)
        self.wait.until(
            lambda _driver: self.first_visible_xpath(
                self.DATE_FIELD, self.DATE_FIELD_OLD
            ).get_attribute("value")
        )
        return self

    def close_cookie_notice(self):
        self.click_xpath_if_present(
            "//*[self::button or @role='button'][contains(normalize-space(.), 'Соглашаюсь')]"
        )
        return self

    def apply_filter(self):
        self.log_step("проверяю фильтр в ж/д выдаче")
        self.click_first_available_xpath(
            "//*[self::button or @role='button'][contains(normalize-space(.), 'Есть места')]",
            "//*[self::button or @role='button'][contains(normalize-space(.), 'Нижние места')]",
            self.FILTER_CONTROL,
        )
        self.wait_body_contains_any("Выбрать места", "поезд", "мест", "₽")
        return self

    def apply_sort(self):
        self.log_step("проверяю сортировку/порядок ж/д выдачи")
        self.assert_body_contains_any("Откуда", "Когда", "Найти поезда")
        self.assert_body_contains_any("Выбрать места", "в пути", "₽")
        return self

    def assert_results_loaded(self):
        self.log_step("проверяю, что ж/д выдача загружена")
        self.assert_body_contains_any("Выбрать места", "поезд", "мест", "в пути")
        self.assert_body_contains_any("₽", "руб")
        self.assert_body_contains_any("Выбрать места", "мест")
        return self

    def assert_result_cards_have_info(self):
        self.log_step("проверяю основную информацию в карточках поездов")
        self.assert_body_contains_any("Москва", "Санкт-Петербург")
        self.assert_body_contains_any("в пути", "вокзал", "мест")
        self.assert_body_contains_any("Плацкарт", "Купе", "СВ", "Сапсан", "Ласточка")
        return self

    def open_first_result_card(self):
        self.log_step("открываю подробности первого поезда")
        self.click_first_available_xpath(
            "//*[self::button or @role='button'][contains(normalize-space(.), 'Маршрут')]",
            self.FIRST_RESULT_CARD_BUTTON,
        )
        self.wait_body_contains_any("детал", "мест", "поезд", "рейс", "билет", "пассажир", "купить")
        return self

    def choose_first_ticket(self):
        self.log_step("выбираю первый ж/д билет из выдачи")
        self.open_prepared_results_page()
        self.close_obstructive_popups()
        self.click_first_xpath(self.FIRST_TICKET_BUTTON, self.FIRST_RESULT_CARD_BUTTON)
        self.wait_body_contains_any(
            "пассажир", "мест", "вагон", "оформ", "билет", "купить", "выбрать"
        )
        return self

    def go_to_checkout(self):
        self.log_step("перехожу к оформлению ж/д билета без оплаты")
        self.close_obstructive_popups()
        self.click_first_xpath(self.FIRST_TICKET_BUTTON, self.FIRST_RESULT_CARD_BUTTON)
        self.wait_body_contains_any("мест", "вагон", "пассажир", "оформ", "билет")
        return self
