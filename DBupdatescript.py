from DBconnection import dbconn
from sqlalchemy.exc import OperationalError, ProgrammingError
from requests.exceptions import ConnectionError
from sqlalchemy import Table, Column, DECIMAL, MetaData, String, insert, update, select
import logging
import requests
import argparse

class Run:
    """Class responsible for carrying out the script
    
        Methods:
        main        -- responsible for calling funcion to handle mode chosen by parameter and most error handling
        argschk     -- checking correctness of passed arguments
        setup       -- setups the currency table needed to 
        update      -- updates currencies
        obtain_data -- obtains up to date currencies values from NBP API
        export      -- exports data from database into .csv format
        help        -- help string to inform user of script usage
    """
    def __init__ (self, cmdargs):
        self.s = False
        parser = argparse.ArgumentParser()
        parser.add_argument('-s', '--setup',help = """modyfikacja istniejącej bazy danych 
            spełniającej wymagania by była w stanie przyjąć nowe waluty.""",
            action = "store_true")
        parser.add_argument('-u', '--update', help="""odświerzenie kursów walut pobranych z API NPB.""",
            action = "store_true")
        parser.add_argument('-e', '--export', help="""eksportowanie danych do pliku .csv.""",
            action = "store_true")
        args = parser.parse_args()
        logging.basicConfig(filename = "logfile.log", level=logging.INFO,\
            format='[%(asctime)s] -> {%(levelname)s} %(message)s')
        self.main(args)
    
    def main(self, args):
        try:
            if args.setup:
                self.setup()
            if args.update:
                self.update()
            if args.export:
                self.export()
        except OperationalError as err:
            if "Access denied" in str(err):
                print("Niepoprawne dane logowania do bazy.")
                logging.error("Niepoprawne dane logowania do bazy.")
            if "Unknown database" in str(err):
                print("Baza danych nie istnieje")
                logging.error("Baza danych nie istnieje")
            if "Can't connect" in str(err):
                print("Baza danych jest niedostępna")
                logging.error("Baza danych jest niedostępna")
        except ConnectionError as err:
            print('Błąd połączenia z API banku.')
            logging.error("Błąd połączenia z API banku.")
            if (self.s):
                print('Nie udało się utworzyć tablicy "Currency".')
                logging.error('Nie udało się utworzyć tablicy "Currency".')
        except AttributeError as err:
            print('Baza źle skonfigurowana, brakuje tablicy "' + str(err) + '".')
            logging.error('Baza źle skonfigurowana, brakuje tablicy "' + str(err) + '".')

    def setup(self):
        self.s = True
        db = dbconn()
        logging.info("Połączono z bazą danych.")
        if not db.base.classes.__contains__('product'):
            raise AttributeError('product')
        else:
            if not db.base.classes.__contains__('currency'):
                currency = Table(
                    'currency', MetaData(), 
                    Column('code', String(3), primary_key = True),
                    Column('name', String(255)), 
                    Column('val', DECIMAL(10,2)),
                )
                USDval, EURval = self.obtainData()
                currency.create(db.session.bind)
                db.refresh()
                db.session.execute(insert(db.base.classes.currency).values(code = 'PLN', name = 'złoty', val = 1.0))
                db.session.execute(insert(db.base.classes.currency).values(code = 'USD', name = 'dolar amerykański', val = USDval))
                db.session.execute(insert(db.base.classes.currency).values(code = 'EUR', name = 'euro', val = EURval))
                db.session.commit()
                logging.info('Tabela "Currency" stworzona i wypełniona.')
            else:
                res = db.base.classes.currency.__table__.columns.keys()
                res.sort()
                if res == ['code', 'name', 'val']:
                    print('Tabela "Currency" już istnieje.')
                    logging.warning('Tabela "Currency" już istnieje.')
                else:
                    print('Tabela "Currency" już istnieje, ale jest niepoprawna.')
                    logging.error('Tabela "Currency" już istnieje, ale jest niepoprawna.')
        return

    def update(self):
        db = dbconn()
        USDval, EURval = self.obtainData()
        tab = db.base.classes.currency
        res = db.session.execute(select(tab).where(tab.code == 'EUR')).one_or_none()
        if res == None:
            db.session.execute(insert(tab).values(code = 'EUR', name = 'euro', val = EURval))
        else:
            db.session.execute(update(tab).where(tab.code == 'EUR').values(val = EURval))
        db.session.commit()
        res = db.session.execute(select(tab).where(tab.code == 'USD')).one_or_none()
        if res == None:
            db.session.execute(insert(tab).values(code = 'USD', name = 'dolar amerykański', val = USDval))
        else:
            db.session.execute(update(tab).where(tab.code == 'USD').values(val = USDval))
        db.session.commit()
        logging.info("Kursy walut zaktualizowane.")
        print("Kursy walut zaktualizowane.")

    def obtainData(self):
        response = requests.get('https://api.nbp.pl/api/exchangerates/rates/a/usd/today/?format=json')
        print(response.status_code)
        if (response.content == b'404 NotFound - Not Found - Brak danych'):
            print("usd -> Dzisiejsze dane niedostępne, używamy najświeższych dostępnych danych.")
            logging.warning("usd -> Dzisiejsze dane niedostępne, używamy najświeższych dostępnych danych.")
            response = requests.get('https://api.nbp.pl/api/exchangerates/rates/a/usd/?format=json')
            USDval = response.json()['rates'][0]['mid']
        else:
            USDval = response.json()['rates'][0]['mid']
        response = requests.get('https://api.nbp.pl/api/exchangerates/rates/a/eur/today/?format=json')
        if (response.content == b'404 NotFound - Not Found - Brak danych'):
            print("eur -> Dzisiejsze dane niedostępne, używamy najśwież szych dostępnych danych.")
            logging.warning("eur -> Dzisiejsze dane niedostępne, używamy najświeższych dostępnych danych.")
            response = requests.get('https://api.nbp.pl/api/exchangerates/rates/a/eur/?format=json')
            EURval = response.json()['rates'][0]['mid']
        else:
            EURval = response.json()['rates'][0]['mid']
        print("Dane z NBP otrzymane.")
        logging.info("Dane z NBP otrzymane.")
        return USDval, EURval

    def export(self):
        db = dbconn()
        prod = db.base.classes.product
        cur = db.base.classes.currency
        curr = dict(db.session.execute(select(cur.code,cur.val)).all())
        results = db.session.execute(select(prod)).all()
        with open('export.csv', 'w') as file:
            file.write(f'"ProductID";"DepartmentID";"Category";"IDSKU";"ProductName";' \
                + f'"Quantity";"UnitPrice";"UnitPriceUSD";"UnitPriceEuro";"Ranking";' \
                + f'"ProductDesc";"UnitsInStock";"UnitsInOrder"\n')
            for result in results:
                r = result[0].__dict__
                print(r)
                file.write(f'"{r["ProductID"]}";"{r["DepartmentID"]}";"{r["Category"]}";"'\
                    + f'{r["IDSKU"]}";"{r["ProductName"]}";{str(r["Quantity"])};{str(r["UnitPrice"])};'\
                    + f'{str(round(r["UnitPrice"]/curr["USD"],2))};{str(round(r["UnitPrice"]/curr["EUR"],2))}'\
                    + f'{str(r["Ranking"])};"{r["ProductDesc"]}";{str(r["UnitsInStock"])}'\
                    + f';{str(r["UnitsInOrder"])}\n')
        print("Dane wyeksportowane.")
        logging.info("Dane wyeksportowane.")
