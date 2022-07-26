from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine


class dbconn:
    """ Class responsible for database connection

        Atributes:\n
        CONN_STR    -- variable holding connection adress for database\n
        engine      -- engine responsible for code to database communication\n
        base        -- variable holding the schema of automapped database\n
        session     -- variable responsible for passing querries\n

        Methods:\n
        refresh -- refreshes automaping of the database
    """
    CONN_STR = "mysql+pymysql://root:root@localhost/mydb"

    def __init__(self):
        self.engine = create_engine(self.CONN_STR)
        self.base = automap_base()
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine)

    def refresh(self) -> None:
        """ Resposnible for refreshing the map of the database, after the
            currency table is created, to ensure access in the same
            program run
        """
        self.base = automap_base()
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine)
