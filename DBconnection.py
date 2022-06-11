from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

class dbconn:
    """Class responsible for database connection

        Atributes:
        engine  -- engine responsible for code to database communication 
        base    -- variable holding the schema of automapped database
        session -- variable responsible for passing querries

        Methods:
        refresh -- refreshes automaping of the database
    """
    def __init__(self):
        self.engine = create_engine("mysql+pymysql://root:root@localhost/mydb")
        self.base = automap_base()
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine)
    
    def refresh(self):
        self.base = automap_base()
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine)
