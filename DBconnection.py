from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

class dbconn:

    def __init__(self):
        self.engine = create_engine("mysql+pymysql://root:root@localhost/mydb")
        self.base = automap_base()
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine)
    
    def refresh(self):
        self.base = automap_base()
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine)
