import customerrors as ce

class Run:
    """Class responsible for carrying out the script
    
        Atributes:
        ---
        Methods:
        argschk -- checking correctness of passed arguments
    """
    def __init__ (self, cmdargs):
        try:
            self.argschk(cmdargs)
        except ce.ArgErr as err:
            print(str(err))
            return
        for i in cmdargs:
            print(i)
    
    def argschk(self, cmdargs):
        if len(cmdargs) != 2:
            if len(cmdargs) < 2:
                msg = 'Argument missing, please provide "-s" to modify exisitng database to fullfil requirements\n' \
                    + '"-u" to collect current currency rates and "-e" to export data to .csv file.'
            else:
                msg = 'Too many arguments provided, please provide only one.'
            raise ce.ArgErr(msg)
        elif cmdargs[1] not in ["-e", "-u", "-s"]:
            msg = ""
            raise ce.ArgErr(msg)
