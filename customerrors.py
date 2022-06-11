class ArgErr (Exception):
    """Something is wrong with passed arguments
    
        Atributes:
        msg -- error message to be displayed
    """
    def __init__ (self, msg):
        self.__msg = msg
        super().__init__(self.__msg)

    def __str__(self):
        return self.__msg + ', proszę użyć "-s" aby zmodyfikować istniejącą bazę' \
            + ' danych która spełnia wymagania\n"-u" aby zdobyć aktualne kursy' \
            + ' walut i "-e" aby wyeksportować dane do pliku .csv.'