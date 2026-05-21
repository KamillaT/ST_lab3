from pages.base_page import BasePage


class SuburbanPage(BasePage):
    SEARCH_BUTTON = (
        "(//*[self::button or self::a or @role='button' or self::div or self::span]"
        "[contains(normalize-space(.), 'Найти') or contains(normalize-space(.), 'Поиск') "
        "or contains(normalize-space(.), 'расписание') or contains(normalize-space(.), 'Расписание')])[1]"
    )

    def open_suburban_page(self):
        self.open_relative("/prigorod/")
        self.wait_body_contains_any("Электрич", "электрич", "Расписание", "Откуда", "станция")
        return self

    def search_route(self, from_station: str, to_station: str):
        self.set_visible_input(1, from_station)
        self.set_visible_input(2, to_station)
        self.set_tomorrow_date_if_possible()
        self.click_xpath(self.SEARCH_BUTTON)
        self.wait_body_contains_any("электрич", "Расписание", "поезд", "станция", from_station, to_station)
        return self
