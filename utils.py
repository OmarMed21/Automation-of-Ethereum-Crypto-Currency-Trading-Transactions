import requests
import pandas as pd
from datetime import datetime
from matplotlib import pyplot
import pygsheets

## API token & wallet address from where we're scarping
API_KEY = "6X9E1S7BUTHWX7J7Q4UIDXQISAGVGPFEDP"
ADDRESS = "0x244Bb3910D13ab7c6a68cE36D05c156FF7e678af"

def transactions(LIMIT_TO_BE_SHOWN:int = None, 
                 page_number:str= "1",
                 eth_address:str = "0x244Bb3910D13ab7c6a68cE36D05c156FF7e678af",
                 api_key:str = "6X9E1S7BUTHWX7J7Q4UIDXQISAGVGPFEDP",
                 ) -> pd.DataFrame:
    """
    PARAMS:
    ------
        page_number: Transactions on each wallet are spread into many pages , you choose one of them
        eth_address: address of Wallet we want to target for transactions
        api_key: after adding a token on ethersacn website
        LIMIT_TO_BE_SHOWN: Number of Transactions you want to see

    RETURNS:
    -------
        Pandas Series of Transactions with Date and some other essential Infos about the Wallet
    """
    if LIMIT_TO_BE_SHOWN is None:
        ## Transactions on the Wallet
        TRANSACTIONS = f"https://api.etherscan.io/api?module=account&action=txlist&address={eth_address}&startblock=0&endblock=99999999&page={str(page_number)}&sort=asc&apikey={api_key}"

    else:TRANSACTIONS = f"https://api.etherscan.io/api?module=account&action=txlist&address={eth_address}&startblock=0&endblock=99999999&page={str(page_number)}&offset={LIMIT_TO_BE_SHOWN}&sort=asc&apikey={api_key}"

    ## perform EDA to get Data TRXs
    data_transactions = requests.get(TRANSACTIONS).json()
    df_transactions = pd.DataFrame(data_transactions['result'])
    df_transactions.timeStamp = df_transactions.timeStamp.astype('int32')
    for idx, timestamp in enumerate(df_transactions.timeStamp):
        df_transactions.timeStamp[idx] = datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y - %H:%M:%S")
    df_transactions.rename(columns={"timeStamp":"Date", "value":"ETH"}, inplace=True)
    df_transactions.ETH = df_transactions.ETH.astype('int64') / 1e18
    df_transactions['NOK'] = round(df_transactions['ETH']*get_crypto_price(), 3)

    ## Final results of TXNs with their Dates
    res = df_transactions[["Date", "ETH", "NOK", "txreceipt_status", "from", "to", "blockNumber"]] ## -> Pandas DataFrame
    return res ##.style.background_gradient(cmap=pyplot.get_cmap('Spectral')).format(precision=4)

def search_by_blockNumber(block_Num:int,
                          DATA) -> pd.DataFrame:
    """
    PARAMS:
    ------
        block_Num: block number of transaction
        DATA: data to search in

    RETURNS:
    -------
        Pandas Dataframe of the of all Infos has that block number
    """
    if str(block_Num) in list(DATA.blockNumber):
        return DATA[DATA.blockNumber == str(block_Num)]
    return "Block Number not Included"

def get_crypto_price(crypto_symbol:str ='ethereum'
                     ,vs_currency:str='nok') -> int:
    """
        Get real-time price of ETH vs NOK
    PARAMS:
    ------
        crypto_symbol: that's threshold currency that we compare with [in our case Ethereum]
        vs_currency: currency that we want to get it's value with first one

    RETURNS:
    -------
        price related to other currency
    """
    ## that's the official api og Coingecko url
    base_url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': crypto_symbol,
        'vs_currencies': vs_currency
    }

    ## scraping the data from API
    response = requests.get(base_url, params=params)

    ## checking of it's connected succesfully
    if response.status_code == 200:
        data = response.json()
        price = data[crypto_symbol][vs_currency]
        return price
    else:
        return None

def send_data_to_google_sheets(DATA:pd.DataFrame,
                               CLOUD_JSON_KEY:str = 'etherscan-crypto-trading-appv2-40b1a22b1007.json',
                               target_sheet_name:str='Etherscan Data',
                               target_worksheet_number:int = 1) -> None:
    """
    send data to Google Cloud and then to Google Sheets through Google Sheets API
    PARAMS:
    ------
        DATA: data to be sent
        CLOUD_JSON_KEY: path to credentials key of service account connected to API
        target_sheet_name: sheet where you want to send data to [NOTE: THAT SHEET MUST BE MANUALLY CREATED BEFORE EXECUTING THE FUNCTION]
        target_worksheet_number: sheet number where you want your data to be added on [NOTE: YOU NEED TO CREATE SHEET BEFORE EXECUTING THE FUNCTION]

    RETURNS:
    -------
        Data will be sent to desired Sheet 
    """
    client = pygsheets.authorize(service_account_file=CLOUD_JSON_KEY)
    sheet = client.open(target_sheet_name)
    worksheet = sheet[target_worksheet_number-1]
    worksheet.set_dataframe(DATA, (1,1))
