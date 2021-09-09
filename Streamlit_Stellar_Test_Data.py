import streamlit as st

st.write("""
# World Data Science Institue
""")

st.title('Welcome to P2P Payment Transfer')


#import stellar-sdk==4.1.1 

#stellar_sdk.keypair is used to generate keypairs which are used for transactions
from stellar_sdk.keypair import Keypair
#stellar_sdk.server used to connect to Stellar-core through the Horizon API
from stellar_sdk.server import Server
#stellar_sdk.network is used to get the Passphrase of either the test or main Stellar network 
from stellar_sdk.network import Network
#TransactionBuilder is used to create 
from stellar_sdk import TransactionBuilder
#stellar_sdk.exceptions is used for Error Dectection in transactions
from stellar_sdk.exceptions import NotFoundError,BadResponseError,BadRequestError
#requests is used to initiate the transaction between friendbot and the Public keys
import requests

#Asset is used to issue Assets
#from stellar_sdk import Asset


#Generates 2 keypairs for Source and Destination Addresses
Source_pair=Keypair.random()
Destination_pair=Keypair.random()
st.text(f"\nSource Secret:{Source_pair.secret}\n")
st.text(f"Source Public:{Source_pair.public_key}\n")
st.text(f"Destination Secret:{Destination_pair.secret}\n")
st.text(f"Destination Public:{Destination_pair.public_key}\n")

Source_pubkey=Source_pair.public_key
Destination_pubkey=Destination_pair.public_key

#change to Network.PUBLIC_NETWORK_PASSPHRASE if using Main Stellar Ledger instead of Test Stellar Ledger
Public_network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE

#accounts need atleast 1 XLM to exist in Stellar's blockchain ledger 
#Stellar Friendbot gives 10,000 XLM,as for accounts
friend_url="https://friendbot.stellar.org"
Source_response=requests.get(friend_url,params={"addr" :  Source_pair.public_key})
Destination_response=requests.get(friend_url,params={"addr" :  Destination_pair.public_key})

#Checks if the account creation was sucessful, otherwise prints error
if Source_response.status_code==200:
    st.text("Account creation Sucessful!")
else:
    st.text("Error")

#establishes connection to Horizon-testnet server
server=Server('https://horizon-testnet.stellar.org')



#Activate code to find sequence number of the Source's public key that is required for transactions
#Source_account=server.load_account(Source_pubkey)
#print(Source_account)

#shows balance of Source.Pair account after transaction with friendbot
Source_account=server.accounts().account_id(Source_pubkey).call()
for balance in Source_account['balances']:
    #XLM is Stellar's own Asset,and in order to not confuse beginners, Code changes it to say XLM
    if balance['asset_type']=="native":
        st.text(f"Asset Type:XLM,Total Balance:{balance['balance']}")
    else:
        st.text(f"Asset Type:{balance['asset_type']},Total Balance:{balance['balance']}")




#checks if destination account exists,as if it doesn't, it will still be charged transaction fees
try:
    server.load_account(Destination_pubkey)
except NotFoundError:
    st.text("Account not found")
    raise Exception("Account not found")
    

#gets current Base Fee
base_fee=server.fetch_base_fee()

amount=st.text_input("How much would you like to send?")
asset_code=st.text_input("what asset would you like to send?\n")
        
add_text_memo=(st.text_input("What would you like to add as a memo?\n"))


set_timeout=(st.text_input("How many seconds would you like for the transaction to be vaild for?\n"))
Transaction_Trust= (
    TransactionBuilder(
        #loads Source_Pair Account
        source_account=server.load_account(Source_pubkey),
        #activates Network Passphrase(Testnet)
        network_passphrase=Public_network_passphrase,
        #establishes cost of Base fee
        base_fee=base_fee)

        .append_payment_op(destination=Destination_pubkey,
        amount=amount,
        asset_code=asset_code
        )
        .add_text_memo(add_text_memo)

        #times out the transaction if not completed within x seconds
        .set_timeout(int(set_timeout))
        .build()
        )

#signs transaction with Source_pair's Private key in order to verify transaction's authorization
Transaction_Trust.sign(Source_pair.secret)

#checks if Transaction was valid, otherwise prints out error response
try:
    Final_response=server.submit_transaction(Transaction_Trust)
    st.text(f"Response:{Final_response}")
    st.text("\nTransaction added to blockchain\n")
except (BadRequestError,BadResponseError) as error:
    st.text(f"Error:{error}")
