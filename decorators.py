from __init__ import logging
from sqlalchemy.exc import OperationalError
from requests.exceptions import ConnectionError


def db_errors(func):
    """ Decorator responsible for handling database errors, such as not
        existing database, incorrect credentials or database not accessible.
    """
    def note(error: str) -> None:
        print(error)
        logging.error(error)

    def wrapper_catch_db_errors(instance):
        try:
            func(instance)
        except OperationalError as err:
            call = {'1049': 'Baza danych nie istnieje',
                    '1045': 'Niepoprawne dane logowania do bazy.',
                    '2003': 'Baza danych jest niedostępna'}
            note(call[err.args[0].split('(')[2].split(',')[0]])
            note('Program zakończony z kodem 2.')
            quit(2)
    return wrapper_catch_db_errors


def api_errors(func):
    """ Decorator responsible for handling API errors, such as inaccessible
        API endpoint.
    """
    def wrapper_catch_api_errors(instance, flag):
        try:
            return func(instance, flag)
        except ConnectionError:
            print('Błąd połączenia z API banku.')
            logging.error('Błąd połączenia z API banku.')
            if flag:
                print('Nie udało się utworzyć tablicy "Currency".')
                logging.error('Nie udało się utworzyć tablicy "Currency".')
            print('Program zakończony z kodem 3.')
            logging.error('Program zakończony z kodem 3.')
            quit(3)
    return wrapper_catch_api_errors


def missing_table_errors(func):
    """ Decorator responsible for handling table errors in database, such as
        nonexisting tables.
    """
    def wrapper_catch_missing_table_errors(instance, args):
        try:
            func(instance, args)
        except AttributeError as err:
            print(err)
            print(f'Baza źle skonfigurowana, brakuje tablicy "{str(err)}".')
            logging.error(f'Baza źle skonfigurowana, brakuje tablicy '
                          f'"{str(err)}".')
            print('Program zakończony z kodem 4.')
            logging.error('Program zakończony z kodem 4.')
            quit(4)
    return wrapper_catch_missing_table_errors


def table_creation_errors(func):
    """ Decorator catching error when attempting to create currency table.\n
        If said table already exists it check if it is the same we need.
    """
    def wrapper_catch_table_creation_errors(instance):
        try:
            func(instance)
        except OperationalError as err:
            err = instance.db.base.classes.currency.__table__.columns.keys()
            err.sort()
            if err == ['code', 'name', 'val']:
                print('Tabela "currency" już istnieje.')
                logging.warning('Tabela "currency" już istnieje.')
            else:
                print('Tabela "currency" już istnieje, ale jest '
                      'niepoprawna.')
                logging.error('Tabela "currency" już istnieje, ale jest '
                              'niepoprawna.')
                print('Program zakończony z kodem 4.')
                logging.error('Program zakończony z kodem 4.')
                quit(4)
    return wrapper_catch_table_creation_errors
