from pages.base_page import BasePage


class AviaPage(BasePage):
    SEARCH_BUTTON = (
        "(//*[self::button or self::a or @role='button' or self::div or self::span]"
        "[contains(normalize-space(.), 'Найти') or contains(normalize-space(.), 'Поиск') "
        "or contains(normalize-space(.), 'Показать')])[1]"
    )

    def open_avia_page(self):
        self.open("https://avia.tutu.ru/")
        self.wait_body_contains_any("Авиа", "авиа", "Самол", "Откуда", "Куда", "билет")
        return self

    def search_route(self, from_city: str, to_city: str):
        self.set_visible_input(1, from_city)
        self.set_visible_input(2, to_city)
        self.set_tomorrow_date_if_possible()
        self.click_xpath(self.SEARCH_BUTTON)
        self.wait_body_contains_any("рейс", "авиа", "билет", "пассажир", from_city, to_city)
        return self
