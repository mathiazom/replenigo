# Usage

* Requires Python 3

* Install required packages with a virtual environment (here named `ludwig`)
```shell
$ python -m venv ludwig
$ source ludwig/bin/activate
(ludwig) $ pip install -r requirements.txt
```

* Use `.env.dist` as template to create your own `.env` file with the required credentials as environment variables `CLIENTID`(*Applikasjonsnøkkel*) and `SECRET`(*Passord*). See https://secure.sbanken.no/Personal/ApiBeta/Info.
```shell
CLIENTID="<your-client-id>"
SECRET="<your-secret>"
```

* Use `refill_params.py.dist` as template to create your own `refill_params.py` file with source account and refill parameters
```shell
SOURCE_ACCOUNT = "<source-account-id>"
TRANSFER_MESSAGE = "<useful-message-within-30-chars>"
REFILL_PARAMS = [
    # account_id : refill_limit
    ("<first-account-id>", <first-refill-limit>),
    ("<second-account-id>", <second-refill-limit>),
    ...
]
```
>example
>```shell
>SOURCE_ACCOUNT = "FCB87IYT37R20BC387RTR3B8FCGFC87"
>TRANSFER_MESSAGE = "Påfyll via hjemmesnekret app"
>REFILL_PARAMS = [
>    # account_id : refill_limit
>    ("72387TBT92VV3RV3RVF3", 7000),
>    ("TV82940V70T4C27048TR", 5000),
>    ...
>]
>```
> to find account id, see https://publicapi.sbanken.no/openapi/apibeta/index.html#/Accounts/Accounts_List

* Run the app:
```shell
(ludwig) $ python refill_app.py
```
