import numpy as np      #module for working with data manipulation
import pandas as pd     #module for working with tabulated data
import requests         #module for http requests
import math
from scipy import stats #module for percentile calculations
import xlsxwriter       #module for transferring data to excel spreadsheet
from bs4 import BeautifulSoup
from env_secrets import user, pwd, host, port, dbName, tableName, investopediaEmail, investopediaPassword
from sqlalchemy import create_engine
from datetime import date
import json

#NOTE: make sure to pip install all of the required modules.

url = 'https://www.quiverquant.com/congresstrading/' #through a http request, load the page

page = requests.get(url) #the page is an object instance. The requests library enforces synchrocity, so you don't need async. (This also means requests are blocking)
#print(type(page))

soup = BeautifulSoup(page.text, 'html.parser')
#print(soup)

table = soup.find('table', class_ = 'table-congress table-politician')
#print(type(table)) #table is a soup object
#print(table)

titles = soup.find_all('th')[0:6] #finding headers for table, 6th is the arrow so manually do it

new_th = soup.new_tag("th")
new_th.string = "returns"
titles.append(new_th)

table_titles = [title.text for title in titles]
print(table_titles)

df = pd.DataFrame(columns = table_titles) #creating dataframe
#print(df)

print(len(df))
print("lol!")
column_data = table.find_all('tr') #returns a list of tr tags

for row in column_data[1:]: #need to go from 1 cause there is an empty list at the front, cannot make dataframe that way
    row_data = row.find_all('td') #putting each data cell of a row into a list
    individual_row_data = [' '.join(data.text.split()) for data in row_data] #taking the text for each data cell - removes all trailing whitespaces - removes all spaces more than 1
    individual_row_data[0] = individual_row_data[0].replace('- ', '').lstrip() #remove '- ', then any leading whitespaces after that
    #print(individual_row_data)

    length = len(df)
    df.loc[length] = individual_row_data #you can actually just assign to length for a dataframe apparently. Maybe cause its already set to 0?

df.to_csv(r'C:\Users\wnqmw\OneDrive\Documents\PythonProjects\NancyVsQuantitativeMomentum\Scrapped data\Trades.csv', index = False)
#print(df)

#-- getting a database of potentially new positions filed today
DEMODATE = 'Mar. 15, 2024'
today = date.today()
dateToday = today.strftime("%b %d, %Y")
dateToday = dateToday[0:3] + "." + dateToday[3:]
#print(dateToday, type(dateToday))
dfToday = df.loc[df['Filed'] == DEMODATE]

#print("--------start")   DEBUGGING PURPOSES
#print(dfToday)

#--starting connection to db
db_connection_str = f'mysql+mysqldb://{user}:{pwd}@{host}:{port}/{dbName}'
db_connection = create_engine(db_connection_str, echo = True, future = True) #need to pip install mysqlclient

dfExistingToday = pd.read_sql(f'SELECT * FROM {tableName}', con=db_connection) #getting existing entries in db
dfExistingToday = dfExistingToday.loc[dfExistingToday['Filed'] == DEMODATE]
dfExistingToday = dfExistingToday.drop(columns=['index'])
#print(dfExistingToday)
#print("--------end") DEBUGGING PURPOSES

failed = False
print(dfExistingToday.equals(dfToday), "xddddddddddd") #if they are not equal, that means a new entry has been added.

DEMODATA = ['AAPL', 'Sale (Full) $100,000-$250,000', 'Rick Scott', 'Mar. 15, 2024', 'Feb. 15, 2024', 'blah', '-']
dfNew = pd.DataFrame(columns = table_titles)  #DEMODATA, 
#print(dfNew)

#print(dfToday.sort_values(by=dfToday.columns.tolist()).reset_index(drop=True).equals(dfExistingToday.sort_values(by=dfExistingToday.columns.tolist()).reset_index(drop=True)), "final fiaweijtowaeitjajo")

print(dfToday)
print(dfExistingToday)
cnt = 0
#for some reason, quiver does not always maintain the same order, so you need to sort and then compare
#may need later: dfToday.sort_values(by=dfToday.columns.tolist()).reset_index(drop=True).equals(dfExistingToday.sort_values(by=dfExistingToday.columns.tolist()).reset_index(drop=True))
# while(not dfToday.equals(dfExistingToday)): #if not equal, keep removing the top row of dfToday and check
#     cnt+= 1
    
#     row1 = dfToday.iloc[-1]
#     length = len(dfNew)
#     dfNew.loc[length] = row1 #appends 1 row from dfToday to dfNew
#     dfToday = dfToday[:-1] #gives a df without the last row

#     if cnt == 1:
#         print(dfToday)
#         print(dfExistingToday)
#     #print(dfToday)
    
#     if(dfToday.empty):
#         raise Exception("There was a new entry, but something went wrong.") #if the entire dataframe is exhausted, raise error
dfToday = dfToday.sort_values(by=dfToday.columns.tolist())
dfExistingToday = dfExistingToday.sort_values(by=dfExistingToday.columns.tolist()).reset_index(drop=True)

merged = dfToday.merge(dfExistingToday, on=list(dfToday.columns), how='outer', indicator=True)
rows_only_in_dfToday = merged[merged['_merge'] == 'left_only'][dfToday.columns]

dfNew = rows_only_in_dfToday
dfNew.loc[len(dfNew.index)] = DEMODATA
print(dfNew, "xddafadfdafasddddddddddddddddddddd")

newStockTickers = []
newStockPrices = []
dfNew = dfNew.reset_index()  # make sure indexes pair with number of rows
for index, row in dfNew.iterrows(): #iterrows() is a generator that yields both index and row
    print(row["Stock"].split(' ', 1)[0] , "- PRINTING NEW STOCKS FOUND")
    newStockTickers.append(row["Stock"].split(' ', 1)[0])

#------------------ EXECUTING TRADES ON NEW STOCKS

# for ticker in newStockTickers:
#     print(marketwatch.get_price('AAPL'))

#------------------creating sql database ***SHOULD BE RESERVED FOR THE VERY END

#df.to_sql(name=tableName, con=db_connection, if_exists='replace')     #THIS CODE REPLACES ENTIRE DB WITH THE CONGRESS DATA.
#uploading dataframe to table - For manual operation of the database, use sql commands on mysql