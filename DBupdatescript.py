from DBconnection import dbconn
from requests.exceptions import ConnectionError
from sqlalchemy import (Table, Column, DECIMAL, MetaData,
                        String, insert, update, select)
import logging
import requests
import argparse


class Run:
    """Class responsible for carrying out the script\n

        Atributes:\n
        BASE        -- holds base api link used while retriving exchange
        rates.\n

        Methods:\n
        main        -- responsible for calling funcion to handle mode chosen
        by parameter and most error handling\n
        setup       -- setups the currency table needed to\n
        update      -- updates currencies\n
        obtainData  -- obtains up to date currencies values from NBP API\n
        export      -- exports data from database into .csv format\n
    """
    BASE = 'https://api.nbp.pl/api/exchangerates/rates/a/'

    def __init__(self):
        self.s = False
        # setting up argparse
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-h', '--help', help="""Pokazuje te wiadomość i
                            kończy działanie.""", action="help")
        parser.add_argument('-s', '--setup', help="""modyfikacja istniejącej bazy danych
                            spełniającej wymagania by była w stanie przyjąć
                             nowe waluty.""", action="store_true")
        parser.add_argument('-u', '--update', help="""odświerzenie kursów walut
                             pobranych z API NBP.""", action="store_true")
        parser.add_argument('-e', '--export', help="""eksportowanie danych do pliku
                             .csv.""", action="store_true")
        args = parser.parse_args()
        # setting up logging module
        logging.basicConfig(filename="logfile.log", level=logging.INFO,
                            format='[%(asctime)s] -> {%(levelname)s}'
                            + ' %(message)s')
        self.main(args)

    def main(self, args):
        """ Main part of the program activating the chosen utilities.
        """
        self.db = dbconn()
        try:
            if args.setup:
                self.setup()
            if args.update:
                self.update()
            if args.export:
                self.export()
        except ConnectionError:
            print('Błąd połączenia z API banku.')
            logging.error("Błąd połączenia z API banku.")
            if (self.s):
                print('Nie udało się utworzyć tablicy "Currency".')
                logging.error('Nie udało się utworzyć tablicy "Currency".')
        except AttributeError as err:
            print(f'Baza źle skonfigurowana, brakuje tablicy "{str(err)}".')
            logging.error(f'Baza źle skonfigurowana, brakuje tablicy\
                "{str(err)}".')

    def setup(self):
        """ Creates and fills the table with initial values if the
            conditions are fulfilled
        """
        self.s = True
        db = dbconn()
        logging.info("Połączono z bazą danych.")
        if not db.base.classes.__contains__('product'):
            raise AttributeError('product')
        else:
            if not db.base.classes.__contains__('currency'):
                currency = Table(
                    'currency', MetaData(),
                    Column('code', String(3), primary_key=True),
                    Column('name', String(255)),
                    Column('val', DECIMAL(10, 2)),
                )
                USDval, EURval = self.obtainData()
                currency.create(db.session.bind)
                db.refresh()
                db.session.execute(insert(db.base.classes.currency).values(
                    code='PLN', name='złoty', val=1.0))
                db.session.execute(insert(db.base.classes.currency).values(
                    code='USD', name='dolar amerykański', val=USDval))
                db.session.execute(insert(db.base.classes.currency).values(
                    code='EUR', name='euro', val=EURval))
                db.session.commit()
                logging.info('Tabela "Currency" stworzona i wypełniona.')
            else:
                res = db.base.classes.currency.__table__.columns.keys()
                res.sort()
                if res == ['code', 'name', 'val']:
                    print('Tabela "Currency" już istnieje.')
                    logging.warning('Tabela "Currency" już istnieje.')
                else:
                    print('Tabela "Currency" już istnieje, ale jest '
                          'niepoprawna.')
                    logging.error('Tabela "Currency" już istnieje, ale jest '
                                  'niepoprawna.')
        return

    def update(self):
        USDval, EURval = self.obtainData()
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
        logging.info("Kursy walut zaktualizowane.")
        print("Kursy walut zaktualizowane.")

    def obtainData(self):
        response = requests.get(self.BASE + 'usd/today/?format=json')
        if (response.status_code == 404):
            response = requests.get(self.BASE + 'usd/?format=json')
            if response.status_code == 404:
                raise ConnectionError
            print('usd -> Dzisiejsze dane niedostępne, używamy najświeższych '
                  'dostępnych danych.')
            logging.warning('usd -> Dzisiejsze dane niedostępne, używamy '
                            'najświeższych dostępnych danych.')
            USDval = response.json()['rates'][0]['mid']
        else:
            USDval = response.json()['rates'][0]['mid']
        response = requests.get(self.BASE + 'eur/today/?format=json')
        if (response.status_code == 404):
            response = requests.get(self.BASE + 'eur/?format=json')
            if response.status_code == 404:
                raise ConnectionError
            print('eur -> Dzisiejsze dane niedostępne, używamy najświeższych '
                  'dostępnych danych.')
            logging.warning('eur -> Dzisiejsze dane niedostępne, używamy '
                            'najświeższych dostępnych danych.')
            EURval = response.json()['rates'][0]['mid']
        else:
            EURval = response.json()['rates'][0]['mid']
        print("Dane z NBP otrzymane.")
        logging.info("Dane z NBP otrzymane.")
        return USDval, EURval

    def export(self):
        prod = self.db.base.classes.product
        cur = self.db.base.classes.currency
        curr = dict(self.db.session.execute(select(cur.code, cur.val)).all())
        results = self.db.session.execute(select(prod)).all()
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
        print("Dane wyeksportowane.")
        logging.info("Dane wyeksportowane.")
