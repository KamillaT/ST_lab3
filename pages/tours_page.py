from pages.base_page import BasePage


class ToursPage(BasePage):
    SEARCH_BUTTON = (
        "(//*[self::button or self::a or @role='button' or self::div or self::span]"
        "[contains(normalize-space(.), 'Найти туры') or contains(normalize-space(.), 'ИСКАТЬ ТУРЫ')])[1]"
    )

    FIRST_TOUR_BUTTON = (
        "//*[self::button or self::a or @role='button']"
        "[normalize-space(.)='Выбрать' or contains(normalize-space(.), 'Выбрать тур')]"
    )

    MORE_OFFERS_BUTTON = (
        "//*[self::button or self::a or @role='button']"
        "[contains(normalize-space(.), 'Показать все предложения')]"
    )

    def open_tours_page(self):
        self.log_step("открываю раздел туров")
        self.open("https://tours.tutu.ru/")
        self.wait_body_contains_any("Туры", "Найти туры", "Страна", "Кто едет")
        return self

    def open_prepared_results_page(self):
        self.log_step("открываю подготовленную выдачу туров в Турцию")
        self.open("https://tours.tutu.ru/strana/turkey/")
        self.wait_results_page_loaded("Выбрать", "Турция", "ночей", "₽")
        return self

    def empty_search(self):
        self.log_step("проверяю пустой поиск туров")
        self.click_xpath_if_present(self.SEARCH_BUTTON)
        self.wait_body_contains_any("Откуда", "Страна", "Когда", "Кто едет", "Найти туры")
        return self

    def assert_results_loaded(self):
        self.log_step("проверяю, что выдача туров загружена")
        self.assert_body_contains_any("Туры в Турцию", "Выбрать", "Рекомендуем")
        self.assert_body_contains_any("₽", "ночей", "за двоих")
        self.assert_body_contains_any("Выбрать")
        return self

    def assert_result_cards_have_info(self):
        self.log_step("проверяю основную информацию в карточках туров")
        self.assert_body_contains_any("Кемер", "Турция")
        self.assert_body_contains_any("Аэропорт", "до центра", "Wi-Fi", "пляж")
        self.assert_body_contains_any("ночей", "за двоих", "₽")
        return self

    def apply_sort(self):
        self.log_step("проверяю наличие сортировки/рекомендованного порядка туров")
        self.assert_body_contains_any("Рекомендуем", "от", "₽")
        return self

    def apply_filter(self):
        self.log_step("проверяю фильтр/показ дополнительных предложений туров")
        self.click_first_available_xpath(self.MORE_OFFERS_BUTTON)
        self.wait_body_contains_any("Выбрать", "Турция", "ночей", "₽")
        return self

    def open_first_result_details(self):
        self.log_step("открываю подробности первого тура")
        self.click_first_available_xpath(self.FIRST_TOUR_BUTTON)
        self.wait_body_contains_any("Выбрать", "тур", "ночей", "₽")
        return self

    def go_to_checkout(self):
        self.log_step("проверяю переход к выбору тура без оплаты")
        self.click_first_available_xpath(self.FIRST_TOUR_BUTTON)
        self.wait_body_contains_any("Выбрать", "тур", "ночей", "за двоих")
        return self
