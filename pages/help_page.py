from pages.base_page import BasePage


class HelpPage(BasePage):
    REFUND_TOPIC = (
        "(//*[self::a or self::button or @role='button' or self::div or self::span]"
        "[contains(normalize-space(.), 'возврат') or contains(normalize-space(.), 'Возврат') "
        "or contains(normalize-space(.), 'вернуть') or contains(normalize-space(.), 'Вернуть') "
        "or contains(normalize-space(.), 'билет')])[1]"
    )

    def open_help(self):
        self.open_relative("/2read/")
        self.wait_body_contains_any("Справ", "Вопрос", "билет", "возврат")
        return self

    def open_refund_topic(self):
        self.click_xpath_if_present(self.REFUND_TOPIC)
        self.wait_body_contains_any("возврат", "вернуть", "билет", "заказ", "Справ")
        return self
