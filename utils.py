from termcolor import cprint, colored


def cspecial(x): cprint(x, 'cyan')


def cinfo(x): cprint(x, 'white')


def cmuted(x): cprint(x, 'white', attrs=['dark'])


def csuccess(x): cprint(x, 'green')


def cerror(x): cprint(x, 'red')


# Format float string to use space as thousands separator and comma as decimal separator
# (aka Norwegian style but without requiring the correct locale to be installed...)
# (see https://www.python.org/dev/peps/pep-0378/)
def fcurrency(s):
    return colored(
        format(float(s), ",.2f").replace(",", " ").replace(".", ",") + " kr",
        attrs=["bold"]
    )
