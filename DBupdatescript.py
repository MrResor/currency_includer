import customerrors as ce
from DBconnection import dbconn
from sqlalchemy.exc import OperationalError
from requests.exceptions import ConnectionError
import logging

class Run:
    """Class responsible for carrying out the script
    
        Atributes:

        -----
        Methods:
        argschk -- checking correctness of passed arguments
        setup   -- setups the currency table needed to 
        update  -- updates currencies
        export  -- exports data from database into .csv format
        help    -- help string to inform user of script usage
    """
    def __init__ (self, cmdargs):
        logging.basicConfig(filename = "logfile.log", level=logging.INFO,\
            format='[%(asctime)s] -> {%(levelname)s} %(message)s')
        try:
            self.argschk(cmdargs)
        except ce.ArgErr as err:
            print(str(err))
            return
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
            print("Baza danych jest niedostępna lub nie istnieje.")
            logging.error("Baza danych jest niedostępna lub nie istnieje.")
        except ConnectionError as err:
            print("Próba połączenia nie powiodła się, ponieważ połączona strona \
nie odpowiedziała poprawnie po ustalonym okresie czasu \nlub utworzone połączenie \
nie powiodło się, ponieważ połączony host nie odpowiedział.")
            logging.error("Błąd połączenia z API banku.")
            if (self.s):
                print('Nie udało się utworzyć tablicy "Currency".')
                logging.error('Nie udało się utworzyć tablicy "Currency".')
    
    def argschk(self, cmdargs):
        if len(cmdargs) != 2:
            if len(cmdargs) < 2:
                msg = 'Brakuje argumentu'
            else:
                msg = 'Za dużo argumentów'
            raise ce.ArgErr(msg)
        elif cmdargs[1] not in ["-e", "-u", "-s", "-h", "-help"]:
            msg = 'Nieznany argument'
            raise ce.ArgErr(msg)

    def setup(self):
        self.s = True
        db = dbconn()
        logging.info("Połączono z bazą danych.")
        if not db.base.classes.__contains__('product'):
            ## TODO should raise error that database does not contain the table we need
            k = 1
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
                db.session.execute(insert(dict(db.base.classes)['currency']).values(code = 'PLN', name = 'złoty', val = 1.0))
                db.session.execute(insert(dict(db.base.classes)['currency']).values(code = 'USD', name = 'dolar amerykański', val = USDval))
                db.session.execute(insert(dict(db.base.classes)['currency']).values(code = 'EUR', name = 'euro', val = EURval))
                db.session.commit()
            else: 
                print('Tabela "Currency" już istnieje.')
        return

    def update(self, db = None):
        if db == None:
            db = dbconn()
        if not db.base.classes.__contains__('currency'):
            ## TODO error database not setup correctly
            return 0
        else:
            from sqlalchemy import select
            results = db.session.execute(select(db.base.classes.currency)).all()
            for result in results:
                print(result[0].__dict__)
        return
    
    def obtain_data(self):
        import requests
        response = requests.get('https://api.nbp.pl/api/exchangerates/rates/a/usd/today/?format=json')
        if (response.content == b'404 NotFound - Not Found - Brak danych'):
            print("usd - > Today's data unavailable, accessing latest available data.")
            response = requests.get('https://api.nbp.pl/api/exchangerates/rates/a/usd/?format=json')
            USDval = response.json()['rates'][0]['mid']
        else:
            USDval = response.json()['rates'][0]['mid']
        response = requests.get('https://api.nbp.pl/api/exchangerates/rates/a/eur/today/?format=json')
        if (response.content == b'404 NotFound - Not Found - Brak danych'):
            print("eur - > Today's data unavailable, accessing latest available data.")
            response = requests.get('https://api.nbp.pl/api/exchangerates/rates/a/eur/?format=json')
            EURval = response.json()['rates'][0]['mid']
        else:
            EURval = response.json()['rates'][0]['mid']
        return USDval, EURval

    def export(self):
        return
    
    def help(self):
        import requests
        response = requests.get('https://api.nbp.pl/api/exchangerates/rates/a/eur/today/?format=json')
        if (response.content == b'404 NotFound - Not Found - Brak danych'):
            print("Today's data unavailable, accessing latest data.")
            response = requests.get('https://api.nbp.pl/api/exchangerates/rates/a/eur/?format=json')
            print(response.json()['rates'][0]['mid'])
#         print("main.py opcje[-s, -u, -e]\njedna z opcji jest wymagana do działania skryptu\n \
# -s\t->\tmodyfikacja istniejącej bazy danych spełniającej wymagania by była w stanie przyjąć nowe waluty.\n \
# -u\t->\todświerzenie kursów walut pobranych z API NPB.\n \
# -e\t->\teksportowanie danych do pliku .csv.")
