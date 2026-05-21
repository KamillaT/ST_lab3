from pages.base_page import BasePage


class HotelPage(BasePage):
    HOTEL_SECTION = (
        "(//*[self::a or self::button or @role='button' or self::div or self::span]"
        "[contains(normalize-space(.), 'Отели') or contains(normalize-space(.), 'отели') "
        "or contains(normalize-space(.), 'Гостиниц') or contains(normalize-space(.), 'жиль') "
        "or contains(normalize-space(.), 'Жиль')])[1]"
    )

    SEARCH_BUTTON = (
        "(//*[self::button or self::a or @role='button' or self::div or self::span]"
        "[contains(normalize-space(.), 'Найти') or contains(normalize-space(.), 'Поиск') "
        "or contains(normalize-space(.), 'Показать')])[1]"
    )

    def open_hotels_from_main(self):
        self.open_relative("/")
        self.click_xpath_if_present(self.HOTEL_SECTION)
        self.wait_body_contains_any("отел", "гостиниц", "жиль", "город", "Найти", "заезд")
        return self

    def search_city(self, city: str):
        self.set_visible_input(1, city)
        self.set_tomorrow_date_if_possible()
        self.click_xpath_if_present(self.SEARCH_BUTTON)
        self.wait_body_contains_any("отел", "гостиниц", "жиль", city, "Найти", "город")
        return self
