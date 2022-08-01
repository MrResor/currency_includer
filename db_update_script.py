from db_connection import dbconn
from decorators import api_errors, missing_table_errors, table_creation_errors
from sqlalchemy import (Table, Column, DECIMAL, MetaData,
                        String, insert, update, select)
import logging
import requests
import argparse


class Run:
    """ Class responsible for carrying out the script\n

        Atributes:\n
        Base        -- Holds base api link used while retriving exchange
        rates.\n

        Methods:\n
        main        -- Responsible for calling funcion to handle modes chosen
        by parameters.\n
        setup       -- Setups the currency table needed for script's correct
        functioning.\n
        update      -- Updates currencies.\n
        obtain_data -- Obtains up to date currencies values from NBP API.\n
        export      -- Exports data from database into .csv format.\n
    """
    Base = 'https://api.nbp.pl/api/exchangerates/rates/a/'

    def __init__(self):
        # setting up argparse
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-h', '--help', help='Pokazuje te wiadomość i '
                            'kończy działanie.', action='help')
        parser.add_argument('-s', '--setup', help='Modyfikacja istniejącej '
                            'bazy danych spełniającej wymagania by była w '
                            'stanie przyjąć nowe waluty.', action='store_true')
        parser.add_argument('-u', '--update', help='Odświeżenie kursów walut '
                            'pobranych z API NBP.', action='store_true')
        parser.add_argument('-e', '--export', help='Eksportowanie danych do '
                            'pliku .csv.', action='store_true')
        args = parser.parse_args()
        # setting up logging module
        logging.basicConfig(filename='logfile.log', level=logging.INFO,
                            format='[%(asctime)s] -> {%(levelname)s} '
                            '%(message)s')
        self.main(args)

    @missing_table_errors
    def main(self, args: argparse.Namespace) -> None:
        """ Main part of the program activating the chosen utilities.\n
            Takes arguments parsed by argparse as parameter.
        """
        self.db = dbconn()
        if args.setup:
            self.setup()
        if args.update:
            self.update()
        if args.export:
            self.export()
        print('Program zakończony z kodem 0.')
        logging.error('Program zakończony z kodem 0.')
        quit(0)

    @table_creation_errors
    def setup(self) -> None:
        """ Creates and fills the table with initial values if the
            conditions are fulfilled.\n
            The main condition is existance of "product" table, and
            lack of already existing "currency" table.
        """
        if not self.db.base.classes.__contains__('product'):
            raise AttributeError('product')
        currency = Table(
            'currency', MetaData(),
            Column('code', String(3), primary_key=True),
            Column('name', String(255)),
            Column('val', DECIMAL(10, 2)),
        )
        currency.create(self.db.session.bind)
        self.db.refresh()
        self.db.session.execute(insert(self.db.base.classes.currency).
                                values(code='PLN', name='złoty',
                                val=1.0))
        self.db.session.commit()
        self.update()
        logging.info('Tabela "currency" stworzona i wypełniona.')

    def update(self) -> None:
        """ Method for updating currency rates using NBP API.
        """
        USDval, EURval = self.obtain_data(False)
        tab = self.db.base.classes.currency
        res = self.db.session.execute(select(tab).where(tab.code == 'EUR')).\
            one_or_none()
        if res is None:
            self.db.session.execute(insert(tab).values(code='EUR', name='euro',
                                                       val=EURval))
        else:
            self.db.session.execute(update(tab).where(tab.code == 'EUR').
                                    values(val=EURval))
        self.db.session.commit()
        res = self.db.session.execute(select(tab).where(tab.code == 'USD')).\
            one_or_none()
        if res is None:
            self.db.session.execute(insert(tab).values(code='USD',
                                    name='dolar amerykański', val=USDval))
        else:
            self.db.session.execute(update(tab).where(tab.code == 'USD').
                                    values(val=USDval))
        self.db.session.commit()
        logging.info('Kursy walut zaktualizowane.')
        print('Kursy walut zaktualizowane.')

    @api_errors
    def obtain_data(self, flag: bool) -> tuple[float, float]:
        """ Method for obtaining currency rates from NBP API.\n
            Takes bool as parameter to notify from which method was this one
            called and returns tuple of floats (rates for USD and EUR).
        """

        # TODO this probably needs to be optimised, tests with 404 api needed
        response = requests.get(self.Base + 'usd/today/?format=json')
        if (response.status_code == 404):
            response = requests.get(self.Base + 'usd/?format=json')
            if response.status_code == 404:
                raise ConnectionError
            print('usd -> Dzisiejsze dane niedostępne, używamy najświeższych '
                  'dostępnych danych.')
            logging.warning('usd -> Dzisiejsze dane niedostępne, używamy '
                            'najświeższych dostępnych danych.')
            usd_val = response.json()['rates'][0]['mid']
        else:
            usd_val = response.json()['rates'][0]['mid']
        response = requests.get(self.Base + 'eur/today/?format=json')
        if (response.status_code == 404):
            response = requests.get(self.Base + 'eur/?format=json')
            if response.status_code == 404:
                raise ConnectionError
            print('eur -> Dzisiejsze dane niedostępne, używamy najświeższych '
                  'dostępnych danych.')
            logging.warning('eur -> Dzisiejsze dane niedostępne, używamy '
                            'najświeższych dostępnych danych.')
            eur_val = response.json()['rates'][0]['mid']
        else:
            eur_val = response.json()['rates'][0]['mid']
        print('Dane z NBP otrzymane.')
        logging.info('Dane z NBP otrzymane.')
        return usd_val, eur_val

    def export(self):
        """ Export data from "product" table with added prices in USD and EUR
            into a .csv file, so it can be easily read in excel.
        """
        prod = self.db.base.classes.product
        cur_tab = self.db.base.classes.currency
        curr = dict(self.db.session.execute(select(cur_tab.code, cur_tab.val)).
                    all())
        results = self.db.session.execute(select(prod)).all()
        # TODO look into write to .csv possibilites in python, maybe there is
        # cleaner solution
        with open('export.csv', 'w') as file:
            file.write('"ProductID";"DepartmentID";"Category";"IDSKU";'
                       '"ProductName";"Quantity";"UnitPrice";"UnitPriceUSD";'
                       '"UnitPriceEuro";"Ranking";"ProductDesc";"UnitsInStock"'
                       ';"UnitsInOrder"\n')
            for result in results:
                r = result[0].__dict__
                file.write(f'"{r["ProductID"]}";"{r["DepartmentID"]}";'
                           f'"{r["Category"]}";"{r["IDSKU"]}";"'
                           f'"{r["ProductName"]}";{str(r["Quantity"])};'
                           f'{str(r["UnitPrice"])};'
                           f'{str(round(r["UnitPrice"]/curr["USD"],2))};'
                           f'{str(round(r["UnitPrice"]/curr["EUR"],2))}'
                           f'{str(r["Ranking"])};"{r["ProductDesc"]}";'
                           f'{str(r["UnitsInStock"])};{str(r["UnitsInOrder"])}'
                           '\n')
        print('Dane wyeksportowane.')
        logging.info('Dane wyeksportowane.')
