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

    def open_bus_page(self):
        self.open("https://bus.tutu.ru/")
        self.wait_body_contains_any("Автобус", "автобус", "Найти", "билет", "рейс")
        return self

    def search_route(self, from_city: str, to_city: str):
        self.set_visible_input(1, from_city)
        self.set_visible_input(2, to_city)
        self.set_tomorrow_date_if_possible()
        self.click_xpath(self.SEARCH_BUTTON)
        self.wait_body_contains_any("автобус", "рейс", "билет", "маршрут", from_city, to_city)
        return self

    def open_refund(self):
        self.wait_body_contains_any("возврат", "Вернуть", "заказ", "билет")
        self.click_xpath_if_present(self.REFUND_LINK)
        self.wait_body_contains_any("возврат", "заказ", "билет", "номер", "Вернуть")
        return self
