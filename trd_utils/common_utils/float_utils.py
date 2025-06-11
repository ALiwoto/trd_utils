
from decimal import Decimal


default_quantize = Decimal("1.00")

def dec_to_str(dec_value: Decimal) -> str:
    return format(dec_value.quantize(default_quantize), "f")

def dec_to_normalize(dec_value: Decimal) -> str:
    return format(dec_value.normalize(), "f")