from __init__ import logging
from sqlalchemy.exc import OperationalError


def db_errors(func):
    def note(error: str) -> None:
        print(error)
        logging.error(error)

    def wrapper_catch_errors(instance):
        try:
            func(instance)
        except OperationalError as err:
            call = {"1049": "Baza danych nie istnieje",
                    "1045": "Niepoprawne dane logowania do bazy.",
                    "2003": "Baza danych jest niedostępna"}
            note(call[err.args[0].split("(")[2].split(",")[0]])
            note("Program zakończony z kodem 2.")
            quit(2)
    return wrapper_catch_errors
