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

import mysql.connector      
from Client.input_manager import InputManager
from hashlib import sha256
import time
from cryptography.fernet import Fernet
import streamlit as st




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

        self.mySQLConfig = {
                        'user': 'sql5436993',
                        'password': 'v7F7jRWVFc',
                        'host': 'sql5.freesqldatabase.com',
                        'database': 'sql5436993',
                        'raise_on_warnings': True
                        }

        self.public_network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE
        


    def SQL_initialize(self):
        self.connection = mysql.connector.connect(**self.mySQLConfig)

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
            




    def process_data(self):                                                                                     #<---------- Handles all data required inputs for account creation ---------->
        
        while True:
                                                                                                   #Starts loop until the new account ID entered is not already registered. 
            #REPLACE WITH STREAMLIT INPUT                                                       
            profileID = st.sidebar.text_input("Please enter your new account ID")              #Enters the new account ID.
            hashedProfileID = sha256(profileID.encode()).hexdigest()                                #Hashes it and turns it into hex string

            query = f"SELECT EXISTS(SELECT * FROM UserLoginData WHERE hashedUsername = \"{hashedProfileID}\") "       #Prepares SQL query

            queryResult = self.SQL_execute_twoway_statement(query)[0][0]                                            #Because the function returns an array with tuples, we want the first registry and the first element from the tuple.

            if queryResult:                                                                     #If the account is already registered, display message and continue in loop.
                st.error("This account ID is already registered, please try another one")
            else:
                with st.sidebar.form(key='my_form'):
                    #REPLACE WITH STREAMLIT INPUT 
                    profileName = st.text_input("Please enter your full name:")                                #Enters the person name.
                    #REPLACE WITH STREAMLIT INPUT 
                    profileAge = st.text_input(message="Please enter your age (Must be greater or equal than 18):")             #Enters the person age with bounds.
                    #REPLACE WITH STREAMLIT INPUT 
                    profileSex = st.text_input("Please enter the letter corresponding to your sex (Male = M) (Female = F):")                                       #Enters the person sex.
                    #REPLACE WITH STREAMLIT INPUT 
                    profilePassword = sha256(st.text_input("Please enter your password, must be minimum 6 characters long, maximum 30:").encode()).hexdigest()   #Enters the new account password with length bounds and hashes it.
                    #REPLACE WITH STREAMLIT INPUT 
                    publicKey = st.text_input("Please your public key:") 
                    #REPLACE WITH STREAMLIT INPUT 
                    privateKey = st.text_input("Please your private key:")
                    submit_but = st.sidebar.form_submit_button('Sign Up') 

                #Prepares data into a hashMap (Dictionary)
                if submit_but:
                    return {
                        "Username": profileID,
                        "HashedUsername": hashedProfileID,
                        "Name": profileName,
                        "Age": profileAge,
                        "Sex": profileSex,
                        "Password": profilePassword,
                        "PublicKey": publicKey,
                        "PrivateKey": privateKey,
                    }      

    def create_account(self): #Full creation of an account process

        profileData = self.process_data()  #Gets all the needed data for the creation of an account

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

        st.info(f"Encrypt Key: {encryptKey}")                                         #If no errors, display successful creation
        st.success("Account succesfully created")                                         #If no errors, display successful creation

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

            return True

    def main_menu(self):                                                                                    #<---------- Main menu for logged users ---------->
        def display_balance():                                                                              #Displays the balance of the current logged user.
            for balance in self.Source_account['balances']:
                #XLM is Stellar's own Asset
                print(f"Asset Type:{balance['asset_type']},Total Balance:{balance['balance']}")
            InputManager.display_message(message = "")

        def display_account_data():                                                                         #Displays all the available data of the current logged user.
            print("")                                                                                       
            print(f"Your registered ID is   : {self.sessionID}")
            print(f"Your registered Name is : {self.name}")
            print(f"Your registered Age is  : {self.age}")
            print(f"Your registered Sex is  : {self.sex}")
            print(f"Balances: ")
            display_balance()


        def send_payment():        
                                                                                     #Initializes the process for sending a payment to another user.            
            receiverOption = InputManager.define_numbers(message="Please enter 1 if the receiver has an account, 2 if not:", infLimit = 1, supLimit = 2,typeOfNumber = int)
            
            if receiverOption == 1:
                #STARTS QUERIES FOR UserPublicKey TABLE
                destinationUsername = InputManager.define_string("Please enter the destination username:")

                query = f"SELECT publicKey FROM UserPublicKey WHERE username = \"{destinationUsername}\""
                queryResult = self.SQL_execute_twoway_statement(query)

                if not queryResult:
                    InputManager.display_message(message = "This user does not exists, please try again")
                    return
                destinationPublicKey = queryResult[0][0]
                #FINISHES QUERIES FOR UserPublicKey TABLE
            else:
                destinationPublicKey = InputManager.define_string("Please enter the destination public key:")

            base_fee=self.server.fetch_base_fee()
            feeConfirmation = InputManager.define_numbers(message=f"An ammount of {base_fee} will be charged as fee, enter 1 if you confirm, 2 for cancelling", infLimit = 1, supLimit = 2,typeOfNumber = int)

            if feeConfirmation == 2:
                InputManager.display_message(message="Transaction canceled")
                return  
            try:
                self.server.load_account(destinationPublicKey)
            except NotFoundError:
                InputManager.display_message(message="Account not found")
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
                    amount=input("\nHow much would you like to send?\n"),
                    asset_code=input("\nWhat asset would you like to send?\n"))

                    .add_text_memo(input("What would you like to add as a memo?\n"))

                    #times out the transaction if not completed within x seconds
                    .set_timeout(int(input("\nHow many seconds would you like for the transaction to be vaild for?\n")))
                    .build()
                    )
            Transaction_Trust.sign(self.privateKey)

            try:
                Final_response=self.server.submit_transaction(Transaction_Trust)
                print(f"Response:{Final_response}")
                InputManager.display_message(message = "\nTransaction added to blockchain\n")
                # print(f"Response:{Final_response}")
                # print("\nTransaction added to blockchain\n")
            except (BadRequestError,BadResponseError) as error:
                InputManager.display_message(message=f"Error: {error}")



        while True:                                                             #Menu for logged users.
            print("")
            print("*****************************************************")
            print(f"WELCOME {self.sessionID}")
            print("")
            print("1) See current balance")
            print("2) Send payment")
            print("3) See my account data")
            print("4) Exit")
            print("")
            print("*****************************************************")
            selectedOption = InputManager.define_numbers(message="Type a number according to your selected option:", infLimit = 1, supLimit = 4,typeOfNumber = int)
            if selectedOption == 4:
                break
            
            if selectedOption == 1:
                display_balance()
            
            if selectedOption == 2:
                send_payment()

            if selectedOption == 3:
                display_account_data()
        



    def initialize_client(self, selectedOption):
        self.SQL_initialize()
        while True:                                                             #Main loop that runs the client console menu.
            #selectedOption = InputManager.define_numbers(message="Type a number according to your selected option", infLimit = 1, supLimit = 3,typeOfNumber = int) #Calls InputManager function for entering a bounded number and repeating until the number is accepted.                                                           #Breaks the main loop and exits the program.
            if selectedOption == 'login': #Not coded yet                                  #Executes what you need to log in into your account.
                logFlag = self.log_in()                                             #Calls the log in service, if is successful returns 'True' else returns 'False'.
                if logFlag:                                                         #If the log in service is successful, call the main logged menu.
                    self.main_menu()

            if selectedOption == 'create_account':                                                 #Executes the necessary for creating an account.
                self.create_account()         



if __name__ == "__main__":
    client = StellarClient()
    client.initialize_client()