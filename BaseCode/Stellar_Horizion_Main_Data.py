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
#requests is used to iniatie the transaction between friendbot and the Public keys
import requests

#Asset is used to issue Assets
#from stellar_sdk import Asset


#For keys to be used in the main Stellar Network, they need to have atleast 1 XLM
#Refer to https://www.stellar.org/lumens/exchanges to learn how to buy XLM
Source_pair_secret=input("Enter your Secret Key:")
Source_pair_public= input("Enter your Public Key")
Destination_pair_public=input("Enter Destination Public Key:")

Source_pubkey=Source_pair_public
Destination_pubkey=Destination_pair_public

#change to Network.TEST_NETWORK_PASSPHRASE if using Test Stellar Ledger instead of Main Stellar Ledger
Public_network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE

#establishes connection to Horizon server
server=Server('https://horizon.stellar.org')


#Activate code to find sequence number of the Source's public key that is required for transactions
#Source_account=server.load_account(Source_pubkey)
#print(Source_account)

#shows balance of Source.Pair account
Source_account=server.accounts().account_id(Source_pubkey).call()

for balance in Source_account['balances']:
    #XLM is Stellar's own Asset
    print(f"Asset Type:{balance['asset_type']},Total Balance:{balance['balance']}")


#checks if destination account exists,as if it doesn't, it will still be charged transaction fees
try:
    server.load_account(Destination_pubkey)
except NotFoundError:
    raise Exception("Account not found")

#gets current Base Fee
base_fee=server.fetch_base_fee()


Transaction_Trust= (
    TransactionBuilder(
        #loads Source_Pair Account
        source_account=server.load_account(Source_pubkey),
        #activates Network Passphrase(Testnet)
        network_passphrase=Public_network_passphrase,
        #establishes cost of Base fee
        base_fee=base_fee)

        .append_payment_op(destination=Destination_pubkey,
        amount=input("\nHow much would you like to send?\n"),
        asset_code=input("what asset would you like to send?\n"))

        .add_text_memo(input("What would you like to add as a memo?\n"))

        #times out the transaction if not completed within x seconds
        .set_timeout(int(input("How many seconds would you like for the transaction to be vaild for?\n")))
        .build()
        )

#signs transaction with Source_pair's Private key in order to verify transaction's authorization
Transaction_Trust.sign(Source_pair.secret)

#checks if Transaction was valid, otherwise prints out error response
try:
    Final_response=server.submit_transaction(Transaction_Trust)
    print(f"Response:{Final_response}")
    print("\nTransaction added to blockchain\n")
except (BadRequestError,BadResponseError) as error:
    print(f"Error:{error}")
