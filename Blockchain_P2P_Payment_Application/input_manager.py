#MADE BY ALBERTO NAVARRETE
#DISTRIBUTION OF THIS LIBRARY IS PERMITED AS LONG AS CREDIT IS GIVEN
#YOU ARE NOT ALLOWED TO CREDIT YOURSELF AS OWNER/DEVELOPER OF THIS LIBRARY
#FOR MOR INFORMATION: https://www.linkedin.com/in/albertonr/

from typing import Iterable


class InputManager:

    def __init__(self):
        pass

    def is_number(number, typeOfNumber = int):
        try:
            if typeOfNumber == int:
                number = int(number)
            elif typeOfNumber == float:
                number = float(number)
            return number,True
        except ValueError:
            return number,False

    def display_message(message):
        print(f"\n{message}")
        input("\nPress Enter to continue\n")

    def define_numbers(message = "", messageKey="", infLimit = None, supLimit = None, quantity = 1,typeOfNumber= int, startKey = 0):

        numbers = []
        iter = 0
        while iter < quantity:
            if messageKey != "":
                displayMessage = message + f" [{messageKey} {iter + startKey}]: "
            else:
                displayMessage = message+" "
            number, isNumber = InputManager.is_number(input(displayMessage), typeOfNumber)

            if isNumber is not False: 
                if infLimit is not None and number < infLimit:
                    InputManager.display_message(f"Error, the value {number} must be greater than {infLimit}")
                    iter -= 1
                elif supLimit is not None and number > supLimit:
                    InputManager.display_message(f"Error, the value {number} must be smaller than {supLimit}")
                    iter -= 1
                else:
                    numbers.append(number)
            else:
                InputManager.display_message(f"Error, the value {number} is not an accepted element")
                iter -= 1

            iter += 1
        
        if len(numbers) != 1:
            return numbers
        else:
            return numbers[0]
    
    def define_string(message ="", infLimit = None, supLimit = None):
        while True:
            string = input(message+" ")
            if infLimit is not None and len(string) < infLimit:
                InputManager.display_message(f"Error, the length of '{string}' must be greater than {infLimit}")
            elif supLimit is not None and len(string) > supLimit:
                InputManager.display_message(f"Error, the length of '{string}' must be smaller than {supLimit}")
            else:
                return string

            



    


# <-------------------------------------- STARTS SIMPLE TESTING REGION -------------------------------------------->
# <-------------------------------------- STARTS SIMPLE TESTING REGION -------------------------------------------->
# <-------------------------------------- STARTS SIMPLE TESTING REGION -------------------------------------------->
if __name__ == "__main__":


    numeros = InputManager.define_numbers(message="Ingresa tu número", messageKey="Número",quantity=5, typeOfNumber=float)
    if isinstance(numeros,Iterable):
        for numero in numeros:
            print(f"Numero: {numero}")
    else:
        print(f"Numero: {numeros}")
# <--------------------------------------  ENDS SIMPLE TESTING REGION  -------------------------------------------->
# <--------------------------------------  ENDS SIMPLE TESTING REGION  -------------------------------------------->
# <--------------------------------------  ENDS SIMPLE TESTING REGION  -------------------------------------------->