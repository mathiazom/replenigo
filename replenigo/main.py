import datetime
import os
from pathlib import Path
from typing import Optional

import typer
from rich.progress import Progress, TimeElapsedColumn, TextColumn, BarColumn

from .config import config_from_stream
from .session import create_auth_session
from .utils import *

API_BASE_URL = "https://publicapi.sbanken.no/apibeta/api/v2"

app = typer.Typer()


def get_customer_name(auth_session):
    data = auth_session.get(
        f"{API_BASE_URL}/Customers/",
    ).json()
    return f"{data['firstName']} {data['lastName']}"


def get_account(auth_session, account_id):
    return auth_session.get(
        f"{API_BASE_URL}/Accounts/{account_id}",
    ).json()


def log_account_details(auth_session, destination_account, source_account):
    destination_account = get_account(auth_session, destination_account['accountId'])
    log_muted(f"...'{destination_account['name']}' is at {fmt_currency(destination_account['available'])}")
    source_account = get_account(auth_session, source_account['accountId'])
    log_muted(f"...'{source_account['name']}' is at {fmt_currency(source_account['available'])}")


def transfer(auth_session, from_account_id, to_account_id, amount, message):
    return auth_session.post(
        f"{API_BASE_URL}/Transfers",
        headers={'content-type': 'application/json'},
        json={
            "FromAccountId": from_account_id,
            "ToAccountId": to_account_id,
            "Message": message[:30],
            "Amount": amount
        }
    )


def refill_account(auth_session, destination_account, source_account, refill_goal, reverse_if_above_goal,
                   transfer_message):
    """
    Transfer required amount from source account to destination account
    so that the resulting available balance satisfies refill goal.
    """
    print(f"Requesting refill of '{destination_account['name']}'")

    if refill_goal < 0:
        log_error(f"...refill goal must be non-negative, was {refill_goal}")
        log_error("...aborted.")
        return False

    log_info(f"...the goal is {fmt_currency(refill_goal)}")
    destination_available_balance = destination_account['available']
    log_info(f"...current available balance is {fmt_currency(destination_available_balance)}")
    above_goal = refill_goal < destination_available_balance

    # Use string representation for transfer_amount to get correct precision
    transfer_amount = '%.2f' % (abs(refill_goal - destination_available_balance))

    if float(transfer_amount) == 0:
        log_special(f"...already at the right balance")
        log_special(f"...no further action.")
        return True

    log_info(f"...need to {'skim' if above_goal else 'transfer'} {fmt_currency(transfer_amount)}")

    # Make sure amount is above documented transfer minimum of 1.0
    if float(transfer_amount) <= 1:
        log_error(f"...transfer amount must be greater than {fmt_currency(1)}")
        log_error("...aborted.")
        return False

    # Comfortably ignoring the documented transfer maximum of 100000000000000000

    if above_goal:
        if reverse_if_above_goal:
            # Reverse transfer, in effect "skimming" the surplus
            log_info(f"...performing the ol' switcheroo")
            destination_account, source_account = source_account, destination_account
            log_info(f"...now sourcing from '{source_account['name']}' and topping up '{destination_account['name']}'")
        else:
            log_special(f"...but reverse_if_above_goal=False")
            log_special(f"...no further action.")
            return True
    else:
        source_available_balance = source_account['available']
        log_info(f"...sourcing from '{source_account['name']}' at {fmt_currency(source_available_balance)}")
        if float(source_available_balance) < float(transfer_amount):
            log_error("...insufficient funds, aborted.")
            return False

    with Progress(TextColumn("[progress.description]{task.description}"),
                  BarColumn(),
                  TimeElapsedColumn()) as progress:
        refill_task = progress.add_task("...transferring", total=None)  # total=None for indeterminate
        response = transfer(auth_session, source_account['accountId'], destination_account['accountId'],
                            transfer_amount, transfer_message)
        if response.status_code != 204:
            progress.stop()
            log_error("...an error occurred.")
            log_error(response.text)
            return False
        progress.update(refill_task, total=0)  # Set total to show indeterminate as completed

    log_success("...success!")
    return True


# Create an empty file to mark a successful refill
# This can be used when scheduling refills to recover from a missed refill
# (for example the server was off at the target date, but turned on a few days later)
def write_checkpoint_file(directory: Path):
    os.makedirs(directory, exist_ok=True)
    # Simply write to file before immediately closing it
    open(directory / str(datetime.date.today().isoformat()), "w").close()


@app.command()
def refill(
        config_stream: typer.FileText = typer.Option(
            "replenigo.yaml",
            "--config-file", "-c",
            encoding="utf-8",
            help="Configurations file"
        ),
        reverse_if_above_goal: Optional[bool] = typer.Option(
            None,
            "--reverse-if-above-goal/--no-reverse-if-above-goal", "-r/-R",
            show_default=False,
            help="If refill goal has been exceeded, decide if the surplus should be transferred back to "
                 "the source account"
        ),
        transfer_message: Optional[str] = typer.Option(
            None,
            "--transfer-message", "-m",
            show_default=False,
            help="Message to be displayed in the bank transfer (max 30 chars)"
        ),
        write_checkpoints: Optional[bool] = typer.Option(
            None,
            "--write-checkpoints/--no-checkpoints", "-p/-P",
            help="Enable or disable \"checkpointing\", which creates an empty checkpoint file on each "
                 "successful refill"
        ),
        checkpoints_dir: Optional[Path] = typer.Option(
            None,
            "--checkpoints-dir", "-d",
            file_okay=False,
            writable=True,
            help="Directory to store checkpoint files"
        )
):
    """
    Refill accounts to specified balances
    """
    config = config_from_stream(config_stream)
    session = create_auth_session(config["auth"]["client_id"], config["auth"]["client_secret"])
    log_special(f"Authorized as {get_customer_name(session)}. Welcome!")
    source_account = get_account(session, config["source_account"])
    success_all = True
    for destination_account_id, refill_goal in config["refill_goals"].items():
        destination_account = get_account(session, destination_account_id)
        if reverse_if_above_goal is None:
            reverse_if_above_goal = config["reverse_if_above_goal"]
        if transfer_message is None:
            transfer_message = config["transfer_message"]
        success = refill_account(session, destination_account, source_account, refill_goal, reverse_if_above_goal,
                                 transfer_message)
        success_all = success_all and success
        log_account_details(session, destination_account, source_account)
    if not success_all:
        log_error("[WARNING] Some refill requests could not be fulfilled")
        raise typer.Exit(code=1)
    if write_checkpoints is None:
        write_checkpoints = config["write_checkpoints"]
    if write_checkpoints:
        # All requests have been fulfilled, so mark the occasion!
        if checkpoints_dir is None:
            checkpoints_dir = Path(config["checkpoints_dir"])
        write_checkpoint_file(checkpoints_dir)


@app.callback()
def callback():
    """
    Script that utilizes Sbanken's Open Banking API to refill accounts to specified balances
    """
