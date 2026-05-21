from pages.base_page import BasePage


class RailwayPage(BasePage):
    SEARCH_BUTTON = (
        "(//*[self::button or self::a or @role='button' or self::div or self::span]"
        "[contains(normalize-space(.), 'Найти') or contains(normalize-space(.), 'Поиск') "
        "or contains(normalize-space(.), 'расписание') or contains(normalize-space(.), 'Расписание')])[1]"
    )

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

    def open_railway_page(self):
        self.open_relative("/poezda/")
        self.wait_body_contains_any("поезд", "Ж/д", "расписание", "Откуда")
        return self

    def open_prepared_results_page(self):
        # Готовая страница результатов Москва -> Санкт-Петербург.
        # Нужна для сценариев фильтрации и открытия карточки результата.
        self.open_relative("/poezda/rasp_d.php?nnst1=2000000&nnst2=2004000")
        self.wait_body_contains_any("поезд", "расписание", "билет", "мест")
        return self

    def search_route(self, from_city: str, to_city: str):
        self.visible_xpath(self.visible_input_xpath(1))
        self.set_visible_input(1, from_city)
        self.set_visible_input(2, to_city)
        self.set_tomorrow_date_if_possible()
        self.click_xpath(self.SEARCH_BUTTON)
        self.wait_body_contains_any("поезд", "расписание", "билет", "мест", from_city, to_city)
        return self

    def empty_search(self):
        self.clear_first_visible_inputs(3)
        self.click_xpath(self.SEARCH_BUTTON)
        self.wait_body_contains_any("Откуда", "Куда", "Укажите", "маршрут")
        return self

    def apply_filter(self):
        self.click_xpath_if_present(self.FILTER_CONTROL)
        self.wait_body_contains_any("фильтр", "Время", "Цена", "поезд", "расписание")
        return self

    def open_first_result_card(self):
        self.click_xpath(self.FIRST_RESULT_CARD_BUTTON)
        self.wait_body_contains_any("детал", "мест", "поезд", "рейс", "билет", "пассажир", "купить")
        return self
