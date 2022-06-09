import customerrors as ce
from DBconnection import dbconn
from sqlalchemy.exc import OperationalError

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
            print("Given database does not exist or is unreachable.")
    
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
        db = dbconn()
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
                    Column('val', DECIMAL),
                )
                currency.create(db.session.bind)
                db.refresh()
                db.session.execute(insert(dict(db.base.classes)['currency']).values(code = 'PLN', name = 'złoty', val = 1.0))
                db.session.commit()
                self.update() # to fill table with some initial values
            else:
                db.session.commit()
                print("Currency table already exists.")
        return

    def update(self):
        return
    
    def export(self):
        return
    
    def help(self):
        print("main.py opcje[-s, -u, -e]\njedna z opcji jest wymagana do działania skryptu\n \
-s\t->\tmodyfikacja istniejącej bazy danych spełniającej wymagania by była w stanie przyjąć nowe waluty.\n \
-u\t->\todświerzenie kursów walut pobranych z API NPB.\n \
-e\t->\teksportowanie danych do pliku .csv.")
