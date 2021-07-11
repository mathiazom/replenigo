# Credentials for authorization, see https://sbanken.no/bruke/utviklerportalen/
CLIENT_ID = ""
SECRET = ""

# Account to provide refills
SOURCE_ACCOUNT_ID = ""

# Transfer message must be at least 1 and at most 30 characters
TRANSFER_MESSAGE = ""

# Can contain any number of tuples on the form `(destination_account_id: str, refill_goal: int)`
REFILL_GOALS = []

# If true, a refill request where the destination balance is above goal will result in transferring
# the surplus to the original source account. If false, such a refill request will be ignored.
REVERSE_IF_ABOVE_GOAL = False
