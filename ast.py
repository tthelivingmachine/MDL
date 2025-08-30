
class Signal:
    def __init__(self, name: str, bitpos: int):
        self.name = name
        self.bitpos = bitpos

    def __repr__(self):
        return f"Signal({self.name}@{self.bitpos})"


class Field:
    def __init__(self, name: str, msb: int, lsb: int):
        self.name = name
        self.msb = msb
        self.lsb = lsb

    def __repr__(self):
        return f"Field({self.name}[{self.msb}:{self.lsb}])"


class Const:
    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Const({self.name}={self.value})"


class Assignment:
    """One entry inside pattern/group/default block"""
    def __init__(self, target: str, value=None, is_signal: bool = False):
        self.target = target
        self.value = value
        self.is_signal = is_signal

    def __repr__(self):
        if self.is_signal:
            return f"AssignSignal({self.target})"
        return f"AssignField({self.target}={self.value})"


class Group:
    def __init__(self, name: str, bitpattern: str, assignments=None):
        self.name = name
        self.bitpattern = bitpattern  # raw string like "10{op:3}{reg:3}"
        self.assignments = assignments or []

    def __repr__(self):
        return f"Group({self.name}, {self.bitpattern}, {self.assignments})"


class Pattern:
    def __init__(self, bitpattern: str = None, base_group: str = None, assignments=None):
        self.bitpattern = bitpattern      # e.g. "11000101"
        self.base_group = base_group      # e.g. "reg_op"
        self.assignments = assignments or []

    def __repr__(self):
        return f"Pattern(base={self.base_group}, bits={self.bitpattern}, assigns={self.assignments})"

