from typing import Protocol, Union, Any
from dataclasses import dataclass

class Algebraic(Protocol):
    def __add__(self, other: Any) -> "Algebraic": ...
    def __sub__(self, other: Any) -> "Algebraic": ...
    def __mul__(self, other: Any) -> "Algebraic": ...
    def __len__(self) -> int: ...
    def __lt__(self, other: Any) -> bool: ...
    def __gt__(self, other: Any) -> bool: ...
    
    # [PROTOCOL] The Matter Interface
    @property
    def mass(self) -> int: ...
    @property
    def is_vacuum(self) -> bool: ...

@dataclass(frozen=True)
class NonNegativeInteger:
    value: str
    def __post_init__(self):
        if not set(self.value).issubset({'|'}):
            raise ValueError("Base-1 data must only contain '|'")
            
    # [PROTOCOL] Physics Mode: Mass is Length
    @property
    def mass(self) -> int: return len(self.value)
    @property
    def is_vacuum(self) -> bool: return len(self.value) == 0

    def __len__(self) -> int: return len(self.value)
    def __int__(self) -> int: return len(self)
    def __repr__(self) -> str: return f"U({int(self)})"
    def __str__(self) -> str: return str(int(self))
    
    def __add__(self, other: Any) -> "Algebraic": return smart_add(self, other)
    
    def __sub__(self, other: Any) -> "Algebraic":
        minus_one = NegativeInteger("|")
        return self + (other * minus_one)
        
    def __mul__(self, other: Any) -> "Algebraic": return smart_mul(self, other)
    def __truediv__(self, other: Any) -> tuple["Algebraic", "Algebraic"]: return smart_div(self, other)

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, NonNegativeInteger): return len(self) < len(other)
        if isinstance(other, NegativeInteger): return False 
        return NotImplemented

    def __le__(self, other: Any) -> bool:
        if isinstance(other, NonNegativeInteger): return len(self) <= len(other)
        if isinstance(other, NegativeInteger): return False
        return NotImplemented

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, NonNegativeInteger): return len(self) > len(other)
        if isinstance(other, NegativeInteger): return True 
        return NotImplemented

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, NonNegativeInteger): return len(self) >= len(other)
        if isinstance(other, NegativeInteger): return True
        return NotImplemented

@dataclass(frozen=True)
class NegativeInteger:
    value: str
    def __post_init__(self):
        if not set(self.value).issubset({'|'}):
            raise ValueError("Base-1 data must only contain '|'")

    # [PROTOCOL] Physics Mode: Mass is Length
    @property
    def mass(self) -> int: return len(self.value)
    @property
    def is_vacuum(self) -> bool: return len(self.value) == 0

    def __len__(self) -> int: return len(self.value)
    def __int__(self) -> int: return -1 * len(self)
    def __repr__(self) -> str: return f"S({int(self)})"
    def __str__(self) -> str: return f"{int(self)}"
    
    def __call__(self, input_data: NonNegativeInteger) -> Union[NonNegativeInteger, "NegativeInteger",]:
        data_len = len(input_data)
        if data_len >= len(self.value): return NonNegativeInteger("|" * (data_len - len(self.value)))
        else: return NegativeInteger("|" * (len(self.value) - data_len))
        
    def __add__(self, other: Any) -> "Algebraic": return smart_add(self, other)
    
    def __sub__(self, other: Any) -> "Algebraic":
        minus_one = NegativeInteger("|")
        return self + (other * minus_one)
        
    def __mul__(self, other: Any) -> "Algebraic": return smart_mul(self, other)
    def __truediv__(self, other: Any) -> tuple["Algebraic", "Algebraic"]: return smart_div(self, other)

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, NonNegativeInteger): return True 
        if isinstance(other, NegativeInteger): return len(self) > len(other) 
        return NotImplemented

    def __le__(self, other: Any) -> bool:
        if isinstance(other, NonNegativeInteger): return True
        if isinstance(other, NegativeInteger): return len(self) >= len(other)
        return NotImplemented

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, NonNegativeInteger): return False
        if isinstance(other, NegativeInteger): return len(self) < len(other) 
        return NotImplemented

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, NonNegativeInteger): return False
        if isinstance(other, NegativeInteger): return len(self) <= len(other)
        return NotImplemented

Integer = Union[NegativeInteger, NonNegativeInteger]

def U(n: int) -> "NonNegativeInteger":
    if n < 0: raise ValueError("U() is for non-negative integers only")
    return NonNegativeInteger("|" * n)

def S(n: int) -> "NegativeInteger":
    if n < 0: raise ValueError("S() magnitude must be positive")
    return NegativeInteger("|" * n)

def smart_add(a: Integer, b: Integer) -> Integer:
    match (a, b):
        case (NonNegativeInteger(), NonNegativeInteger()): return NonNegativeInteger(a.value + b.value)
        case (NegativeInteger(), NegativeInteger()): return NegativeInteger(a.value + b.value)
        case (NonNegativeInteger(), NegativeInteger()): return b(a)
        case (NegativeInteger(), NonNegativeInteger()): return a(b)
        case _: return NotImplemented

def smart_mul(a: Integer, b: Integer) -> Integer:
    match (a, b):
        case (NonNegativeInteger(), NonNegativeInteger()): return NonNegativeInteger(a.value * len(b))
        case (NonNegativeInteger(), NegativeInteger()): return NegativeInteger(a.value * len(b))
        case (NegativeInteger(), NonNegativeInteger()): return NegativeInteger(a.value * len(b))
        case (NegativeInteger(), NegativeInteger()): return NonNegativeInteger(a.value * len(b))
        case _: return NotImplemented

def smart_div(a: Integer, b: Integer) -> tuple[Integer, Integer]:
    len_a = len(a)
    len_b = len(b)
    if len_b == 0: raise ZeroDivisionError("Cannot tile with an empty string.")
    q_mag = len_a // len_b
    r_mag = len_a % len_b
    q_str = "|" * q_mag
    r_str = "|" * r_mag
    if isinstance(a, type(b)): quotient = NonNegativeInteger(q_str)
    else: quotient = NegativeInteger(q_str)
    if isinstance(a, NonNegativeInteger): remainder = NonNegativeInteger(r_str)
    else: remainder = NegativeInteger(r_str)
    return (quotient, remainder)