import customerrors as ce
from DBconnection import dbconn
from sqlalchemy.exc import OperationalError, ProgrammingError
from requests.exceptions import ConnectionError
import logging

class Run:
    """Class responsible for carrying out the script
    
        Methods:
        main        -- 
        argschk     -- checking correctness of passed arguments
        setup       -- setups the currency table needed to 
        update      -- updates currencies
        obtain_data -- obtains up to date currencies values from NBP API
        export      -- exports data from database into .csv format
        help        -- help string to inform user of script usage
    """
    def __init__ (self, cmdargs):
        self.s = False
        logging.basicConfig(filename = "logfile.log", level=logging.INFO,\
            format='[%(asctime)s] -> {%(levelname)s} %(message)s')
        try:
            self.argschk(cmdargs)
        except ce.ArgErr as err:
            print(str(err))
            return
        self.main(cmdargs)
    
    def main(self, cmdargs):
        try:
            if cmdargs[1] == "-s":
                self.setup()
            elif cmdargs[1] == "-u":
                self.update()
            elif cmdargs[1] == "-e":
                self.export()
            else:
                self.help()
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
    
    def argschk(self, cmdargs):
        if len(cmdargs) != 2:
            if len(cmdargs) < 2:
                msg = 'Brakuje argumentu'
            else:
                msg = 'Za dużo argumentów'
            logging.error(msg)
            raise ce.ArgErr(msg)
        elif cmdargs[1] not in ["-e", "-u", "-s", "-h", "-help"]:
            msg = 'Nieznany argument'
            logging.error(msg)
            raise ce.ArgErr(msg)

    def setup(self):
        self.s = True
        db = dbconn()
        logging.info("Połączono z bazą danych.")
        if not db.base.classes.__contains__('product'):
            raise AttributeError('product')
        else:
            if not db.base.classes.__contains__('currency'):
                from sqlalchemy import Table, Column, DECIMAL, MetaData, String, insert
                currency = Table(
                    'currency', MetaData(), 
                    Column('code', String(3), primary_key = True),
                    Column('name', String(255)), 
                    Column('val', DECIMAL(10,2)),
                )
                USDval, EURval = self.obtain_data()
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
        USDval, EURval = self.obtain_data()
        from sqlalchemy import update, select, insert
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

    def obtain_data(self):
        import requests
        response = requests.get('https://api.nbp.pl/api/exchangerates/rates/a/usd/today/?format=json')
        if (response.content == b'404 NotFound - Not Found - Brak danych'):
            print("usd -> Dzisiejsze dane niedostępne, używamy najświerzszych dostępnych danych.")
            logging.warning("usd -> Dzisiejsze dane niedostępne, używamy najświerzszych dostępnych danych.")
            response = requests.get('https://api.nbp.pl/api/exchangerates/rates/a/usd/?format=json')
            USDval = response.json()['rates'][0]['mid']
        else:
            USDval = response.json()['rates'][0]['mid']
        response = requests.get('https://api.nbp.pl/api/exchangerates/rates/a/eur/today/?format=json')
        if (response.content == b'404 NotFound - Not Found - Brak danych'):
            print("eur -> Dzisiejsze dane niedostępne, używamy najświerzszych dostępnych danych.")
            logging.warning("eur -> Dzisiejsze dane niedostępne, używamy najświerzszych dostępnych danych.")
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
        from sqlalchemy import select
        currencies = db.session.execute(select(cur.code,cur.val)).all()
        for curr in currencies:
            if curr[0] == 'EUR':
                EURval = curr[1]
            elif curr[0] == 'USD':
                USDval = curr[1]
        results = db.session.execute(select(prod)).all()
        with open('export.csv', 'w') as file:
            file.write('"ProductID","DepartmentID","Category","IDSKU","ProductName",' \
                + '"Quantity","UnitPrice","UnitPriceUSD","UnitPriceEuro","Ranking",' \
                + '"ProductDesc","UnitsInStock","UnitsInOrder"\n')
            for result in results:
                r = result[0].__dict__
                file.write('"'+r['ProductID']+'","'+r['DepartmentID']+'","'+r['Category']+'","'\
                    +r['IDSKU']+'","'+r['ProductName']+'",'+str(r['Quantity'])+','+str(r['UnitPrice'])+','\
                    +str(round(r['UnitPrice']/USDval,2))+','+str(round(r['UnitPrice']/EURval,2)) \
                    +','+str(r['Ranking'])+',"'+r['ProductDesc']+'",'+str(r['UnitsInStock']) \
                    +','+str(r['UnitsInOrder'])+'\n')
        print("Dane wyeksportowane.")
        logging.info("Dane wyeksportowane.")
    
    def help(self):
        print('main.py opcje[-s, -u, -e]\njedna z opcji jest wymagana do działania skryptu\n' \
            + '-s\t->\tmodyfikacja istniejącej bazy danych spełniającej wymagania by była ' \
            + 'w stanie przyjąć nowe waluty.\n-u\t->\todświerzenie kursów walut pobranych ' \
            + 'z API NPB.\n-e\t->\teksportowanie danych do pliku .csv.')
