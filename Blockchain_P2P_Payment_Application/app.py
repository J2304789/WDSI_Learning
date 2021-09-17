import streamlit as st
st.set_page_config(page_title='P2P Payment App', layout='wide', initial_sidebar_state='auto')
import datetime


# Custom imports 
from multiapp import MultiPage
from pages import home, login, signup
from typing import Text
import streamlit as st
from re import U
from stellar_sdk.keypair import Keypair
#stellar_sdk.server used to connect to Stellar-core through the Horizon API
from stellar_sdk.server import Server
#stellar_sdk.network is used to get the Passphrase of either the test or main Stellar network 
from stellar_sdk.network import Network
#TransactionBuilder is used to create 
from stellar_sdk import TransactionBuilder
#stellar_sdk.exceptions is used for Error Dectection in transactions
from stellar_sdk.exceptions import NotFoundError,BadResponseError,BadRequestError
# #requests is used to initiate the transaction between friendbot and the Public keys
import requests

from Client.stellar_client import StellarClient

import mysql.connector      
from Client.input_manager import InputManager
from hashlib import sha256
import time
from cryptography.fernet import Fernet
import streamlit as st
import pandas as pd

# Create an instance of the app 
app = MultiPage()


# Title of the main page
st.title("P2P Payment app")

#st.header("")
st.markdown('---')

custom_green = 'rgb(124, 230, 110)'
custom_red = 'rgb(230, 134, 110)'
custom_blue = 'rgb(110, 186, 230)'
custom_orange = 'rgb(230, 172, 110)'
        #self.send_payment()

server = Server('https://horizon.stellar.org')
public_network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE
options = st.sidebar.selectbox('Pages', options=['Login', 'Create Account'])
sc = StellarClient()

def transaction_form():
    col_1_1, col_2_1, col_3_1 = st.columns((1, 5, 1))
    with col_2_1:
        with st.expander('I want to make a transaction!'):
            with st.form(key='transaction_form'):
                destinationPublicKey = st.text_input("Please enter the destination public key:")

                source_key = st.text_input('Please, enter your public key!')       

                privateKey = st.text_input('Please, enter your secret key!', type='password')
                if privateKey:
                    source_key = Keypair.from_secret(privateKey)
                base_fee = server.fetch_base_fee()
                amount_money = st.text_input("\nHow much would you like to send?\n") 
                asset_transaction = st.text_input("\nWhat asset would you like to send?\n")
                memo_message = st.text_input("What would you like to add as a memo?\n")
                valid_time = st.text_input("\nHow many seconds would you like for the transaction to be vaild for?\n")
                submit_transaction = st.form_submit_button('Make transaction')
            
            if submit_transaction:
                st.spinner(f"An ammount of {base_fee} will be charged as fee")
                if (not amount_money or not asset_transaction or not valid_time):
                    st.warning('Fill al the fields to continue your transaction!')
                else:
                    try:
                        server.accounts().account_id(destinationPublicKey).call()
                    except:
                        st.error('Invalid Public Key!')
                    Transaction_Trust= (
                                        TransactionBuilder(
                                            #loads Source_Pair Account
                                            source_account=server.load_account(source_key.public_key),
                                            #activates Network Passphrase(Testnet)
                                            network_passphrase=public_network_passphrase,
                                            #establishes cost of Base fee
                                            base_fee=base_fee
                                            )

                                            .append_payment_op(destination=destinationPublicKey,
                                            amount=amount_money,
                                            asset_code=asset_transaction)

                                            .add_text_memo(memo_message)

                                            #times out the transaction if not completed within x seconds
                                            .set_timeout(int(valid_time))
                                            .build()
                                            )

                    Transaction_Trust.sign(privateKey)

                    try:
                            Final_response=server.submit_transaction(Transaction_Trust)
                            st.success("\nYour transaction was succesfull! Transaction added to blockchain\n")
                    except (BadRequestError,BadResponseError) as error:
                            st.error(f"The transaction failed, please try again!")
    return

if options == 'Login':
    if sc.log_in():
        sc.main_menu()
    transaction_form()
else:
    signup.app()