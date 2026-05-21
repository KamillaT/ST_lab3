from pages.base_page import BasePage


class MainPage(BasePage):
    RAILWAY_SECTION = (
        "(//*[self::a or self::button or @role='button' or self::div or self::span]"
        "[contains(normalize-space(.), 'Ж/д') or contains(normalize-space(.), 'поезд') "
        "or contains(normalize-space(.), 'Поезда')])[1]"
    )

    AVIA_SECTION = (
        "(//*[self::a or self::button or @role='button' or self::div or self::span]"
        "[contains(normalize-space(.), 'Авиабилеты') or contains(normalize-space(.), 'Авиа') "
        "or contains(normalize-space(.), 'авиа')])[1]"
    )

    HOTELS_SECTION = (
        "//*[contains(normalize-space(.), 'Отели') or contains(normalize-space(.), 'отели') "
        "or contains(normalize-space(.), 'Гостиниц') or contains(normalize-space(.), 'жиль') "
        "or contains(normalize-space(.), 'Жиль')]"
    )

    LOGIN_BUTTON = (
        "(//*[self::a or self::button or @role='button' or self::div or self::span]"
        "[contains(normalize-space(.), 'Войти') or contains(normalize-space(.), 'Личный кабинет')])[1]"
    )

    def open_main(self):
        self.open_relative("/")
        return self

    def go_to_railway(self):
        self.click_xpath(self.RAILWAY_SECTION)
        self.wait_body_contains_any("поезд", "Ж/д", "расписание", "Откуда")
        return self

    def go_to_avia(self):
        self.click_xpath(self.AVIA_SECTION)
        self.wait_body_contains_any("Авиа", "авиа", "Самол", "Откуда", "Куда", "билет")
        return self

    def assert_hotels_visible(self):
        self.visible_xpath(self.HOTELS_SECTION)
        return self

    def open_login_form(self):
        self.click_xpath_if_present(self.LOGIN_BUTTON)
        self.wait_body_contains_any("Телефон", "почт", "Войти", "Код", "Личный кабинет")
        return self
