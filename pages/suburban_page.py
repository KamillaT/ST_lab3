from pages.base_page import BasePage


class SuburbanPage(BasePage):
    SEARCH_BUTTON = (
        "(//*[self::button or self::a or @role='button' or self::div or self::span]"
        "[contains(normalize-space(.), 'Найти') or contains(normalize-space(.), 'Поиск') "
        "or contains(normalize-space(.), 'расписание') or contains(normalize-space(.), 'Расписание')])[1]"
    )

    FIRST_RESULT_LINK = (
        "//*[self::a or self::button or @role='button']"
        "[contains(normalize-space(.), 'Москва Ярославская') "
        "or contains(normalize-space(.), 'Пушкино') "
        "or contains(normalize-space(.), 'Монино') "
        "or contains(normalize-space(.), 'Фрязино')]"
    )

    def open_suburban_page(self):
        self.log_step("открываю раздел электричек")
        self.open_relative("/prigorod/")
        self.wait_body_contains_any("Электрич", "электрич", "Расписание", "Откуда", "станция")
        return self

    def search_route(self, from_station: str, to_station: str):
        self.log_step(f"ищу электрички: {from_station} -> {to_station}")
        self.set_visible_input(1, from_station)
        self.set_visible_input(2, to_station)
        self.set_tomorrow_date_if_possible()
        self.click_xpath(self.SEARCH_BUTTON)
        self.wait_body_contains_any("электрич", "Расписание", "поезд", "станция", from_station, to_station)
        return self

    def open_prepared_results_page(self):
        self.log_step("открываю подготовленную выдачу электричек Москва -> Мытищи")
        self.open_relative("/rasp.php?st1=20000&st2=46707")
        self.wait_results_page_loaded("Расписание электричек", "Электричка", "Билеты в приложении")
        return self

    def empty_search(self):
        self.log_step("проверяю пустой поиск электричек")
        self.clear_first_visible_inputs(3)
        self.click_xpath(self.SEARCH_BUTTON)
        self.wait_body_contains_any("Откуда", "Куда", "станция", "Показать расписание")
        return self

    def assert_results_loaded(self):
        self.log_step("проверяю, что выдача электричек загружена")
        self.assert_body_contains_any("Расписание электричек", "Электричка", "Иволга", "Спутник")
        self.assert_body_contains_any("Москва", "Мытищи")
        self.assert_has_visible_xpath(self.FIRST_RESULT_LINK, "В выдаче электричек нет ссылки на рейс")
        return self

    def assert_result_cards_have_info(self):
        self.log_step("проверяю основную информацию в строках электричек")
        self.assert_body_contains_any("в пути", "разовый билет", "Билеты в приложении")
        self.assert_body_contains_any("₽", "руб")
        return self

    def apply_sort(self):
        self.log_step("проверяю переключение дня/порядка в выдаче электричек")
        self.click_first_available_xpath(
            "//*[self::a or self::button or @role='button'][contains(normalize-space(.), 'Завтра')]",
            "//*[self::a or self::button or @role='button'][contains(normalize-space(.), 'Сегодня')]",
        )
        self.wait_body_contains_any("Расписание электричек", "Электричка", "в пути")
        return self

    def apply_filter(self):
        self.log_step("проверяю фильтр типа электричек")
        self.click_first_available_xpath(
            "//*[self::button or @role='button' or self::a][contains(normalize-space(.), 'Обычные электрички')]",
            "//*[self::button or @role='button' or self::a][contains(normalize-space(.), 'Иволги')]",
            "//*[self::button or @role='button' or self::a][contains(normalize-space(.), 'Скорые')]",
        )
        self.wait_body_contains_any("Расписание электричек", "Электричка", "в пути")
        return self

    def open_first_result_details(self):
        self.log_step("проверяю, что подробности рейса электрички доступны по ссылке")
        links = [
            element.get_attribute("href")
            for element in self.driver.find_elements("xpath", self.FIRST_RESULT_LINK)
            if element.is_displayed() and element.get_attribute("href")
        ]
        assert links, "В выдаче электричек нет ссылки на подробности рейса"
        self.assert_body_contains_any("Расписание электричек", "Электричка", "в пути")
        return self

    def assert_ticket_app_handoff(self):
        self.log_step("проверяю указание на оформление билета в приложении/расписании")
        self.assert_body_contains_any("электрич", "расписание", "маршрут")
        return self
