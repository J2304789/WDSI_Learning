from hashlib import sha256
import socket
import json
import time
from input_manager import InputManager

class Client:
    def __init__(self):
        self.sessionID = ""
        self.sessionName = ""
        self.sessionAge = ""
        self.sessionSex = ""
        self.sessionPassword = ""
        self.sessionBalance = 0
        self.sessionData = {}
    
    def start_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("127.0.0.1",5010))
    
    def stop_socket(self):

        self.sock.close()
    
    def process_data(self):                                                                                     #<---------- Handles all data required inputs for account creation ---------->
        
        transactionType = "verifyUser"                                                                      #Defines transaction type.
        while True:                                                                                         #Starts loop until the new account ID entered is not already registered.
            self.start_socket()                                                                                 #Starts socket.
            profileID = InputManager.define_string("Please enter your new account ID: ")                          #Enters the new account ID.

            self.sock.send(transactionType.encode())                                                            #Encodes transaction type and sends it to server.

            time.sleep(1)                                                                                       #Sets 1 second delay for preventing joining bytes packages in server reception.
            self.sock.send(profileID.encode())                                                                  #Encodes new account ID and sends it to server for existance verification.
            transactionResult = self.sock.recv(1024).decode()                                                   #Awaits and reveices server response.
            # print(transactionResult)
            self.stop_socket()                                                                                  #Disconnects socket.
            if transactionResult == "True":                                                                     #If the account is already registered, display message and continue in loop.
                InputManager.display_message("This account ID is already registered, please try another one!")
            else:                                                                                               #If the account is not registered, break the loop.
                break

        profileName = InputManager.define_string("Please enter your full name:")                                #Enters the person name.
        profileAge = InputManager.define_numbers(message="Please enter your age (Must be equal or greater than 18): ", infLimit = 18,typeOfNumber = int)             #Enters the person age with bounds.
        profileSex = InputManager.define_string("Please enter the letter corresponding to your sex (Male = M) (Female = F): ")                                       #Enters the person sex.
        profilePassword = sha256(InputManager.define_string(message="Please enter your password, must be minimum 6 characters long, maximum 30: ", infLimit=6, supLimit=30).encode())    #Enters the new account password with length bounds.

        # print(self.profileData)
        return {
            "ID": profileID,
            "Name": profileName,
            "Age": profileAge,
            "Sex": profileSex,
            "Password": profilePassword.hexdigest(),
        }
        

    def create_account(self):                                                                           #<---------- Starts create account process ---------->
        
        profileData = self.process_data()                                                               #Processes all the data needed for an account creation.

        self.start_socket()                                                                             #Starts socket.
        
        transactionType = "createClient"                                                                #Defines transaction type.
        self.sock.send(transactionType.encode())                                                        #Encodes transaction type and sends it to the server.

        data = json.dumps(profileData)                                                                  #Transforms profile data into json string format.

        time.sleep(1)                                                                                   #Sets 1 second delay for preventing joining bytes packages in server reception.
        self.sock.send(data.encode())                                                                   #Encodes profile data and sends it to server.

        transactionResult = self.sock.recv(1024).decode()                                               #Awaits and receives server response.

        self.stop_socket()                                                                              #Disconnects socket.
        InputManager.display_message("Transaction result: " + transactionResult)                        #Displays transaction result.

    def log_in(self):                                                                                   #<---------- Starts log in process ---------->

        sessionID = InputManager.define_string("Please enter your account ID: ")                          #Enters the user ID you want to log in.


        self.start_socket()                                                                             #Starts socket
        sessionPassword = sha256(InputManager.define_string(message="Please enter your password: ", infLimit=6, supLimit=30).encode()).hexdigest()   #Enters password, and it gets hashed and converted into hexadecimal.
        
        transactionType = "verifyPassword"                                                              #Defines transaction type.
        self.sock.send(transactionType.encode())                                                        #Encodes transaction type string and sends it to server.

        profileData = {"ID": sessionID, "Password": sessionPassword }                                   #Prepares profile data into hashMap.
        data = json.dumps(profileData)                                                                  #Converts hashmap into json format string.
        time.sleep(1)                                                                                   #Sets 1 second delay for preventing joining bytes packages in server reception.
        self.sock.send(data.encode())                                                                   #Encodes json and sends it to server.

        transactionResult = self.sock.recv(1024).decode()                                               #Awaits for server response.

        self.stop_socket()                                                                              #Disconnects socket.
        # print(transactionResult)
        if transactionResult == "False":                                                                #If the password is wrong, it returns and displays a message.
            InputManager.display_message("The password for this account is incorrect, please try again!")
            return False
        else:                                                                                           #If the password is correct, it stores the user ID as the sessionID and the password.
            self.sessionID = sessionID
            self.sessionPassword = sessionPassword
            return True

    def get_user_data(self):                                                                            #<---------- Gets current logged user data from server ---------->
        self.start_socket()                                                                             #Starts socket.

        transactionType = "getUserData"                                                                 #Defines transaction type.
        self.sock.send(transactionType.encode())                                                        #Encondes transaction type string, and sends it to server.

        time.sleep(1)                                                                                   #Sets 1 second delay for preventing joining bytes packages in server reception.
        self.sock.send(self.sessionID.encode())                                                         #Sends ID of current logged user.

        transactionResult = self.sock.recv(1024).decode()                                               #Awaits for receiving transaction result.
        self.stop_socket()                                                                              #Disconnects socket.
        self.sessionData = json.loads(transactionResult)                                                #Transforms json data received from server into a hashMap.

        self.sessionName = self.sessionData["Name"]                                                     #Defines name of the curent logged user.
        self.sessionAge = self.sessionData["Age"]                                                       #Defines age of the curent logged user.
        self.sessionSex = self.sessionData["Sex"]                                                       #Defines sex of the curent logged user.
        self.sessionBalance = self.sessionData["Balance"]                                               #Defines balance of the curent logged user.


    def main_menu(self):                                                                                    #<---------- Main menu for logged users ---------->
        def display_balance():                                                                              #Displays the balance of the current logged user.
            InputManager.display_message(message=f"Your current balance is: {self.sessionBalance}")

        def display_account_data():                                                                         #Displays all the available data of the current logged user.
            print("")                                                                                       
            print(f"Your registered ID is   : {self.sessionID}")
            print(f"Your registered Name is : {self.sessionName}")
            print(f"Your registered Age is  : {self.sessionAge}")
            print(f"Your registered Sex is  : {self.sessionSex}")
            print(f"Your current Balance is : {self.sessionBalance}")
            InputManager.display_message(message="")

        def validate_balance(amount):                                                                       #<---------- Validates if the current balance of the logged user is sufficient for amount sent as parameter.
            return amount <= self.sessionBalance

        def send_payment():                                                                                 #Initializes the process for sending a payment to another user.
                                                                                                            # <------------- Starts existence of user verification ------------->
            self.start_socket()                                                                                 #Starts socket.
            receptorID = InputManager.define_string("Please enter the receptor ID: ")                            #Enters the receptor ID.
            
            transactionType = "verifyUser"                                                                      #Defines transaction type.
            self.sock.send(transactionType.encode())                                                            #Encodes string, and sends it to server.

            time.sleep(1)                                                                                       #Sets 1 second delay for preventing joining bytes packages in server reception.
            self.sock.send(receptorID.encode())                                                                 #Encondes the receptor ID, and sends it to server.
            transactionResult = self.sock.recv(1024).decode()                                                   #Waits and receives the server response if the account is registered or not.
            # print(transactionResult)
            self.stop_socket()                                                                                  #Disconnects socket.
            if transactionResult == "False":                                                                    #If the account doesn't exists, returns and displays message.
                InputManager.display_message(f"This account ID '{receptorID}' doesn't exists")
                return                                                                                       # <------------- Finishes existence of user verification ------------->

            print(f"You currently have ${self.sessionBalance}")                                              #Displays current blanace.
            sendingAmount = InputManager.define_numbers(message="Enter the amount you want to send: ", infLimit = 1, typeOfNumber = float)   #Enters the sending amount.
            approvalFlag = validate_balance(sendingAmount)                                                   #Validates and returns if the logged user has the sufficient balance for a deposit.
            if not approvalFlag:                                                                             #If it doesn't, it returns and displays message.
                InputManager.display_message("You dont have enough money.")
                return
            
            data = {"Sender": self.sessionID, "Receptor": receptorID, "Amount": sendingAmount}               #Prepares the data in json format.
            data = json.dumps(data)                                                                          #Transforms json into string.

            self.start_socket()                                                                             #Starts socket.

            transactionType = "makeDeposit"                                                                 #Defines transaction type.
            self.sock.send(transactionType.encode())                                                        #Sends transaction type to server.

            time.sleep(1)                                                                                   #Sets 1 second delay for preventing joining bytes packages in server reception.  
            self.sock.send(data.encode())                                                                   #Sends data to server.

            transactionResult = self.sock.recv(1024).decode()                                               #Awaits for receiving transaction result.

            self.stop_socket()                                                                              #Disconnects socket.
            
            self.sessionBalance -= sendingAmount                                                            #Updates the balance stored in the client.

            InputManager.display_message(f"Transaction result: {transactionResult}")                        #Displays transaction result.








        self.get_user_data()
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
            selectedOption = InputManager.define_numbers(message="Type a number according to your selected option: ", infLimit = 1, supLimit = 4,typeOfNumber = int)
            if selectedOption == 4:
                break
            
            if selectedOption == 1:
                display_balance()
            
            if selectedOption == 2:
                send_payment()

            if selectedOption == 3:
                display_account_data()



    def initialize_client(self):                                                    #Initializes the client.

        while True:                                                                 #Main loop that runs the client console menu.
            print("")
            print("*****************************************************")
            print("WELCOME TO THE PYTHON BANK P2P SERVICE")
            print("")
            print("1) Log in")                                                      #Option for log in into your account by typing 1.
            print("2) Create account")                                              #Option for creating an account by typing 2.
            print("3) Exit")                                                        #Option for exiting the menu by typing 3.
            print("")
            print("*****************************************************")
            selectedOption = InputManager.define_numbers(message="Type a number according to your selected option: ", infLimit = 1, supLimit = 3,typeOfNumber = int) #Calls InputManager function for entering a bounded number and repeating until the number is accepted.
            if selectedOption == 3:                                                 #What it executes when you exit the menu.
                print()
                print("THANKS FOR USING THE PYTHON BANK P2P SERVICE")
                print()
                break                                                               #Breaks the main loop and exits the program.
            if selectedOption == 1:                                                 #Executes what you need to log in into your account.
                logFlag = self.log_in()                                             #Calls the log in service, if is successful returns 'True' else returns 'False'.
                if logFlag:                                                         #If the log in service is successful, call the main logged menu.
                    self.main_menu()

            if selectedOption == 2:                                                 #Executes the necessary for creating an account.
                self.create_account()                                               #Calls the create account service.

            
    



if __name__ == "__main__":          #What is going to be executed when the client runs.
    client = Client()               #Creates an object from the 'Client' class.
    client.initialize_client()      #Initializes client.