


class ExchangeError(RuntimeError):
    """
    Specifies an error coming from the exchange.
    """
    def __init__(self, *args):
        super().__init__(*args)

