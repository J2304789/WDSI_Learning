from stellar_base.horizon import Horizon

def data_handler(response):#Code to print out value for every ledger in ledger_data
    print(response)

def get_ledger_data():
    ledger_data=Horizon(horizon_uri='https://horizon.stellar.org')#Connects to Horizon Server for data
    ledger_data=ledger_data.ledgers(cursor="now",order="asc",sse=True)
    for ledger in ledger_data:
        data_handler(ledger)

#every ledger will start with "hello" and end with "byebye"
get_ledger_data()