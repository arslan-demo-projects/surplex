
##The scraper scripts have been developed using python 3 
##Scrape auctions from [Surplex Website](https://www.surplex.com/es/a.html) and store the scraped auction results into a MYSQL database.
```
*** Step-1 ***

Script has developed using python3 or latest version. You can 
download and install IDE Pycharm Community Edition  (used for 
managing python projects and scripts).
```
### Download Pycharm from [Jetbrains](https://www.jetbrains.com/pycharm/download/) Official Website

###You can also get help from [Here](https://www.geeksforgeeks.org/creating-python-virtual-environment-windows-linux/?ref=lbp) to know how to create virtual environment at linux or windows


```
*** Step-2 ***

Install latest pip version.

Now the below-mentioned modules need to install using terminal or 
command line interface using pip:-
```
`pip install scrapy==2.5.1`

`pip install pillow==9.3.0`

`pip install requests==2.22.0`

`pip install mysql-connector-python==8.0.19`

`pip install pyOpenSSL==22.0.0`

`pip install cryptography==38.0.4`

##OR 
You can install all requirements using requirements.txt.
Please write this command in terminal:
````
pip install -r requirements.txt
````

```
*** Step-3 ***

Note: Now Set your project interpreter in which you have installed the
above modules / dependencies.
```
```
*** Step-4 ***

You will need to input your Mysql database credentials inside script
named as "db_credentials.py". Currently, database credentials set as:

database_credentials = {
    "host": "localhost",
    "user": "root",
    "passwd": "toor",
    "database": "auctions_database"
}

Database Table names set as:

table_name_auction = "table_auction_surplex"

You can update / replace your database credentials.
```

```
*** Step-5 ***

Open the command prompt and navigate into the project folder like:
cd surplex
cd surplex
cd spiders

for run script at command prompt please write command :-
python run_script.py


Note: Before run script Please make sure you are in project directory:
 "~/surplex/surplex/spiders/"
 
If you have questions regarding script, please inbox me I will be happy
to help you!
```

````
*** Step-6 ***

When script will finish execution, all auctions data stored into
MYSQL database and script will generate a CSV file as well.
````

```
*** Step-7 ***

For any query please send me message.
```
####best regards,
###alifarslan
