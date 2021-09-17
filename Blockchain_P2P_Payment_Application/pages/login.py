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

def app():
    sc = StellarClient()
    if sc.log_in():
            #sc.main_menu()
            #sc.main_menu()
        st.write(sc.send_payment())
        # sc.initialize_client('login')