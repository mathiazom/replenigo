import datetime
import os

from session_config import session
from config import SOURCE_ACCOUNT_ID, REFILL_GOALS, TRANSFER_MESSAGE, REVERSE_IF_ABOVE_GOAL
from utils import *

API_BASE_URL = "https://publicapi.sbanken.no/apibeta/api/v2"

# Directory for storing 'successful refill' markers
CHECKPOINTS_DIR = "checkpoints"


def transfer(auth_session, from_account_id, to_account_id, amount):
    return auth_session.post(
        f"{API_BASE_URL}/Transfers",
        headers={'content-type': 'application/json'},
        json={
            "FromAccountId": from_account_id,
            "ToAccountId": to_account_id,
            "Message": TRANSFER_MESSAGE[:30],
            "Amount": amount
        }
    )


def get_customer_name(auth_session):
    data = auth_session.get(
        f"{API_BASE_URL}/Customers/",
    ).json()
    return f"{data['firstName']} {data['lastName']}"


def get_account(auth_session, account_id):
    return auth_session.get(
        f"{API_BASE_URL}/Accounts/{account_id}",
    ).json()


# Transfer required amount from source account to destination account
# so that the resulting available balance equals refill goal.
def refill_account(auth_session, destination_account, source_account, refill_goal):
    cinfo(f"Requesting refill of '{destination_account['name']}'")

    if refill_goal < 0:
        cerror(f"...refill goal must be nonnegative, was {refill_goal}")
        cerror("...aborted.")
        return False

    cinfo(f"...the goal is {fcurrency(refill_goal)}")
    destination_available_balance = destination_account['available']
    cinfo(f"...current available balance is {fcurrency(destination_available_balance)}")
    above_goal = refill_goal < destination_available_balance

    # Use string representation for transfer_amount to get correct precision
    transfer_amount = '%.2f' % (abs(refill_goal - destination_available_balance))

    if float(transfer_amount) == 0:
        cspecial(f"...already at the right balance")
        cspecial(f"...no further action.")
        return True

    cinfo(f"...need to {'skim' if above_goal else 'transfer'} {fcurrency(transfer_amount)}")

    # Make sure amount is above documented transfer minimum of 1.0
    if float(transfer_amount) <= 1:
        cerror(f"...transfer amount must be greater than {fcurrency(1)}")
        cerror("...aborted.")
        return False

    # Comfortably ignoring the documented transfer maximum of 100000000000000000

    if above_goal:
        if REVERSE_IF_ABOVE_GOAL:
            # Reverse transfer, in effect "skimming" the surplus
            cinfo(f"...performing the ol' switcheroo")
            destination_account, source_account = source_account, destination_account
            cinfo(f"...now sourcing from '{source_account['name']}' and topping up '{destination_account['name']}'")
        else:
            cspecial(f"...but REVERSE_IF_ABOVE_GOAL=False")
            cspecial(f"...no further action.")
            return True
    else:
        source_available_balance = source_account['available']
        cinfo(f"...sourcing from '{source_account['name']}' at {fcurrency(source_available_balance)}")
        if float(source_available_balance) < float(transfer_amount):
            cerror("...insufficient funds, aborted.")
            return False

    # Perform actual transfer
    response = transfer(auth_session, source_account['accountId'], destination_account['accountId'],
                        transfer_amount)

    if response.status_code != 204:
        cerror("...an error occured.")
        cerror(response.text)
        return False

    csuccess("...success!")
    return True


# Create an empty file to mark a successful refill
# This can be used when scheduling refills to recover from a missed refill
# (for example the server was off at the target date, but turned on a few days later)
def write_checkpoint_file():
    if not os.path.isdir(CHECKPOINTS_DIR):
        os.mkdir(CHECKPOINTS_DIR)
    # Simply write to file before immediately closing it
    open(f"{CHECKPOINTS_DIR}/{str(datetime.date.today().isoformat())}", "w").close()


def log_account_details(auth_session, destination_account, source_account):
    destination_account = get_account(auth_session, destination_account['accountId'])
    cmuted(f"...'{destination_account['name']}' is at {fcurrency(destination_account['available'])}")
    source_account = get_account(auth_session, source_account['accountId'])
    cmuted(f"...'{source_account['name']}' is at {fcurrency(source_account['available'])}")


def main():
    cspecial(f"Authorized as {get_customer_name(session)}. Welcome!")
    source_account = get_account(session, SOURCE_ACCOUNT_ID)
    success = True
    for destination_account_id, refill_goal in REFILL_GOALS:
        destination_account = get_account(session, destination_account_id)
        success = success and refill_account(session, destination_account, source_account, refill_goal)
        log_account_details(session, destination_account, source_account)
    if success:
        # All requests have been fulfilled, so mark the occasion!
        write_checkpoint_file()
    else:
        cerror("WARNING: Some refill requests could not be fulfilled")


if __name__ == "__main__":
    main()
