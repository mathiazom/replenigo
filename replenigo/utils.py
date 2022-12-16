from termcolor import cprint, colored


def log_special(x): cprint(x, 'cyan')


def log_info(x): cprint(x, 'white')


def log_muted(x): cprint(x, 'white', attrs=['dark'])


def log_success(x): cprint(x, 'green')


def log_error(x): cprint(x, 'red')


# Format float string to use space as thousands separator and comma as decimal separator
# (aka Norwegian style but without requiring the correct locale to be installed...)
# (see https://www.python.org/dev/peps/pep-0378/)
def fmt_currency(s):
    return colored(
        format(float(s), ",.2f").replace(",", " ").replace(".", ",") + " kr",
        attrs=["bold"]
    )
