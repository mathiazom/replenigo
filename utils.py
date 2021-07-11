from termcolor import cprint, colored
import locale

locale.setlocale(locale.LC_ALL, "Norwegian")


def cspecial(x): cprint(x, 'cyan')


def cinfo(x): cprint(x, 'white')


def cmuted(x): cprint(x, 'white', attrs=['dark'])


def csuccess(x): cprint(x, 'green')


def cerror(x): cprint(x, 'red')


# Format string to Norwegian currency
def fcurrency(s):
    return colored(
        locale.currency(float(s), grouping=True, symbol=False) + " kr",
        attrs=["bold"]
    )
