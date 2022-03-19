import yahoo_fin.stock_info as yf
import pandas as pd

'''
Two ways to create a screener:
1. Create a filter while gathering the data.
2. Collect data & filter based on multiple criteria afterwards.
'''

#Get tickers
tickers = yf.tickers_sp500() #manual input is an option

#
capitalization = 0
cash = 0
investments = 0
debt = 0
ev = 0
net_inc = 0

#Output in a dataframe
summary = pd.DataFrame(columns = ['Ticker', 'Market cap','Net income',
                                  'Cash', 'Debt', 'Investments', 'Enterprise value'])

def market_cap(ticker):
    global capitalization
    shares_row = 0
    stats = yf.get_stats(ticker)
    price = float(yf.get_live_price(ticker))

    #Discover the row
    for i in range(len(stats['Attribute'])):
        if stats['Attribute'][i] == 'Shares Outstanding 5':
            break
        else:
            shares_row += 1
    
    shares = stats['Value'][shares_row]
    #Adjust for the letter
    if shares[-1].lower() == 'm':
        shares = float(shares[:-1])
    elif shares[-1].lower() == 'b':
        shares = float(shares[:-1])*1000

    #Calculate market cap in millions         
    capitalization = shares * price

def bs(ticker):
    global capitalization
    global cash
    global investments
    global debt
    global ev
    stats = yf.get_stats(ticker)
    balance_sheet = yf.get_balance_sheet(ticker, yearly=False)
    years = balance_sheet.columns
    investments = 0    
    count_debt = 0
    count_cash = 0
    
    #Find the row for debt
    for i in range(len(stats['Attribute'])):
        if stats['Attribute'][i] == 'Total Debt (mrq)':
            break
        else:
            count_debt += 1

    debt = stats['Value'][count_debt]

    #Adjust for the letter
    if debt[-1].lower() == 'm':
        debt = float(debt[:-1])
    elif debt[-1].lower() == 'b':
        debt = float(debt[:-1])*1000   
    
    #Find the row for cash
    for i in range(len(stats['Attribute'])):
        if stats['Attribute'][i] == 'Total Cash (mrq)':
            break
        else:
            count_cash += 1
            
    cash = stats['Value'][count_cash]
    
    #Adjust for the letter
    if cash[-1].lower() == 'm':
        cash = float(cash[:-1])
    elif cash[-1].lower() == 'b':
        cash = float(cash[:-1])*1000

    #Investments
    try:
        investments = balance_sheet[years[0]]['longTermInvestments']/1000000
    except:
        investments = 0

    ev = capitalization - cash - investments + debt
    
def income_statement(ticker):
    global net_inc
    net_inc = 0
    quarterly_is = yf.get_income_statement(ticker, yearly = False)
    years = quarterly_is.columns
    for i in range(4):
        net_inc += quarterly_is[years[i]]['netIncomeFromContinuingOps']        
    
def cfs(ticker):
    pass

def collect_data():
    global summary
    for ticker in tickers[0:5]:
        try:
            market_cap(ticker)
            bs(ticker)
            income_statement(ticker)
            cfs(ticker)
            new_row = {'Ticker': ticker,
                       'Market cap': capitalization,                       
                       'Cash': cash,
                       'Debt': debt,
                       'Investments': investments,
                       'Enterprise value': ev,
                       'Net income': net_inc,}

            summary = summary.append(new_row, ignore_index = True)
            print(ticker + ' added.')
        except:
            print(ticker + ': Something went wrong.')
    summary.to_csv('summary.csv')
                
collect_data()
