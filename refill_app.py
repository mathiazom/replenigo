from termcolor import colored, cprint
cspecial = lambda x : cprint(x,'cyan')
cinfo = lambda x : cprint(x,'white')
cmuted = lambda x : cprint(x,'white', attrs=['dark'])
csuccess = lambda x : cprint(x,'green')
cerror = lambda x : cprint(x,'red')

# Currency formatting
import locale
locale.setlocale(locale.LC_ALL, "Norwegian")
fcurrency = lambda s : colored(locale.currency(float(s),grouping=True,symbol=False) + " kr",attrs=["bold"])

import requests
from decimal import Decimal
from session_conf import session
from refill_params import SOURCE_ACCOUNT_ID, REFILL_PARAMS, TRANSFER_MESSAGE

API_BASE_URL = "https://publicapi.sbanken.no/apibeta/api/v2"

def transfer(session, from_account_id, to_account_id, amount):
    return session.post(
        f"{API_BASE_URL}/Transfers",
        headers={'content-type':'application/json'},
        json={
          "FromAccountId": from_account_id,
          "ToAccountId": to_account_id,
          "Message": TRANSFER_MESSAGE[:30],
          "Amount": amount
        }
    )

def get_customer_name(session):
    data = session.get(
        f"{API_BASE_URL}/Customers/",
    ).json()
    return f"{data['firstName']} {data['lastName']}"

def get_account_info(session, account_id):
    return session.get(
        f"{API_BASE_URL}/Accounts/{account_id}",
    ).json()

# Transfer required amount from source_account_id to account_id so that
# resulting available balance equals refill_limit.
# (Use string representation for refill_amount to get correct precision)
def refill_account(session, destination_account, refill_limit, source_account):
    cinfo(f"Requesting refill of '{destination_account['name']}'")
    cinfo(f"...the goal is {fcurrency(refill_limit)}")
    if refill_goal < 0:
        cerror(f"...refill goal must be nonnegative, was {refill_goal}")
        cerror("...aborted.")
        return
    destination_available_balance = destination_account['available']
    cinfo(f"...current available balance is {fcurrency(destination_available_balance)}")
    above_limit = refill_limit < destination_available_balance
    transfer_amount = '%.2f'%(abs(refill_limit - destination_available_balance))
    if (float(transfer_amount) == 0):
        cspecial(f"...already at the right balance, no refill today.")
        return
    cinfo(f"...need to {'skim' if above_limit else 'transfer'} {fcurrency(transfer_amount)}")
    if (float(transfer_amount) <= 1):
        cerror(f"...transfer amount must be greater than {fcurrency(1)}")
        cerror("...aborted.")
        return
    # Comfortably ignoring the documented transfer max limit of 100000000000000000
    if (above_limit):
        cinfo(f"...performing the ol' switcheroo")
        cinfo(f"...now sourcing from '{destination_account['name']}' and topping up '{source_account['name']}'")
        response = transfer(session, destination_account['accountId'], source_account['accountId'], transfer_amount.replace("-",""))
    else:
        source_available_balance = source_account['available']
        cinfo(f"...sourcing from '{source_account['name']}' at {fcurrency(source_available_balance)}")
        if (float(source_available_balance) < float(transfer_amount)):
            cerror("...insufficient funds, aborted.")
            return
        response = transfer(session, source_account['accountId'], destination_account['accountId'], transfer_amount)
    if (response.status_code != 204):
        cerror("...an error occured.")
        cerror(response.text)
    else:
        csuccess("...success!")
    # Log updated account details
    destination_account = get_account_info(session, destination_account['accountId'])
    cmuted(f"...'{destination_account['name']}' is at {fcurrency(destination_account['available'])}")
    source_account = get_account_info(session, source_account['accountId'])
    cmuted(f"...'{source_account['name']}' is at {fcurrency(source_account['available'])}")

def main():
    cspecial(f"Authorized as {get_customer_name(session)}. Welcome!")
    source_account = get_account_info(session, SOURCE_ACCOUNT_ID)
    for destination_account_id, refill_limit in REFILL_PARAMS:
        destination_account = get_account_info(session, destination_account_id)
        refill_account(session, destination_account, refill_limit, source_account)

if __name__ == "__main__":
    main()
