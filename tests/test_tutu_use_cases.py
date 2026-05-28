import os
import uuid

import pytest

from pages.avia_page import AviaPage
from pages.auth_page import AuthPage
from pages.bus_page import BusPage
from pages.help_page import HelpPage
from pages.hotel_page import HotelPage
from pages.main_page import MainPage
from pages.railway_page import RailwayPage
from pages.suburban_page import SuburbanPage
from pages.tours_page import ToursPage


FALLBACK_EXISTING_EMAIL = "armangokka@gmail.com"


def existing_auth_email() -> str:
    return os.getenv("TUTU_EMAIL") or os.getenv("TUTU_LOGIN") or FALLBACK_EXISTING_EMAIL


def env_auth_email() -> str | None:
    return os.getenv("TUTU_EMAIL") or os.getenv("TUTU_LOGIN")


def unique_missing_email() -> str:
    suffix = uuid.uuid4().hex[:8]
    return f"tutu-lab-1230-{suffix}@example.ru"


def interactive_auth_enabled() -> bool:
    return os.getenv("TUTU_INTERACTIVE_AUTH") == "1" or bool(os.getenv("TUTU_EMAIL_CODE"))


def read_email_code_from_terminal(email: str) -> str:
    if os.getenv("TUTU_EMAIL_CODE"):
        return os.environ["TUTU_EMAIL_CODE"].strip()

    prompt = f"\nВведите 4-значный код из письма для {email}: "
    try:
        return input(prompt).strip()
    except (EOFError, OSError):
        try:
            with open("/dev/tty", "r", encoding="utf-8") as tty_in, open(
                "/dev/tty", "w", encoding="utf-8"
            ) as tty_out:
                tty_out.write(prompt)
                tty_out.flush()
                return tty_in.readline().strip()
        except OSError:
            pytest.skip("Для ввода кода запустите тест из терминала: pytest -s -k email_code")


def test_tc01_go_to_railway_tickets(driver):
    MainPage(driver).open_main().go_to_railway()


def test_tc02_successful_railway_search(driver):
    RailwayPage(driver).open_railway_page().search_route("Москва", "Санкт-Петербург")


def test_tc03_empty_railway_search_validation(driver):
    RailwayPage(driver).open_railway_page().empty_search()


def test_tc03_railway_origin_only_validation(driver):
    RailwayPage(driver).open_railway_page().origin_only_validation("Москва")


def test_tc03_railway_destination_only_validation(driver):
    RailwayPage(driver).open_railway_page().destination_only_validation("Санкт-Петербург")


def test_tc03_railway_invalid_origin_validation(driver):
    RailwayPage(driver).open_railway_page().invalid_origin_validation("ЫЫЫЫЫЫ", "Санкт-Петербург")


def test_tc04_bus_search(driver):
    BusPage(driver).open_bus_page().search_route("Москва", "Санкт-Петербург")


def test_tc05_bus_ticket_refund(driver):
    BusPage(driver).open_bus_page().open_refund()


def test_tc06_go_to_avia_tickets(driver):
    MainPage(driver).open_main().go_to_avia()


def test_tc07_avia_search(driver):
    AviaPage(driver).open_avia_page().search_route("Москва", "Санкт-Петербург").assert_form_has_round_trip_and_passengers()


def test_tc07_avia_empty_search_validation(driver):
    AviaPage(driver).open_avia_page().empty_search_validation()


def test_tc07_avia_origin_only_validation(driver):
    AviaPage(driver).open_avia_page().origin_only_validation("Москва")


def test_tc07_avia_destination_only_validation(driver):
    AviaPage(driver).open_avia_page().destination_only_validation("Санкт-Петербург")


def test_tc07_avia_route_without_dates_validation(driver):
    AviaPage(driver).open_avia_page().route_without_dates_validation("Москва", "Санкт-Петербург")


def test_tc08_suburban_train_search(driver):
    SuburbanPage(driver).open_suburban_page().search_route("Москва", "Химки")


def test_tc09_hotel_search(driver):
    HotelPage(driver).open_hotels_from_main().search_city("Казань")


def test_tc10_results_filter(driver):
    RailwayPage(driver).open_prepared_results_page().apply_filter()


def test_tc11_open_result_card(driver):
    RailwayPage(driver).open_prepared_results_page().open_first_result_card()


def test_tc12_authorization_form(driver):
    MainPage(driver).open_main().open_login_form()


def test_tc13_help_refund_topic(driver):
    HelpPage(driver).open_help().open_refund_topic()


def test_tc14_login_invalid_email(driver):
    AuthPage(driver).invalid_email_validation("not-an-email")


def test_tc15_login_nonexistent_user(driver):
    AuthPage(driver).nonexistent_user_validation(unique_missing_email())


def test_tc16_login_wrong_password(driver):
    AuthPage(driver).login_with_password(existing_auth_email(), "wrong-password-1230").assert_login_failed()


def test_tc17_login_short_password(driver):
    AuthPage(driver).short_password_validation(existing_auth_email(), "123")


def test_tc18_registration_invalid_email(driver):
    AuthPage(driver).registration_invalid_email_validation("bad-registration-email")


def test_tc19_choose_railway_ticket(driver):
    RailwayPage(driver).choose_first_ticket()


def test_tc24_avia_results_filter_details_and_checkout(driver):
    (
        AviaPage(driver)
        .open_avia_page()
        .search_route("Москва", "Санкт-Петербург")
        .assert_results_loaded()
        .assert_result_cards_have_info()
        .apply_filter()
        .open_first_result_details()
        .go_to_checkout()
        .fill_checkout_to_payment()
    )


def test_tc25_railway_results_sort_filter_details_and_checkout(driver):
    (
        RailwayPage(driver)
        .open_prepared_results_page()
        .assert_results_loaded()
        .assert_result_cards_have_info()
        .apply_sort()
        .apply_filter()
        .open_first_result_card()
        .go_to_checkout()
    )


def test_tc26_bus_empty_search_validation(driver):
    BusPage(driver).open_bus_page().empty_search()


def test_tc27_bus_results_sort_filter_details_and_checkout(driver):
    (
        BusPage(driver)
        .open_prepared_results_page()
        .assert_results_loaded()
        .assert_result_cards_have_info()
        .apply_sort()
        .apply_filter()
        .open_first_result_details()
        .go_to_checkout()
    )


def test_tc28_suburban_empty_search_validation(driver):
    SuburbanPage(driver).open_suburban_page().empty_search()


def test_tc29_suburban_results_sort_filter_and_details(driver):
    (
        SuburbanPage(driver)
        .open_prepared_results_page()
        .assert_results_loaded()
        .assert_result_cards_have_info()
        .apply_sort()
        .apply_filter()
        .open_first_result_details()
        .assert_ticket_app_handoff()
    )


def test_tc30_hotel_empty_search_validation(driver):
    HotelPage(driver).open_hotels_from_main().empty_search()


def test_tc31_hotel_results_sort_filter_details_and_checkout(driver):
    (
        HotelPage(driver)
        .open_prepared_results_page()
        .assert_results_loaded()
        .assert_result_cards_have_info()
        .apply_sort()
        .apply_filter()
        .go_to_checkout()
    )


def test_tc32_tours_empty_search_validation(driver):
    ToursPage(driver).open_tours_page().empty_search()


def test_tc33_tours_results_sort_filter_details_and_checkout(driver):
    (
        ToursPage(driver)
        .open_prepared_results_page()
        .assert_results_loaded()
        .assert_result_cards_have_info()
        .apply_sort()
        .apply_filter()
        .open_first_result_details()
        .go_to_checkout()
    )


def test_tc20_login_wrong_email_code(driver):
    AuthPage(driver).invalid_email_code_validation(existing_auth_email(), "0000")


def test_tc21_password_reset_request(driver):
    AuthPage(driver).request_password_reset(existing_auth_email())


@pytest.mark.skipif(
    not env_auth_email() or not interactive_auth_enabled(),
    reason="Set TUTU_EMAIL/TUTU_LOGIN and TUTU_INTERACTIVE_AUTH=1 to enter the email code in terminal",
)
def test_tc22_successful_authorization_by_email_code(driver):
    email = env_auth_email()
    auth_page = AuthPage(driver).request_email_code(email)
    if auth_page.is_any_visible(auth_page.RATE_LIMIT_MESSAGE) and not auth_page.is_any_visible(auth_page.CODE_FIELD):
        pytest.skip("Tutu ограничил отправку кодов, повторите интерактивный тест позже")
    code = read_email_code_from_terminal(email)
    auth_page.enter_code(code).wait_until_auth_completed_or_code_error().assert_logged_in()


@pytest.mark.skipif(
    not os.getenv("TUTU_LOGIN") or not os.getenv("TUTU_PASSWORD"),
    reason="Set TUTU_LOGIN and TUTU_PASSWORD to run a positive authorization test",
)
def test_tc23_successful_authorization_by_password(driver):
    AuthPage(driver).login_with_password(
        os.environ["TUTU_LOGIN"],
        os.environ["TUTU_PASSWORD"],
        restore_cache=True,
    ).assert_logged_in()
