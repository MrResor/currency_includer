# Recruitment program for Hawatel company
Versions in other languages:
<a href = https://github.com/MrResor/Hawatel_rekrutacja/blob/main/README.pl.md>Polski </a></br>

## Usage overview
Program can be run from console with 'python main.py', with 4 different arguments:</br>
-h  displays help,</br>
-s  sets up database by adding "currency" table which is neccessary for the script correct operation,</br>
-u  updates values held in "currency" table,</br>
-e  exports data in .csv format,</br>

### -h "help"
Outputs some simple help string about the script.

### -s "setup"
Makes sure that the database has table "product" which is also vital for correct operation of the script. Then if table product exists checks if table currency exists and if it doesn't it creates one, and makes a get reqest to NBP API to get exchange rates for USD and EUR to fill them into the table. If it does it checks if the fields are ligning up with the ones we need, if yes it logs information that it already exists, otherwise it logs that the incorrect currency table exist.

### -u "update"
Updates the currency table with the values obtained from NBP API. If the  API does not have value from today, the second call is made to obtain the latest exchange rate. Such case is noted in logs. Next script attempts to update the data, but in case of error it will fail. No matter if it fails or succeds this is added to the logs.

### -e "export"
Exports data into .csv format, so it can be easily seen in excel. In case of any errors process fails, once again bot success and failure are added to log.