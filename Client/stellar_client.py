from re import U
from typing import ValuesView
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

#import mysql.connector
import psycopg2
from Client.input_manager import InputManager
from hashlib import sha256
import time
from cryptography.fernet import Fernet
import streamlit as st
import pandas as pd
import os




class StellarClient:

    def __init__(self):

        self.sessionID = ""
        self.name = ""
        self.hashedSessionID = ""
        self.sessionPassword = ""
        self.privateKey = ""
        self.encryptKey = ""
        self.sex = ""
        self.age = ""
        self.balances = ""
        #self.connection = None

        self.posSQLConfig = {
                        'user': 'pcmsnpipsrhmfv',
                        'password': '98429e5d87a9ec2ec50a22f4469a2d78cc79a5d6fb136d2c72d554c0e72ba447',
                        'host': 'ec2-54-145-110-118.compute-1.amazonaws.com',
                        'database': 'd21v5u2d9flgmq'
                        }

        self.public_network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE
        self.SQL_initialize()
        


    def SQL_initialize(self):
        #self.connection = mysql.connector.connect(**self.mySQLConfig)
        
        self.connection = psycopg2.connect(**self.posSQLConfig)

    def SQL_execute_oneway_statement(self,query):
        try:
            statement = self.connection.cursor()

            statement.execute(query)

            self.connection.commit()

            statement.close()

            queryExecuted = True
        except TypeError as e:
            # InputManager.display_message(f"Error: {e}")
            queryExecuted = False

        
        return queryExecuted
    
    def SQL_execute_twoway_statement(self,query):
        try:
            statement = self.connection.cursor()

            statement.execute(query)

            data = []

            queryResult = statement.fetchone()

            while (queryResult != None):
                registry = queryResult
                data.append(registry)

                queryResult = statement.fetchone()
            
            # print(data)
            
            statement.close()
        except Exception as e:
            InputManager.display_message(f"Error: {e}")
            data = "Error in query"
        return data
            




    def process_data(self, profileData):                                                                                     #<---------- Handles all data required inputs for account creation ---------->
        

        encryptKey = Fernet.generate_key()  #Generates a unique encryption key
        fernetKey = Fernet(encryptKey)      #Generates a Fernet object for encrypting things with the key in bytes format
        encryptKey = encryptKey.decode()     #Passes the key to a string

        #STARTS QUERIES FOR UserLoginData TABLE

        query = f"INSERT INTO UserLoginData VALUES(\"{profileData['HashedUsername']}\" , \"{profileData['Password']}\", \"{encryptKey}\")"  #Prepares the SQL query
        queryResult = self.SQL_execute_oneway_statement(query)                                                                              #Executes the SQL query

        if not queryResult:                                                                                 #If this query wasn't successful, print error.
            st.error("There was an error while creating your account, query 1")
            return

        #FINISHES QUERIES FOR UserLoginData TABLE

        usernameSpecialHash = profileData["Username"]+"WDSI"                                                    #We salt the username with a 'WSDI' string for more security
        usernameSpecialHash = sha256(usernameSpecialHash.encode()).hexdigest()                                  #We hash the username

        bytesPrivateKey = profileData["PrivateKey"].encode()                                                    #Gets the private key and pass it into a bytes format
        encryptedPrivateKey = fernetKey.encrypt(bytesPrivateKey).decode()                                       #Encrypts the private key and pass it to string

        bytesName = profileData["Name"].encode()                                                                #Passes the name and pass it into bytes format
        encryptedName = fernetKey.encrypt(bytesName).decode()                                                   #Encrypts the name and pass it to string

        balances = "{}"

        #STARTS QUERIES FOR UserData TABLE

        query2 = f"INSERT INTO UserData VALUES(\"{usernameSpecialHash}\",\"{encryptedPrivateKey}\",\"{encryptedName}\", \"{profileData['Sex']}\", {profileData['Age']},\"{balances}\")" #Prepares SQL query
        queryResult2 = self.SQL_execute_oneway_statement(query2)

        if not queryResult2:                                                                                    #If this query wasn't successful, print error.
            st.error("There was an error while creating your account, query 2")
            return

        #FINISHES QUERIES FOR UserData TABLE


        #STARTS QUERIES FOR UserPublicKey TABLE
    
        query3 = f"INSERT INTO UserPublicKey VALUES(\"{profileData['Username']}\",\"{profileData['PublicKey']}\")"
        queryResult3 = self.SQL_execute_oneway_statement(query3)

        #FINISHES QUERIES FOR UserPublicKey TABLE

        if not queryResult3:
            st.error(message = "There was an error while creating your account, query 2")
            return

        #st.info(f"Encrypt Key: {encryptKey}")                                         #If no errors, display successful creation
        st.success("Account succesfully created")                                        #If no errors, display successful creation
    

    def log_in(self):
        #with st.sidebar.text:
        sessionID = st.sidebar.text_input("Please enter your account ID", key='1')
        sessionPassword = sha256(st.sidebar.text_input("Please enter your password:", type='password', key='2').encode()).hexdigest()
        submit = st.sidebar.button('Login')
        #STARTS QUERIES FOR UserLoginData TABLE
        if submit:
            hashedSessionID = sha256(sessionID.encode()).hexdigest()
            query = f"SELECT encryptionKey FROM UserLoginData WHERE hashedUsername = \"{hashedSessionID}\" AND hashedPassword = \"{sessionPassword}\""
            queryResult = self.SQL_execute_twoway_statement(query)
        
            #FINISHES QUERIES FOR UserLoginData TABLE

            if not queryResult:
                st.error("The password or user for this account is incorrect, please try again")
                return False
            else:
                self.sessionID = sessionID
                self.hashedSessionID = hashedSessionID
                self.sessionPassword = sessionPassword
                self.encryptKey = queryResult[0][0].encode()
                st.sidebar.success('You logged succesfully!')

            usernameSpecial = self.sessionID+"WDSI"                                                    #We salt the username with a 'WSDI' string for more security
            usernameSpecialHash = sha256(usernameSpecial.encode()).hexdigest()

            #STARTS QUERIES FOR UserData TABLE

            query2 = f"SELECT * FROM UserData WHERE usernameSpecialHash = \"{usernameSpecialHash}\""
            queryResult2 = self.SQL_execute_twoway_statement(query2)

            #FINISHES QUERIES FOR UserData TABLE

            fernetKey = Fernet(self.encryptKey)      #Generates a Fernet object for encrypting things with the key in bytes format

            nameEncrypted = queryResult2[0][2].encode()
            self.name = fernetKey.decrypt(nameEncrypted).decode()

            privateKeyEncrypted = queryResult2[0][1].encode()
            self.privateKey = fernetKey.decrypt(privateKeyEncrypted).decode()

            self.sex = queryResult2[0][3]
            self.age = queryResult2[0][4]
            self.balances = queryResult2[0][5]
            #STARTS QUERIES FOR UserPublicKey TABLE

            query3 = f"SELECT publicKey FROM UserPublicKey WHERE username = \"{self.sessionID}\""
            queryResult3 = self.SQL_execute_twoway_statement(query3)

            self.publicKey = queryResult3[0][0]
            #FINISHES QUERIES FOR UserPublicKey TABLE

            #InputManager.display_message(message = f"Publickey: {self.publicKey}")                                         #If no errors, display successful creation
            
            #STELLAR CONFIG

            self.server = Server('https://horizon.stellar.org')
            #self.server = Server("https://horizon-testnet.stellar.org")
            try:
                self.Source_account=self.server.accounts().account_id(self.publicKey).call()
            except:
                #InputManager.display_message(message = "Invalid Stellar public key")
                #st.error('We cannot found your Public Key!')
                return False
            st.success('You logged succesfully!')
            return True

    def main_menu(self):                                                                                    #<---------- Main menu for logged users ---------->
        # sourcery no-metrics
        def display_balance():
            dataframe = {'Asset Type': [], 
                         'Total Balance': []}                                                                            #Displays the balance of the current logged user.
            for balance in self.Source_account['balances']:
                if balance['asset_type'] == "native":
                    balance['asset_type'] = "XLM"
                dataframe['Asset Type'].append(balance['asset_type'])
                dataframe['Total Balance'].append(balance['balance'])
                # return {'Asset Type': [balance['asset_type']], 
                #                 'Total Balance': [balance['balance']]}
                #st.write(f"Asset Type: {balance['asset_type']}, Total Balance: {balance['balance']}")
            #InputManager.display_message(message = "")
            dataframe = pd.DataFrame(dataframe)

            dataframe.index = dataframe['Asset Type']
            dataframe.drop('Asset Type', axis=1, inplace=True)
            # print(dataframe)
            return dataframe

        def display_account_data():                                                                         #Displays all the available data of the current logged user.
                                                                                                 
            registered_id = [self.sessionID]
            name = [self.name]
            age = [self.age]
            sex = [self.sex]
            return registered_id, name, age, sex


        def send_payment():        
                                                                                     #Initializes the process for sending a payment to another user.            
            receiverOption = st.text_input("Please enter YES if the receiver has an account, NO if not: ", key='3')
            
            # receiverOption = InputManager.define_numbers(message="Please enter 1 if the receiver has an account, 2 if not:", infLimit = 1, supLimit = 2,typeOfNumber = int)
            print(f"R: '{receiverOption}'")
            if receiverOption == "YES":
                #STARTS QUERIES FOR UserPublicKey TABLE
                destinationUsername = st.text_input("Please enter the destination username: ", key='4')

                # destinationUsername = InputManager.define_string("Please enter the destination username:")

            destinationUsername = st.text_input("Please enter the destination username:")
            if destinationUsername:
                query = f"SELECT publicKey FROM UserPublicKey WHERE username = \"{destinationUsername}\""
                queryResult = self.SQL_execute_twoway_statement(query)

                if not queryResult:
                    st.warning("This user does not exists, please try again!")
                    return
                destinationPublicKey = queryResult[0][0]
            self.know_form_builder()
                #FINISHES QUERIES FOR UserPublicKey TABLE
            #button_avance = st.form_submit_button('Advance in transaction')
            if receiverOption != 'Yes, I do!':
                with st.form(key='unknow_key'):
                    destinationPublicKey = st.text_input("Please enter the destination public key:")

                    base_fee=self.server.fetch_base_fee()
                    feeInformation = st.info(f"An ammount of {base_fee} will be charged as fee")
                    feeConfirmation = st.radio('Do you want to continue?', 
                                                options=["Yes!", "No! I want to cancel this transaction!"])

                if feeConfirmation =="No! I want to cancel this transaction!":
                    st.info('This transacttion was canceled!')
                    return 
                else:
                    if destinationPublicKey:
                        try:
                            self.server.load_account(destinationPublicKey)
                        except NotFoundError:
                            st.warning("This Account was not found. Please, put a valid accounnt!")
                            return
        with st.form(key='trans_form'):
            destinationPublicKey = st.text_input("Please enter the destination public key:")
            amount_money = st.text_input("\nHow much would you like to send?\n") 
            asset_transaction = st.text_input("\nWhat asset would you like to send?\n")
            memo_message = st.text_input("What would you like to add as a memo?\n")
            valid_time = st.text_input("\nHow many seconds would you like for the transaction to be vaild for?\n")

            submit_transaction = st.form_submit_button('Make transaction!')
        if submit_transaction:
            if not destinationPublicKey or not amount_money or not asset_transaction or not valid_time:
                st.warning('Fill al the fields to continue your transaction!')
            else:
                destinationPublicKey = st.text_input("Please enter the destination public key: ", key='5')
                # destinationPublicKey = InputManager.define_string("Please enter the destination public key:")

            base_fee=self.server.fetch_base_fee()
            feeConfirmation = int(st.text_input(f"An ammount of {base_fee} will be charged as fee, enter 1 if you confirm, 2 for cancelling", key='6'))
            # feeConfirmation = InputManager.define_numbers(message=f"An ammount of {base_fee} will be charged as fee, enter 1 if you confirm, 2 for cancelling", infLimit = 1, supLimit = 2,typeOfNumber = int)

            if feeConfirmation == 2:
                st.error("Transaction canceled")
                # InputManager.display_message(message="Transaction canceled")
                return  
            try:
                self.server.load_account(destinationPublicKey)
            except NotFoundError:
                st.error("Account not found")
                # InputManager.display_message(message="Account not found")
                return
            
            Transaction_Trust= (
                TransactionBuilder(
                    #loads Source_Pair Account
                    source_account=self.server.load_account(self.publicKey),
                    #activates Network Passphrase(Testnet)
                    network_passphrase=self.public_network_passphrase,
                    #establishes cost of Base fee
                    base_fee=base_fee
                    )

                    .append_payment_op(destination=destinationPublicKey,
                    
                    amount = st.number_input("How much would you like to send?", key='7'),
                    asset_code = st.text_input("What asset would you like to send?: ", key='8') )

                    .add_text_memo(st.text_input("What would you like to add as a memo? ", key='9'))

                    #times out the transaction if not completed within x seconds
                    .set_timeout(int(st.number_input("How many seconds would you like for the transaction to be vaild for? ", key='10', min_value=0)))
                    .build()
                    )

            try:
                Final_response=self.server.submit_transaction(Transaction_Trust)
                print(f"Response:{Final_response}")
                st.success('Transaction added to blockchain')
                # InputManager.display_message(message = "\nTransaction added to blockchain\n")
                # print(f"Response:{Final_response}")
                # print("\nTransaction added to blockchain\n")
            except (BadRequestError,BadResponseError) as error:
                st.error(f"Error: {error}")
                # InputManager.display_message(message=f"Error: {error}")

        fcol_1, fcol_2, fcol_3 = st.columns((1, 2, 1))
        with fcol_2:
            with st.expander('Click to display your balance'):
                st.table(display_balance())
        scol_1, scol_2, scol_3 = st.columns((1, 5, 1))
        with scol_2:
            with st.expander('Click here to see your account data.'): 
                id, name, age, sex = self.display_account_data()
                st.table(pd.DataFrame({'id':id, 
                                        'name':name, 
                                        'age':age, 
                                        'sex':sex}))
        tcol_1 = st.columns((1))
        # with tcol_1:
        #     with st.expander('Click here to make a payment.'): 
        send_payment()


    # def initialize_client(self, selectedOption):
    #     self.SQL_initialize()
    #     while True:                                                             #Main loop that runs the client console menu.
    #         #selectedOption = InputManager.define_numbers(message="Type a number according to your selected option", infLimit = 1, supLimit = 3,typeOfNumber = int) #Calls InputManager function for entering a bounded number and repeating until the number is accepted.                                                           #Breaks the main loop and exits the program.
    #         if selectedOption == 'login': #Not coded yet                                  #Executes what you need to log in into your account.
    #             logFlag = self.log_in()                                             #Calls the log in service, if is successful returns 'True' else returns 'False'.
    #             if logFlag:                                                         #If the log in service is successful, call the main logged menu.
    #                 self.main_menu()

    #         if selectedOption == 'create_account':                                                 #Executes the necessary for creating an account.
    #             self.create_account()         



if __name__ == "__main__":
    # client = StellarClient()
    # client.initialize_client()
    pass