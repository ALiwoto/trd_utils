from decimal import Decimal
from trd_utils.types_helper import BaseModel
from trd_utils.types_helper.decorators import map_json_fields

PERFORMANCE_BASE = Decimal(100)
NUMERIC_PREFIXES = ("1000000", "100000", "10000", "1000", "100")


@map_json_fields(
    field_map={
        "market" + "cap": "market_cap",
    }
)
class Bubbles1kSingleInfo(BaseModel):
    id: str = None
    name: str = None
    slug: str = None
    symbol: str = None
    dominance: Decimal = None
    image: str = None
    rank: int = None
    stable: bool = None
    price: Decimal = None
    market_cap: Decimal = None
    volume: Decimal = None
    cg_id: str = None
    symbols: dict[str, str] = None
    performance: dict[str, Decimal] = None
    rank_diffs: dict[str, int] = None
    exchange_prices: dict[str, Decimal] = None

    def get_monthly_change(self) -> Decimal | None:
        """
        Returns the normalized monthly change percentage if available.
        Please note that 1.0 means +100%, -1.0 means -100%, 0.5 means +50%, etc.
        """
        return self.get_normalized_change("month")

    def get_3months_change(self) -> Decimal | None:
        """
        Returns the normalized 3 months change percentage if available.
        Please note that 1.0 means +100%, -1.0 means -100%, 0.5 means +50%, etc.
        """
        return self.get_normalized_change("month3")

    def get_1minute_change(self) -> Decimal | None:
        """
        Returns the normalized 1 minute change percentage if available.
        Please note that 1.0 means +100%, -1.0 means -100%, 0.5 means +50%, etc.
        """
        return self.get_normalized_change("min1")

    def get_weekly_change(self) -> Decimal | None:
        """
        Returns the normalized weekly change percentage if available.
        Please note that 1.0 means +100%, -1.0 means -100%, 0.5 means +50%, etc.
        """
        return self.get_normalized_change("week")

    def get_4hour_change(self) -> Decimal | None:
        """
        Returns the normalized 4 hour change percentage if available.
        Please note that 1.0 means +100%, -1.0 means -100%, 0.5 means +50%, etc.
        """
        return self.get_normalized_change("hour4")

    def get_yearly_change(self) -> Decimal | None:
        """
        Returns the normalized yearly change percentage if available.
        Please note that 1.0 means +100%, -1.0 means -100%, 0.5 means +50%, etc.
        """
        return self.get_normalized_change("year")

    def get_hourly_change(self) -> Decimal | None:
        """
        Returns the normalized 1 hour change percentage if available.
        Please note that 1.0 means +100%, -1.0 means -100%, 0.5 means +50%, etc.
        """
        return self.get_normalized_change("hour")

    def get_daily_change(self) -> Decimal | None:
        """
        Returns the normalized daily change percentage if available.
        Please note that 1.0 means +100%, -1.0 means -100%, 0.5 means +50%, etc.
        """
        return self.get_normalized_change("day")

    def get_normalized_change(self, period: str) -> Decimal | None:
        """
        Returns the normalized change percentage for the specific period if available.
        Please note that 1.0 means +100%, -1.0 means -100%, 0.5 means +50%, etc.
        Supported periods are: "1h", "24h", "week", "month", "3months", "6months", "year", "ytd"
        """
        if self.performance and period in self.performance:
            return self.performance[period] / PERFORMANCE_BASE
        return None

    def __str__(self) -> str:
        perf_str = ""
        if self.performance:
            perf_str = " | " + ", ".join(
                f"{k}: {v:+.2f}%" for k, v in self.performance.items() if v is not None
            )

        price_str = f"${self.price:,.4f}" if self.price else "N/A"
        m_cap_str = f"${self.market_cap:,.0f}" if self.market_cap else "N/A"
        vol_str = f"${self.volume:,.0f}" if self.volume else "N/A"
        dom_str = f"{(self.dominance * 100):.2f}%" if self.dominance else "N/A"

        return (
            f"#{self.rank or '?'} {self.symbol or '???'} ({self.name or 'Unknown'}); "
            f"Price: {price_str} | MCap: {m_cap_str} | Vol: {vol_str}; "
            f"Dominance: {dom_str}{perf_str}"
        )

    def __repr__(self):
        return self.__str__()


class BubblesTop1kCollection(BaseModel):
    data: list[Bubbles1kSingleInfo] = None
    _symbol_index: dict[str, Bubbles1kSingleInfo] = None

    def _build_index(self) -> None:
        """Build index once for O(1) lookups instead of O(n) loops"""
        if self._symbol_index is not None:
            return
        
        self._symbol_index = {}
        if not self.data:
            return
        
        for info in self.data:
            sym_lower = info.symbol.lower()
            self._symbol_index[sym_lower] = info
    
    @classmethod
    def _strip_prefix(self, symbol_lower: str, original: str = None) -> str:
        """Remove exchange multiplier prefixes like 1000000, k, etc."""
        original = original or symbol_lower
        
        # numeric prefixes (1000000MOG -> mog)
        for prefix in NUMERIC_PREFIXES:
            if symbol_lower.startswith(prefix):
                return symbol_lower[len(prefix):]
        
        # letter prefix k/K (kPEPE -> pepe)
        # only strip if lowercase k/m followed by uppercase (to avoid stripping KAVA -> AVA)
        if len(original) > 1 and original[0].lower() in 'km' and original[1].isupper():
            return symbol_lower[1:]
        
        return symbol_lower

    def try_find_by_symbol(self, symbol: str) -> Bubbles1kSingleInfo | None:
        """
        Try to find symbol with normalization for exchange prefixes.
        Handles: 1000000MOG, kPEPE, 10000SATS, etc.
        """
        self._build_index()
        
        if not self._symbol_index:
            return None
        
        sym_lower = symbol.lower()
        
        # 1. exact match (fast path)
        if sym_lower in self._symbol_index:
            return self._symbol_index[sym_lower]
        
        # 2. try with prefix stripped
        stripped = self._strip_prefix(sym_lower, symbol)
        if stripped != sym_lower and stripped in self._symbol_index:
            return self._symbol_index[stripped]
        
        return None

    def find_by_symbol(self, symbol: str) -> Bubbles1kSingleInfo | None:
        for bubble_info in self.data:
            if bubble_info.symbol.lower() == symbol.lower():
                return bubble_info
        return None

    def __str__(self) -> str:
        return f"BubblesTop1kCollection: total assets: {len(self.data)}"

    def __repr__(self) -> str:
        return self.__str__()
