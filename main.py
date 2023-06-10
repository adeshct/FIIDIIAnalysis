import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
%matplotlib inline
plt.style.use('seaborn-darkgrid')

import warnings
warnings.simplefilter('ignore')

#------------------------------
# Fetching NIFTY futures data from bhavcopy files and storing it into a DataFrame
#------------------------------

dates = [str(x) if x>=10 else '0'+str(x) for x in range(1, 32)]
months = [str(x) if x>=10 else '0'+str(x) for x in range(1, 13)]
years = [2022]

data = pd.DataFrame(columns=['<ticker>', '<date>',  '<open>', '<high>', '<low>', '<close>', '<volume>', '<o/i>'])
df = pd.DataFrame()

for year in years:
   for month in months:
       for date in dates:
           filename = f'{year}-{month}-{date}-NSE-FO.txt'
           try:
               df = pd.read_csv(filename)
               data = data.append(df.iloc[3:6], ignore_index=True)
           except:
               pass
            
#------------------------------
# Keeping only the required columns and renaming them
#------------------------------

data=data[['<ticker>', '<date>', '<close>', '<volume>', '<o/i>']]
data.columns=['ticker', 'date', 'close', 'volume', 'oi']

#------------------------------
#converting date column elements into datetime object from integers and making the Date as the index
#------------------------------

Date=[]
a= data['date']

for i in range(len(a)):
   c=str(a[i])
   b= datetime(year=int(c[0:4]), month=int(c[4:6]), day=int(c[6:8]))
   Date.append(b)
  
data['Date']=Date   
data.set_index('Date',drop=True,inplace=True)
data.drop(['date'],axis=1,inplace=True)

data.head()

#------------------------------
#plotting close prices for NIFTY futures
#------------------------------

data['close'].groupby(data['ticker']).plot(figsize=(15,7))
plt.title(' Close prices for NSE NIFTY50 futures in the first quarter of 2020 \n (Note: red lines mark the expiry dates)'\
        ,fontsize ='xx-large')
plt.axvline(datetime(2020, 1, 30), color='r') # Jan expiry
plt.axvline(datetime(2020, 2, 27),color='r') # Feb expiry
plt.axvline(datetime(2020, 3, 26),color='r') # March expiry
plt.legend()
plt.show()

#------------------------------
# price vs volume analysis
#------------------------------

ax =data['volume'].groupby(data.index).sum().plot(figsize=(15,7), color='black')

plt.ylabel('Volume traded in number of contracts',fontsize='x-large')
plt.title(' Price vs volume \n (Note: red lines mark the expiry dates)',fontsize ='xx-large')

plt.axvline(datetime(2020, 1, 30), color='r') #expiry1
plt.axvline(datetime(2020, 2, 27),color='r')
plt.axvline(datetime(2020, 3, 26),color='r')

plt.axvline(datetime(2020, 3, 13),color='black', ls=':', ymax=0.95)

data[data['ticker']=='NIFTY-I']['close'].plot(ax=ax, secondary_y=True,color='b')
plt.ylabel('Close prices Nifty',fontsize='x-large')
plt.legend()
plt.show()

#------------------------------
#plotting open interest across all three series
#------------------------------

data['oi'].groupby(data.index).sum().plot(figsize=(15,7),color='g')
plt.title(' Open interest in NSE NIFTY50 futures in the first quarter of 2020 \n (Note: red lines mark the expiry dates)'\
        ,fontsize ='xx-large')
plt.ylabel('Open interest in crores of contracts',fontsize='x-large')
plt.axvline(datetime(2020, 1, 30), color='r') #expiry1
plt.axvline(datetime(2020, 2, 27),color='r')
plt.axvline(datetime(2020, 3, 26),color='r')
plt.legend()
plt.show()


#------------------------------
#plotting close prices and open interest together
#------------------------------

ax= data['oi'].groupby(data.index).sum().plot(figsize=(15,7), color='g')
plt.ylabel('Open interest to volume ratio',fontsize='x-large')
plt.title(' Close price vs Open interest \n (Note: red lines mark the expiry dates)',fontsize ='xx-large')
plt.legend()
plt.axvline(datetime(2020, 1, 30), color='r')
plt.axvline(datetime(2020, 2, 27),color='r')
plt.axvline(datetime(2020, 3, 26),color='r')

data[data['ticker']=='NIFTY-I']['close'].plot(ax=ax, secondary_y=True,color='b')
plt.ylabel('Close prices Nifty',fontsize='x-large')

plt.show()

#------------------------------
# Creating a function to generate rollover percent
#------------------------------

def rollover(DF, expiry_date):
   ''' This function takes the futures data, expiry date
       and returns an estimate of rollover percent '''
  
   df = data.loc[expiry_date]
  
   Near_month_oi = df[df['ticker']=='NIFTY-I']['oi'].mean()
   Next_month_oi = df[df['ticker']=='NIFTY-II']['oi'].mean()
   Far_month_oi = df[df['ticker']=='NIFTY-III']['oi'].mean()
  
   return round(100* (Next_month_oi + Far_month_oi) /  (Near_month_oi + Next_month_oi + Far_month_oi),2)

# Creating a new DataFrame with rollover % for expiry dates
expiry_dates =[datetime(2020, 1, 30).date(),datetime(2020, 2, 27).date(),datetime(2020, 3, 26).date()]

expiry_df = pd.DataFrame(index=expiry_dates , columns = ['rollover %','oi','Nifty'])

for i in range(len(expiry_dates)):
   expiry_df['rollover %'].iloc[i] = rollover(data, expiry_dates[i])
   expiry_df['oi'].iloc[i] = data[data['ticker']=='NIFTY-II']['oi'].loc[expiry_dates[i]]
   expiry_df['Nifty'].iloc[i] = data[data['ticker']=='NIFTY-I']['close'].loc[expiry_dates[i]]
  
expiry_df.index.name='Expiry_date'
expiry_df

#------------------------------
#plotting price with rollover% on the same plot
#------------------------------

data[data['ticker']=='NIFTY-I'].close.plot(figsize=(15,7),color='b')
plt.title(' Close price vs rollover % in Q1 of 2020 \n (Note: Horizontal green line marks the three month average rollover%\n \
Vertical red lines mark the expiry dates)', fontsize='xx-large' )
plt.axvline(datetime(2020, 1, 30), color='r')
plt.axvline(datetime(2020, 2, 27),color='r')
plt.axvline(datetime(2020, 3, 26),color='r')
plt.ylabel('Close price of Nifty-I',fontsize='x-large')
plt.legend(loc='lower left')

axes2 = plt.twinx()
axes2.bar(expiry_df.index, expiry_df['rollover %'], color='indigo', label='rollover %', width= 2)
plt.ylabel('Rollover in %',fontsize='x-large')
plt.axhline(70, color='green')
plt.legend(loc='best')
plt.show()

#------------------------------
# Fetching FII/DII data
#------------------------------

fii_dii = pd.read_excel('FII DII.xlsx')

#------------------------------
# plotting and visualising FII/DII data
#------------------------------
ax = fii_dii[['net FII buy/sell', 'net DII buy/sell']].plot(figsize=(15,7),color=['red','blue'],marker='d', markersize=12)
plt.ylabel('FII/DII net Investment in crores',fontsize='x-large')
plt.xlabel('Month',fontsize='x-large')
fii_dii['NIFTY'].plot(ax=ax, secondary_y='NIFTY',color='black',linestyle='dashed', marker='o',\
                     markerfacecolor='black', markersize=12)
plt.ylabel('NIFTY',fontsize='x-large')
plt.xlabel('Month',fontsize='x-large')
plt.title('FII/DII net investment vs Nifty', fontsize='xx-large')
plt.legend()
plt.show()
