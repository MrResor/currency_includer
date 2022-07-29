from decorators import db_errors
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine


class dbconn:
    """ Class responsible for database connection.\n

        Atributes:\n
        CONN_STR    -- Variable holding connection adress for database.\n
        engine      -- Engine responsible for code to database communication.\n
        base        -- Variable holding the schema of automapped database.\n
        session     -- Variable responsible for passing querries.\n

        Methods:\n
        refresh     -- Refreshes automaping of the database.
    """
    CONN_STR = 'mysql+pymysql://root:root@localhost/mydb'

    def __init__(self):
        self.session = None
        self.setup()

    @db_errors
    def setup(self) -> None:
        """ Initializes database connection and elements neccessary for
            database operation.
        """
        self.engine = create_engine(self.CONN_STR)
        self.base = automap_base()
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine)

    def refresh(self) -> None:
        """ Responsible for refreshing the map of the database, after the
            currency table is created, to ensure access in the same
            program run.
        """
        self.base = automap_base()
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine)

    def __del__(self):
        if self.session:
            self.session.close()
        self.engine.dispose()
