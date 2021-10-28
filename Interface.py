####################################################### CREATE INTERFACE GUI ###########################################
import os
from tkinter import *
import time

window = Tk()
window.title("DEX PancakeBot")
window.minsize(width=500, height= 600)
window.config(padx=20, pady=20)

# Title
Title = Label(text="Welcome to the Limit PancakeSwap Bot", font=("Century", 16))
Title.grid(column=1, row=0)

################################################ Define all function ##################################################

def run_bot():
    buy_qty = buy_amount_entry.get()
    contract = contract_token_entry.get()
    target = target_price_entry.get()
    new_text = (f"You are running the bot\n"
          f"Buy: {buy_qty}\n"
          f"Contract: {contract}\n"
          f"target: {target}")
    label_resume.config(text=new_text)

def actual_time():
    hour = time.strftime("%H")
    minute = time.strftime("%M")
    second = time.strftime("%S")

    label_time.config(text=hour + ":" + minute + ":" + second)
    label_time.after(1000, actual_time)


def close_window():
    new_text = buy_amount_entry.get()
    label1.config(text=new_text)


def action_buy_Sell():
    if action.get() == 1:
        print("Buy token")
    elif action.get() == 2:
        print("Sell Token")


# Radiobutton
def radio_used():
    print(radio_state.get())

#################################################### Define all Labels #################################################

# Label
label1 = Label(text="This the first GUI of the bot", font=("Century", 16))
label1.grid(column=1, row=1)

# Label for time
label_time = Label(text="", font=("Century", 16))
label_time.grid(column=1, row=7)

# Label for amount
label_amount = Label(text="How much amount of WBNB would you like to trade ", font=("Century", 16))
label_amount.grid(column=0, row=3)

# Label for contract
label_contract = Label(text="What is the contract to trade (Omit if in config file) ", font=("Century", 16))
label_contract.grid(column=0, row=5)

# Label for target price
label_target_price_entry = Label(text="What is the target price?", font=("Century", 16))
label_target_price_entry.grid(column=0, row=7)

# Label final
label_resume = Label(text=" ", font=("Century", 16))
label_resume.grid(column=0, row=15)

############################################## Define all entries ######################################################

# Entry for the buy amount
buy_amount_entry = Entry(width=15)
buy_amount_entry.grid(column=0, row=4)

# Entry for write the contract
contract_token_entry = Entry(width=25)
contract_token_entry.grid(column=0, row=6)

# Entry for the target price
target_price_entry = Entry(width=15)
target_price_entry.grid(column=0, row=8)

######################################### Define the RadioButtons ######################################################

#Variable to hold on to which radio button value is checked.
radio_state = IntVar()
tradeButton = Radiobutton(text="Trade", value=1, variable=radio_state, command=radio_used)
notifyButton = Radiobutton(text="Notify", value=2, variable=radio_state, command=radio_used)
tradeButton.grid(column=0, row=10)
notifyButton.grid(column=0, row=11)

#Variable to hold on to which radio button value is checked Buy or Sell.
action = IntVar()
BuyButton = Radiobutton(text="Buy", value=1, variable=action, command=action_buy_Sell)
SellButton = Radiobutton(text="Sell", value=2, variable=action, command=action_buy_Sell)
BuyButton.grid(column=1, row=10)
SellButton.grid(column=1, row=11)

################################################## Define Buttons ######################################################

# Button to close the program
run = Button(text="Run", command=run_bot)
run.grid(column=0, row=12)


# Button to close the program
close = Button(text="Close", command=window.destroy)
close.grid(column=1, row=12)

# # Button
# button = Button(text="Sell", command=close_window)
# button.grid(column=0, row=5)
#
# button = Button(text="Buy", command=close_window)
# button.grid(column=3, row=5)


actual_time()

window.mainloop()
