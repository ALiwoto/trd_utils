"""
General usage wallet-related utils code.
"""


def shorten_wallet_address(
    address: str,
    start_chars: int = 7,
    end_chars: int = 6,
):
    """
    Shortens an Ethereum address by keeping a specific number of characters
    from the beginning and end, separated by '...'.

    Args:
        address (str): The Ethereum address to shorten
        start_chars (int): Number of characters to keep from the beginning (default: 7)
        end_chars (int): Number of characters to keep from the end (default: 6)

    Returns:
        str: The shortened address
    """
    if not address or len(address) <= start_chars + end_chars:
        return address

    return f"{address[:start_chars]}...{address[-end_chars:]}"
