import pandas as pd
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import numpy as np



#first request to get the options contracts

url='https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-sistema-pregao-enUS.asp'


page=requests.get(url)
soup=BeautifulSoup(page.text)

descriptions=[]
contract_options=[]
for i in soup.find_all('option'):
    description=str(i)[str(i).find('>')+1:str(i).find('</option>')].strip()
    descriptions.append(description)
    contract_options.append(description[:description.find(':')].strip())

#Contract_options são todas as opções de contratos para extrair do site
#Descriptions são as descrições desses contratos


#Referencias para manipulação do HTML

key_string_center = '</tr><td class="text-center">'
sep_string_center = '<td class="text-center">'
sep_string_right = '<td class="text-right">'
headers_sep_string = '<th class="text-center">'
str_sep = '</td>'
merc_identifier = 'MercFut3 = MercFut3 + '
item_sep = ';'

#Headers

pege_contract=requests.get(url,params={'Data':'12/12/2022','Mercadoria':'DOL'})
page_contract_text=pege_contract.text

headers_raw_1=pd.Series(page_contract_text.split(merc_identifier)[0].split(item_sep))
headers_raw_2=pd.Series(page_contract_text.split(merc_identifier)[2].split(item_sep))
def clean_headers(row_value:str):
    
    lkeyh=len(headers_sep_string)
    str_sep = '</th>'


    if row_value.find(headers_sep_string)>-1:
        
        start_str_value=row_value.find(headers_sep_string)+lkeyh
        end_str_value=row_value.find(str_sep)
        value=row_value[start_str_value:end_str_value]
        
        return value
    else: return np.nan


headers_raw_1=headers_raw_1.apply(clean_headers).dropna()
headers_raw_2=headers_raw_2.apply(clean_headers).dropna()

headers=list(headers_raw_1.append(headers_raw_2))
headers.remove('Contract Months')
headers.remove('Data')
headers.insert(0,'Contract Months')
headers
def clean_row(row_value:str):
    
    lkeyc=len(sep_string_center)
    lkeyr=len(sep_string_right)

    if row_value.find(sep_string_center)>-1:
        
        start_str_value=row_value.find(sep_string_center)+lkeyc
        end_str_value=row_value.find(str_sep)
        value=row_value[start_str_value:end_str_value]
        
        return value

    elif row_value.find(sep_string_right)>-1:
        
        start_str_value=row_value.find(sep_string_right)+lkeyr
        end_str_value=row_value.find(str_sep)
        value=row_value[start_str_value:end_str_value]

        return value
    else: return np.nan
def get_fut_contract(page_single_contract,date,contract):

    raw_row=page_single_contract.split(merc_identifier)[3:-1]
    table=[]

    for i in raw_row:
        
        vector_row=i.split(item_sep)
        vector_row=pd.Series(vector_row)
        row=vector_row.apply(clean_row).dropna()
        row=list(row)
        

        table.append(row)
    table=pd.DataFrame(table,columns=headers)

    #this date has to be iterated
    table['Date']=date
    table['Contract']=contract
    
    return table
Main function
def scraper(start_date: datetime,end_date : datetime,contracts):

    df=pd.DataFrame()
    date_list = pd.date_range(start=start_date, end=end_date)

    url='https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-sistema-pregao-enUS.asp'

    for contract in contracts:
        for curent_date in date_list:

            pege_contract=requests.get(url,params={'Data':f'{curent_date.month}/{curent_date.day}/{curent_date.year}','Mercadoria':f'{contract}'})
            contract_table=get_fut_contract(pege_contract.text,curent_date,contract)

            df=pd.concat([df,contract_table])

    return df
    
start_date=datetime(2022,12,13)
end_date=datetime(2022,12,16)
contracts=['AUD','ARS']

scraper(start_date,end_date,contracts)


#page of a single contract in a single date
pege_contract=requests.get(url2,params={'Data':f'{month}/{day}/{year}','Mercadoria':f'{contract}'})
soup_contract=BeautifulSoup(pege_contract.text)


