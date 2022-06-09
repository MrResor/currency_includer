import pymysql
import sqlalchemy
import customerrors as ce
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

class Run:
    """Class responsible for carrying out the script
    
        Atributes:

        -----
        Methods:
        argschk -- checking correctness of passed arguments
        setup   -- setups the currency table needed to 
        update  -- updates currencies
        export  -- exports data from database into .csv format
        help    -- 
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
        except sqlalchemy.exc.OperationalError as err:
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
        Base = automap_base()
        try:
            engine = create_engine("mysql+pymysql://root:root@localhost/wakamakafon")
        except pymysql.err.OperationalError as err:
            print(str(err))
        Base.prepare(engine, reflect=True)
        session = Session(engine)
        if not Base.classes.__contains__('product'):
            ## TODO should raise error that database is
            k = 1
        else:
            k = 3
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
