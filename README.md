# Simple program updating currency rates in MySQL database
Versions in other languages:
<a href = https://github.com/MrResor/currency_includer/blob/main/README.pl.md>Polski </a>

## Short description
Script capable of connecting into existing database, altering it by adding "currency" table, fill it with present currency exchange rates and export data into .csv file. Every step of program operation is logged. Currency rates are obtained from NPB API, and if currency table was created correctly beforehand these updates can be created whenever, since specific switch was prepared for them. 

## Usage overview
Program can be run from console with 'python main.py', and can take  4 different arguments:

### -h, --help
Outputs simple help string about the script.

### -s, --setup
Makes sure that the database has table "product" which is vital for correct operation of the script. Then if it exists, script attempts to create a "currency" table. In case this table already is present in the database a check is performed to see if it is correct one. When it is, user is informed that table is already created. Otherwise, an error message appears. After successfull creation of the table a get request to NBP API is made to get exchange rates for USD and EUR to fill them into the table. if no "product" table is found, user is notified.

### -u, --update
Updates the "currency" table with the values obtained from NBP API. If the  API does not have value from today, the second call is made to obtain the latest exchange rate. Such case is noted in logs. Then script attempts to update the data, but in case of error it will fail. Both successful and failed attempts are logged correspondingly.

### -e, --export
Exports data into .csv format, so it can be easily seen in excel. In case of any errors process fails, once again both success and failure are added to the loggfile.

## Exit codes
&nbsp;&nbsp;&nbsp;0 - Program executed correctly.  
&nbsp;&nbsp;&nbsp;2 - Database connection error (wrong password, wrong database, database unresponsive).  
&nbsp;&nbsp;&nbsp;3 - API connection error.  
&nbsp;&nbsp;&nbsp;4 - Database tables incorrect (table "product" missing, table "currency" missing, table "currency" present but incorrect.)  
In case of any above errors, refer to loggfile created in script directory.
## Notes
Updated database schema can be found <a href = "https://github.com/MrResor/currency_includer/blob/main/dbschema.txt">here</a>. This is the same schema as provided with additon of the table that the script will create with "-s" option. Worth noting however is the fact that the database provided does not store prices correctly, since everything after decimal point is truncated (decimal(10,0) should be decimal(10,2)). Additionally, from the data provided to populate the database, filling sellers was impossible, since table requires third colum to be 'B' and all data provided has 'S'.