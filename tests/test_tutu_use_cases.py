from pages.avia_page import AviaPage
from pages.bus_page import BusPage
from pages.help_page import HelpPage
from pages.hotel_page import HotelPage
from pages.main_page import MainPage
from pages.railway_page import RailwayPage
from pages.suburban_page import SuburbanPage


def test_tc01_go_to_railway_tickets(driver):
    MainPage(driver).open_main().go_to_railway()


def test_tc02_successful_railway_search(driver):
    RailwayPage(driver).open_railway_page().search_route("Москва", "Санкт-Петербург")


def test_tc03_empty_railway_search_validation(driver):
    RailwayPage(driver).open_railway_page().empty_search()


def test_tc04_bus_search(driver):
    BusPage(driver).open_bus_page().search_route("Москва", "Санкт-Петербург")


def test_tc05_bus_ticket_refund(driver):
    BusPage(driver).open_bus_page().open_refund()


def test_tc06_go_to_avia_tickets(driver):
    MainPage(driver).open_main().go_to_avia()


def test_tc07_avia_search(driver):
    AviaPage(driver).open_avia_page().search_route("Москва", "Санкт-Петербург")


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
