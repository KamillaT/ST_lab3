from pages.base_page import BasePage


class BusPage(BasePage):
    SEARCH_BUTTON = (
        "(//*[self::button or self::a or @role='button' or self::div or self::span]"
        "[contains(normalize-space(.), 'Найти') or contains(normalize-space(.), 'Поиск') "
        "or contains(normalize-space(.), 'Показать')])[1]"
    )

    REFUND_LINK = (
        "(//*[self::a or self::button or @role='button' or self::div or self::span]"
        "[contains(normalize-space(.), 'Вернуть') or contains(normalize-space(.), 'вернуть') "
        "or contains(normalize-space(.), 'Возврат') or contains(normalize-space(.), 'возврат') "
        "or contains(normalize-space(.), 'заказ')])[1]"
    )

    FIRST_RESULT_BUTTON = (
        "//*[self::button or self::a or @role='button']"
        "[contains(normalize-space(.), 'Купить билет') or contains(normalize-space(.), 'Выбрать')]"
    )

    SORT_CONTROL = (
        "(//*[self::button or @role='button' or self::div]"
        "[contains(normalize-space(.), 'По времени отправления') or contains(normalize-space(.), 'Цена')])[1]"
    )

    def open_bus_page(self):
        self.log_step("открываю раздел автобусов")
        self.open("https://bus.tutu.ru/")
        self.wait_body_contains_any("Автобус", "автобус", "Найти", "билет", "рейс")
        return self

    def search_route(self, from_city: str, to_city: str):
        self.log_step(f"ищу автобусные билеты: {from_city} -> {to_city}")
        self.set_visible_input(1, from_city)
        self.set_visible_input(2, to_city)
        self.set_tomorrow_date_if_possible()
        self.click_xpath(self.SEARCH_BUTTON)
        self.wait_body_contains_any("автобус", "рейс", "билет", "маршрут", from_city, to_city)
        return self

    def open_prepared_results_page(self):
        self.log_step("открываю подготовленную автобусную выдачу Москва -> Санкт-Петербург")
        date = self.future_date()
        self.open(
            "https://bus.tutu.ru/raspisanie/gorod_Moskva/gorod_Sankt-Peterburg/"
            f"?from=1447874&to=1447624&date={date}&travelers=1&amount=1"
        )
        self.wait_body_contains_all("Купить билет", "в пути")
        return self

    def empty_search(self):
        self.log_step("проверяю пустой поиск автобусов")
        self.clear_first_visible_inputs(3)
        self.click_xpath(self.SEARCH_BUTTON)
        self.wait_body_contains_any("Откуда", "Куда", "Укажите", "Билеты на автобус")
        return self

    def assert_results_loaded(self):
        self.log_step("проверяю, что автобусная выдача загружена")
        self.assert_body_contains_any("Купить билет", "автобус", "рейс", "в пути")
        self.assert_body_contains_any("₽", "руб", "за одного")
        self.assert_body_contains_any("Купить билет", "Выбрать")
        return self

    def assert_result_cards_have_info(self):
        self.log_step("проверяю основную информацию в карточках автобусов")
        self.assert_body_contains_any("Москва", "Санкт-Петербург")
        self.assert_body_contains_any("в пути", "Автовокзал", "перевозчик", "отзыв")
        self.assert_body_contains_any("за одного", "мест")
        return self

    def apply_sort(self):
        self.log_step("проверяю сортировку в автобусной выдаче")
        self.click_first_available_xpath(self.SORT_CONTROL)
        self.wait_body_contains_any("Купить билет", "По времени", "₽")
        return self

    def apply_filter(self):
        self.log_step("проверяю фильтр/быстрый переключатель в автобусной выдаче")
        self.click_first_available_xpath(
            "//*[self::button or @role='button'][contains(normalize-space(.), 'Самый дешёвый')]",
            "//*[self::button or @role='button'][contains(normalize-space(.), 'Отели')]",
            "//*[self::button or @role='button'][contains(normalize-space(.), 'Авиа')]",
        )
        self.wait_body_contains_any("Купить билет", "автобус", "₽")
        return self

    def open_first_result_details(self):
        self.log_step("открываю подробности первого автобусного рейса")
        self.click_first_available_xpath(
            "(//*[self::button or @role='button'][contains(normalize-space(.), 'Маршрут')])[1]",
            "(//*[self::button or @role='button'][contains(normalize-space(.), 'отзыв')])[1]",
        )
        self.wait_body_contains_any("маршрут", "автобус", "перевозчик", "Купить билет")
        return self

    def go_to_checkout(self):
        self.log_step("перехожу к оформлению автобусного билета без оплаты")
        self.click_first_available_xpath(self.FIRST_RESULT_BUTTON)
        self.wait_body_contains_any("пассажир", "оформ", "билет", "телефон", "мест")
        return self

    def open_refund(self):
        self.log_step("открываю сценарий возврата автобусного билета")
        self.wait_body_contains_any("возврат", "Вернуть", "заказ", "билет")
        self.click_xpath_if_present(self.REFUND_LINK)
        self.wait_body_contains_any("возврат", "заказ", "билет", "номер", "Вернуть")
        return self
