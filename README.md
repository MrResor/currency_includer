# Recruitment program for Hawatel company
Versions in other languages:
<a href = https://github.com/MrResor/Hawatel_rekrutacja/blob/main/README.pl.md>Polski </a></br>

## Usage overview
Program can be run from console with 'python main.py', with 4 different arguments:</br>

### -h "help"
Outputs simple help string about the script.

### -s "setup"
Makes sure that the database has table "product" which is also vital for correct operation of the script. Then if table product exists checks if table currency exists and if it doesn't it creates one, and makes a get request to NBP API to get exchange rates for USD and EUR to fill them into the table. If it does it checks if the fields are ligning up with the ones we need, if yes it logs information that it already exists, otherwise it logs that the incorrect currency table exist.

### -u "update"
Updates the currency table with the values obtained from NBP API. If the  API does not have value from today, the second call is made to obtain the latest exchange rate. Such case is noted in logs. Next script attempts to update the data, but in case of error it will fail. Both successful and failed attempts are logged correspondingly.

### -e "export"
Exports data into .csv format, so it can be easily seen in excel. In case of any errors process fails, once again both success and failure are added to the loggile.