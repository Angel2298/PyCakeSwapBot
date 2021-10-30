# ROBOT PANCAKESWAP

# Import all the libraries to use
import threading

import requests
from web3 import Web3
from os import system
import os
from time import sleep
import winsound
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bsp
from decimal import Decimal
import time
from threading import Thread
from Buy import buyToken
from Sell import sellToken
import json

with open('config_json.json', 'r') as config_file:
    json_config_data = json.load(config_file)
    print(json_config_data)

# Clear the screen when using the PowerShell or Command Promp
def clear():
    _ = os.system('cls')

# Verify or ask for the contract of the token to work with
if json_config_data["TOKEN_CONTRACT"] == "":
    token = input("Enter here the contract of the token to verify\n"
                  "Enter here: ")
else:
    token = json_config_data["TOKEN_CONTRACT"]

# URL to the Binance Smart Chain Network connection
bsc_network = "https://bsc-dataseed.binance.org/"

# Connection to the HTTPS Ethereum node of BSC
w3 = Web3(Web3.HTTPProvider(bsc_network))

# Verify that the connection to the network is correct.
if w3.isConnected():
    print("Connection Established")

show_transaction = True

# Check if the contract is a valid to  contract on the Blockchain
TOKEN_Contract = w3.toChecksumAddress(token)
print(f"\nAddress of the token correct: {TOKEN_Contract}")

# Check if the contract of WBNB is valid
WBNB_Contract = w3.toChecksumAddress(json_config_data["WBNB_CONTRACT"])
print(f"\nAddress of WBNB correct: {WBNB_Contract}")

# Check if the PancakeRouter v2 contract is valid
PANCAKEROUTER_Contract = w3.toChecksumAddress(json_config_data["PANCAKEROUTER_CONTRACT"])
print(f"\nAddress of PancakeRouter correct: {PANCAKEROUTER_Contract}")

# Address of the personal wallet of METAMASK or TRUSTWALLET
My_Wallet_Address = json_config_data["PUBLIC_ADDRESS"]

# Options to load the page of the webdriver
options = Options()

# Option to not print the page
# options.headless = True

# Verify the connection to selenium
# Remove the logs from the console
os.environ['WDM_LOG_LEVEL'] = '0'
# Remove the blank space from the console
os.environ['WDM_PRINT_FIRST_LINE'] = 'False'

# Get the Driver directly from the webdriver-manager module
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)

# driver.delete_all_cookies()

# Function to show the Transaction Information on Bsc (STILL TO WORK, OPEN THE PAGE BUT IT SUDDENLY CLOSES IT)
def informationTx(url):
    transaction_url = webdriver.Chrome(executable_path=ChromeDriverManager().install())
    return transaction_url.get(url)

###################################################### ABI #############################################################

# Function to get the ABI of the given contract
def getABI(contract, driver):
    try:
        # name = f"{contract}.txt"
        with open(f"contracts/ABI_Contract_{contract}.txt", mode="r") as file:
            abi = file.readlines()[0]
            print("File found in the first time")
    except FileNotFoundError:
        print("Not found in the first place")
        # Get the page to interact with the smart contract of the token
        driver.get(f"https://bscscan.com/address/{contract}#code")

        # Get the source code of the token page, page_source method require the object, not variable
        page_code = driver.page_source

        # Parse the source code into html language
        code_parse = bsp(markup=page_code, features="lxml")

        # Find the element ABI contract
        ABI_contract = code_parse.find_all(name="pre", attrs={"class": "wordwrap js-copytextarea2"})
        # Get just the contract without the html code
        abi = ABI_contract[0].get_text()

        # Create a file for the new contract
        with open(f"contracts/ABI_Contract_{contract}.txt", mode="w") as file:
            file.write(abi)
    return abi

########################################################################################################################



############################# Get the balance of the WBNB of your wallet ###############################################

def getUpdateInformation():
    # FIrst get the ABI of the WBNB contract
    wbnb_abi = getABI(WBNB_Contract, driver)

    # Declaring the token contract
    wbnb_eth_contract = w3.eth.contract(address=WBNB_Contract, abi=wbnb_abi)

    # Return the balance in the wallet of the token but without decimals
    wbnb_balance = wbnb_eth_contract.functions.balanceOf(My_Wallet_Address).call()

    # Convert the number of wei to the actual value of 'ether'
    wbnb_balance = w3.fromWei(wbnb_balance, 'ether')

    # Symbol of the WBNB
    wbnb_symbol = wbnb_eth_contract.functions.symbol().call()

    print(f"\nBalance: {wbnb_balance} {wbnb_symbol}")

    # Create a contract on the ethereum network for the token to trade
    token_eth_contract = w3.eth.contract(address=TOKEN_Contract, abi=getABI(TOKEN_Contract, driver))

    # Return the balance in the wallet of the token but without decimals
    token_balance = token_eth_contract.functions.balanceOf(My_Wallet_Address).call()

    # Convert the number of wei to the actual value of 'ether'
    token_balance = w3.fromWei(token_balance, 'ether')

    # Get the symbol of the current token
    token_symbol = token_eth_contract.functions.symbol().call()

    print(f"The amount of {token_symbol} is: {token_balance}")
    print(type(token_balance))

    # Create a contract on the ethereum network for the Pancakerouteradress
    pancake_eth_contract = w3.eth.contract(address=PANCAKEROUTER_Contract, abi=getABI(PANCAKEROUTER_Contract, driver))

    params ={
        'symbol': token_symbol,
        'w3': w3,
        'My_Wallet_Address': My_Wallet_Address,
        'token_eth_contract': token_eth_contract,
        'pancake_eth_contract': pancake_eth_contract,
        "PANCAKEROUTER_Contract": PANCAKEROUTER_Contract,
        'TOKEN_Contract': TOKEN_Contract,
        'WBNB_Contract': WBNB_Contract,
    }

    return token_symbol, wbnb_balance, token_balance, params


########################################################################################################################




# Function to emit a window sound when something happen
def windowsSound():
    for i in range(5):
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
    return


########################################## BUY TOKEN ##################################################################

# Function to buy token
def buyToken(**kwargs):
    # Params given of the key args
    symbol = kwargs["symbol"]
    w3 = kwargs["w3"]
    My_Wallet_Address = kwargs["My_Wallet_Address"]
    pancake_eth_contract = kwargs["pancake_eth_contract"]
    token_to_buy = kwargs["TOKEN_Contract"]
    WBNB_Contract = kwargs["WBNB_Contract"]
    amount = kwargs["amount"]

    buy_amount = w3.toWei(Decimal(amount), 'ether')

    # The minimum amount tokens to receive for the transaction in pancake
    amountOutMin = 0

    # An array of token addresses of which you would like to swap
    path_addresses = [WBNB_Contract, token_to_buy]

    # Address of the recipient
    address_to = My_Wallet_Address

    # Unix timestamp deadline by which the transaction must confirm.
    deadline = int(time.time() + 5000)

    # Build Transaction dictionary to give as a parameter, refer to:
    # "https://web3py.readthedocs.io/en/stable/web3.eth.html" ".send_transaction()" method
    transaction = {
        'from': My_Wallet_Address,
        'value': buy_amount,
        'gas': 300000,
        'gasPrice': w3.toWei('5', 'gwei'),
        'nonce': w3.eth.get_transaction_count(My_Wallet_Address)
    }

    # Private Key of the wallet to use
    private_key = json_config_data["PRIVATE_KEY"]

    # Call the function inside the contract of the pancakerouter v2 on line 111 to swap token
    # The "functions" method let the user interact with the functions of a contract
    transaction_pancake = pancake_eth_contract.functions.swapExactETHForTokens(amountOutMin, path_addresses,
                                                                               address_to,
                                                                               deadline).buildTransaction(transaction)

    # Sign the transaction with the private key to aprove the transaction
    signed_buy_transaction = w3.eth.account.sign_transaction(transaction_pancake, private_key= private_key)

    try:
        # Sends a signed and serialized transaction. Returns the transaction hash as a HexBytes object.
        raw_trans_token = w3.eth.send_raw_transaction(signed_buy_transaction.rawTransaction)

        # Get just the number of the transaction
        buy_transaction_number_finalized = w3.toHex(raw_trans_token)

        # Get the variable if it was successfully purchased
        if buy_transaction_number_finalized:
            buy_transaction_result = f"Successfully bought {amount} of {symbol}"

        # Return the list with the 2 answers, the txn number and the message
        results =[buy_transaction_number_finalized, buy_transaction_result]

        return results

    except ValueError as val:
        # Get the error code for debug in the future
        if val.args[0].get("message") in "intrinsic gas too low":
            results = ["Error, Failed", f"Failed: {val.args[0].get('message')} "]
        else:
            results = ["Error, Failed", f"Failed: {val.args[0].get('message')} : {val.args[0].get('code')}"]
        return results

########################################################################################################################

########################################## SELL TOKEN ##################################################################

# Function to sell token
def sellToken(**kwargs):
    # Params given of the key args
    symbol = kwargs["symbol"]
    w3 = kwargs["w3"]
    My_Wallet_Address = kwargs["My_Wallet_Address"]
    pancake_eth_contract = kwargs["pancake_eth_contract"]
    token_to_sell = kwargs["TOKEN_Contract"]
    WBNB_Contract = kwargs["WBNB_Contract"]
    token_eth_contract = kwargs["token_eth_contract"]
    PANCAKEROUTER_Contract = kwargs["PANCAKEROUTER_Contract"]
    amount = kwargs["amount"]

    # Convert the amount to sell in wei
    sell_amount = w3.toWei(Decimal(amount), 'ether')

    # The minimum amount tokens to receive for the transaction in pancake
    amountOutMin = 0

    # An array of token addresses of which you would like to swap
    path_addresses = [token_to_sell, WBNB_Contract]

    # Address of the recipient
    address_to = My_Wallet_Address

    # Unix timestamp deadline by which the transaction must confirm.
    deadline = int(time.time() + 5000)

    # Private Key of the wallet to use
    private_key = json_config_data["PRIVATE_KEY"]

    # Tokens that need to be approved first
    # Get the amount available in the current used wallet
    num_of_tokens_balance = token_eth_contract.functions.balanceOf(My_Wallet_Address).call()
    token_balance_in_wallet = w3.fromWei(num_of_tokens_balance, 'ether')

    if sell_amount <= num_of_tokens_balance:

        # Dictionary that must be pass as a parameter fot the .buildTransaction
        transaction1 = {
            'from': My_Wallet_Address,
            # 'value': sell_amount,
            'gas': 200000,
            'gasPrice': w3.toWei('5', 'gwei'),
            'nonce': w3.eth.get_transaction_count(My_Wallet_Address)
        }

        # Tokens that need to be approved first
        # Call the approval function of the token
        token_approval = token_eth_contract.functions.approve(PANCAKEROUTER_Contract,
                                                              num_of_tokens_balance).buildTransaction(transaction1)

        # Sign the transaction with the private key to aprove the transaction
        approved_signed_sell_transaction = w3.eth.account.sign_transaction(token_approval, private_key=private_key)

        # Sends a signed and serialized transaction. Returns the transaction hash as a HexBytes object.
        raw_trans_token = w3.eth.send_raw_transaction(approved_signed_sell_transaction.rawTransaction)

        # Get just the number of the transaction
        approved_sell_transaction_number_finalized = w3.toHex(raw_trans_token)

        # Print that the token was successfully approved
        if approved_sell_transaction_number_finalized:
            print(f"\nTransaction successfully approved, Txn  {approved_sell_transaction_number_finalized} ")

        # Continue with the process

            print(f"\nContinue with the swap of: {amount} {symbol} for BNB")

        time.sleep(10)

        transaction2 = {
            'from': My_Wallet_Address,
            # 'value': sell_amount,
            'gas': 200000,
            'gasPrice': w3.toWei('5', 'gwei'),
            'nonce': w3.eth.get_transaction_count(My_Wallet_Address)
        }

        # Do the swap
        # Call the function inside the contract of the pancakerouter v2 on line 111 to swap token
        # The "functions" method let the user interact with the functions of a contract
        transaction_pancake = pancake_eth_contract.functions.swapExactTokensForETH(sell_amount, amountOutMin,
                                                                                   path_addresses, address_to,
                                                                                   deadline).buildTransaction(transaction2)

        # Sign the transaction with the private key to aprove the transaction
        signed_sell_transaction = w3.eth.account.sign_transaction(transaction_pancake, private_key=private_key)

        try:
            # Sends a signed and serialized transaction. Returns the transaction hash as a HexBytes object.
            raw_trans_token = w3.eth.send_raw_transaction(signed_sell_transaction.rawTransaction)

            # Get just the number of the transaction
            sell_transaction_number_finalized = w3.toHex(raw_trans_token)

            # Get the variable if it was successfully purchased
            if sell_transaction_number_finalized:
                sell_transaction_result = f"Successfully sold {amount} of {symbol}"

            # Return the list with the 2 answers, the txn number and the message
            results =[sell_transaction_number_finalized, sell_transaction_result]

            return results

        except ValueError as val:
            # Get the error code for debug in the future
            if val.args[0].get("message") in "intrinsic gas too low":
                results = ["Error, Failed", f"Failed: {val.args[0].get('message')} "]
            else:
                results = ["Error, Failed", f"Failed: {val.args[0].get('message')} : {val.args[0].get('code')}"]
            return results
    else:
        message = print(f"Unfortunately, you are trying to sell more {amount} than you have: {token_balance_in_wallet}")
        return message

########################################################################################################################

########################################## Initialice a class of Thread ################################################

# Create a class to do over an over again a thread
class TradeThread(Thread):
    """
    A threading
    """
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        """Initialize the thread"""
        def function():
            self.results = target(*args, **kwargs)

        super().__init__(group=group, target=function, name=name, daemon=daemon)

########################################################################################################################

############################################ RUN TRADING ROBOT ########################################################

def StartBot():


    # Page to get the price of the token
    swap_url = f'https://swap.arken.finance/tokens/bsc/{TOKEN_Contract}'

    # Open the url of the page to get the price
    driver.get(swap_url)

    ################# Sometimes the webpage doesn´t load correctly without the enough time #############################
    sleep(2)

    initial_data = False
    get_new_data = True
    running_cycle = False
    first_time = True
    run_program = True

    while run_program:
    ########## HERE MUST START THE WHILE CYCLE #########################################################################

        if running_cycle:
            # Open the url of the page to get the price
            driver.get(swap_url)
            sleep(2)
            running_cycle = False
            if first_time:
                sleep(2)
                first_time = False

        # Get the source code of the token page, page_source method require the object, not variable
        # swap_page_code = WebDriverWait(driver, 3)until()
        swap_page_code = driver.page_source

        # print(swap_page_code)

        # Parse the source code into html language
        swap_code_parse = bsp(markup=swap_page_code, features="lxml")
        #print(swap_code_parse)

        # Find the price of the token
        live_price_token = swap_code_parse.find_all(name="b", attrs={"class": "number"})
        # Get just the price without the html code and witouht the "$" symbol
        live_price = live_price_token[0].get_text()[1:]
        print(live_price)


        # Price in type float to compare against the price that the user want
        live_price_float = float(live_price)
        print(type(live_price_float))

        # sleep(5)
        # clear()

        if not initial_data:
            if get_new_data:
                # Get data to trade
                token_symbol, wbnb_balance, token_balance, params = getUpdateInformation()
                get_new_data = False

            print("¡¡¡Welcome to the PyCakeSwap Bot!!!")
            # Show on the screen the current price of the token
            print(f"The actual price of {token_symbol} is: ${live_price}")
            # sleep(2)
            # clear()

            # Ask if the user want to swap or just get a notify when a price is reached:
            trading = bool(input("Would you like to trade or just get notify?"
                                 "\nTrade: Type any key and press enter "
                                 "\nNotify: *PRESS JUST ENTER*"
                                 "\nAnswer here: "))

            if trading:
                # Ask for the action that the user want to do
                accion = input("\n¿What would you like to do?\n"
                               "Buy or sell?\n"
                               "Write here:  ").lower()

                # Ask for the quantity (amount) of token to buy/sell {token_symbol}
                cantidad = input(f"\n¿What amount of WBNB would you like to {accion}?\n"
                                     "Write here: ")

                # Append the amount to the params dictionary
                params["amount"] = cantidad

                # Ask for the price that they would like to trade
                target = float(input(f"\n¿At what price would you like to {accion}?\n"
                                     "Write here: "))
            else:
                # Ask for the price that they would like to get notified
                target = float(input(f"\n¿At what price would you like to get notify?\n"
                                     "Write here: "))


            initial_data = True
            running_cycle = True

        # Message when the token is successful traded
        token_traded_msg = ""
        is_token_traded = False
        token_transaction = None

        # Print a message whe the token is successfully traded
        if is_token_traded:
            print(f"\n{token_symbol} was successfully traded!: "
                  f"\n The results are {token_traded_msg} "
                  f"\n Transaction: {token_transaction} ")



        if accion == "sell":
            # running_cycle = True
            print("Starting again")
            if live_price_float >= target:

                action1 = threading.Thread(target=windowsSound)
                if not trading:
                    action1.start()

                if trading:
                    action_trade = TradeThread(target=sellToken, kwargs=params)
                    action1.start()
                    action_trade.start()
                    action_trade.join()
                    action1.join()

                    transaction, recieved_message = action_trade.results
                    if transaction not in "Error, Failed" and show_transaction:
                        url = f"https://bscscan.com/tx/{transaction}"
                        print(f"CONGRATULATIONS, Successfully sell {cantidad} of {token_symbol} ")
                        informationTx(url)
                        sleep(2)

                    get_new_data = True
                    if bool(print("Would you like to be notified at a new price or shut down the Bot? "
                          "\nYes: Get a notification at a new price (Press any key and after that ENTER)"
                          "\nNo: Shut down (Press just ENTER)")):
                        target = float(input("What is the new price to get notified:"
                                             "\nWrite here: "))
                    else:
                        run_program = False
                        sleep(2)


        elif accion == "buy":
            # running_cycle = True
            print("Starting again")
            print("Still no error")
            if live_price_float <= target:
                print("Continue buying")

                action1 = threading.Thread(target=windowsSound)
                if not trading:
                    action1.start()

                if trading:
                    action_trade = TradeThread(target=buyToken, kwargs=params)
                    action1.start()
                    action_trade.start()
                    action_trade.join()
                    action1.join()

                    transaction, recieved_message = action_trade.results
                    if transaction not in "Error, Failed" and show_transaction:
                        url = f"https://bscscan.com/tx/{transaction}"
                        print(f"CONGRATULATIONS, Successfully buy {cantidad} of {token_symbol} ")
                        informationTx(url)
                        sleep(2)

                    get_new_data = True
                    if bool(print("Would you like to be notified at a new price or shut down the Bot? "
                          "\nYes: Get a notification at a new price (Press any key and after that ENTER)"
                          "\nNo: Shut down (Press just ENTER)")):
                        target = float(input("What is the new price to get notified:"
                                             "\nWrite here: "))
                    else:
                        run_program = False
                        sleep(2)

        else:
            clear()
            print("You have entered something wrong")
            sleep(2)
            print("Restarting the program right now")
            sleep(0.5)
            print("waiting..."); sleep(0.2)
            print("waiting..."); sleep(0.2)
            print("waiting..."); sleep(0.2)
            # We have to run again the program
            StartBot()
        sleep(2)


if __name__ == "__main__":
    StartBot()