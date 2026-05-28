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

    FIRST_HOTEL_LINK = (
        "//a[contains(@href, 'hotel.tutu.ru/h_') and normalize-space(.)!='']"
    )

    BOOK_BUTTON = (
        "//*[self::button or self::a or @role='button']"
        "[contains(normalize-space(.), 'Выбрать') "
        "or contains(normalize-space(.), 'Забронировать') "
        "or contains(normalize-space(.), 'Бронировать')]"
    )

    def open_hotels_from_main(self):
        self.log_step("открываю раздел отелей с главной")
        self.open_relative("/")
        self.click_xpath_if_present(self.HOTEL_SECTION)
        self.wait_body_contains_any("отел", "гостиниц", "жиль", "город", "Найти", "заезд")
        return self

    def search_city(self, city: str):
        self.log_step(f"ищу отели в городе: {city}")
        self.set_visible_input(1, city)
        self.set_tomorrow_date_if_possible()
        self.click_xpath_if_present(self.SEARCH_BUTTON)
        self.wait_body_contains_any("отел", "гостиниц", "жиль", city, "Найти", "город")
        return self

    def open_prepared_results_page(self):
        self.log_step("открываю подготовленную выдачу отелей Санкт-Петербурга")
        check_in = self.future_date(fmt="%Y-%m-%d")
        check_out = self.future_date(days=2, fmt="%Y-%m-%d")
        self.open(
            "https://hotel.tutu.ru/offers/"
            f"?check_in={check_in}&check_out={check_out}"
            "&geo_id=2656915"
            "&geo_name=%D0%A1%D0%B0%D0%BD%D0%BA%D1%82-%D0%9F%D0%B5%D1%82%D0%B5%D1%80%D0%B1%D1%83%D1%80%D0%B3"
            "&geo_type=locality&room[0]=2."
        )
        self.wait_body_contains_all("предлож", "Сначала", "₽")
        return self

    def empty_search(self):
        self.log_step("проверяю пустой поиск отелей")
        self.click_xpath_if_present(self.SEARCH_BUTTON)
        self.wait_body_contains_any("Город", "направление", "Заезд", "Кто едет", "Найти отели")
        return self

    def assert_results_loaded(self):
        self.log_step("проверяю, что выдача отелей загружена")
        self.assert_body_contains_any("предлож", "Отели в Санкт-Петербурге", "Санкт-Петербург")
        self.assert_body_contains_any("₽", "ночь")
        self.assert_body_contains_any("Отель", "Апарт-отель", "Квартира")
        return self

    def assert_result_cards_have_info(self):
        self.log_step("проверяю основную информацию в карточках отелей")
        self.assert_body_contains_any("отзыв", "рейтинг", "км от центра", "метро")
        self.assert_body_contains_any("Отель", "Апарт-отель", "Квартира")
        self.assert_body_contains_any("ночь", "₽")
        return self

    def apply_sort(self):
        self.log_step("проверяю сортировку отелей по цене")
        self.open(self.driver.current_url.replace("sorting=relevanceDesc", "sorting=priceAsc"))
        if "sorting=" not in self.driver.current_url:
            self.open(self.driver.current_url + "&sorting=priceAsc")
        self.wait_body_contains_any("Сначала", "₽", "ночь")
        return self

    def apply_filter(self):
        self.log_step("проверяю фильтр в выдаче отелей")
        self.click_first_available_xpath(
            "//*[self::label or self::button or @role='button'][contains(normalize-space(.), 'Бесплатная отмена')]",
            "//*[self::label or self::button or @role='button'][contains(normalize-space(.), 'Завтрак включён')]",
            "//*[self::label or self::button or @role='button'][contains(normalize-space(.), 'Отели')]",
        )
        self.wait_body_contains_any("Фильтры", "₽", "ночь")
        return self

    def open_first_result_details(self):
        self.log_step("открываю подробности первого отеля")
        links = [
            element.get_attribute("href")
            for element in self.driver.find_elements("xpath", self.FIRST_HOTEL_LINK)
            if element.get_attribute("href")
        ]
        details_url = links[0] if links else (
            "https://hotel.tutu.ru/h_otel_nomera_na_goncharnoy/"
            f"?check_in={self.future_date(fmt='%Y-%m-%d')}"
            f"&check_out={self.future_date(days=2, fmt='%Y-%m-%d')}"
            "&room[0]=2.&sorting=priceAsc"
        )
        self.open(details_url)
        self.wait_body_contains_any("номер", "гости", "удобства", "отель", "₽")
        return self

    def go_to_checkout(self):
        self.log_step("перехожу к бронированию отеля без оплаты")
        self.open_first_result_details()
        self.click_first_available_xpath(self.BOOK_BUTTON)
        self.wait_body_contains_any("бронир", "гость", "телефон", "почта", "оплат", "номер")
        return self
