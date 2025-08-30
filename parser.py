from ast import *

class Parser:
    def __init__(self):
        # Use dicts for fast lookup by name
        self.signals: dict[str, Signal] = {}
        self.fields: dict[str, Field] = {}
        self.consts: dict[str, Const] = {}
        self.groups: dict[str, Group] = {}

        # defaults and patterns can repeat → keep as lists
        self.defaults: list[Assignment] = []
        self.patterns: list[Pattern] = []

    def parse(self, tokens):
        self.pointer = 0
        self.tokens = tokens

        while not self.at_end():
            token = self.peek()
            if token.type == 'SIGNAL':
                self.parse_signal()
            elif token.type == 'FIELD':
                self.parse_field()
            elif token.type == 'CONST':
                self.parse_const()
            elif token.type == 'DEFAULT':
                self.parse_default()
            elif token.type == 'GROUP':
                self.parse_group()
            elif token.type == 'PATTERN':
                self.parse_pattern()
            elif token.type == 'EOF':
                break
            else:
                raise SyntaxError(f"Unexpected token: {token}")

        return self

    def parse_signal(self):
        self.expect("SIGNAL")
        name = self.expect("IDENT").value
        self.expect("COLON")
        bitpos = int(self.expect("NUMBER").value)
        self.expect("SEMICOL")
        self.signals[name] = Signal(name, bitpos)

    def parse_field(self):
        self.expect("FIELD")
        name = self.expect("IDENT").value
        self.expect("COLON")
        self.expect("LBRACKET")
        msb = int(self.expect("NUMBER").value)
        self.expect("COLON")
        lsb = int(self.expect("NUMBER").value)
        self.expect("RBRACKET")
        self.expect("SEMICOL")
        self.fields[name] = Field(name, smb, lsb)

    def parse_const(self):
        self.expect("CONST")
        name = self.expect("IDENT").value
        self.expect("ASSIGN")
        value_token = self.advance()
        if value_token.type == "NUMBER":
            value = int(value_token.value, 10)
        elif value_token.type == "BIN_NUMBER":
            value = int(value_token.value, 2)
        elif value_token.type == "HEX_NUMBER":
            value = int(value_token.value, 16)
        else:
            raise SyntaxError(f"Unexpected const value {value_token.type}")
        self.expect("SEMICOL")
        self.consts[name] = Const(name, value)

    def parse_default(self):
        self.expect("DEFAULT")
        self.expect("LBRACE")
        while self.peek().type != "RBRACE":
            name = self.expect("IDENT").value
            if self.peek().kind == "COLON":
                self.advance()
                value_token = self.advance()
                if value_token.type in ("NUMBER", "BIN_NUMBER", "HEX_NUMBER", "IDENT"):
                    value = value_token.value
                else:
                    raise SyntaxError(f"Invalid default assignment {value_token}")
                self.expect("SEMICOL")
                self.defaults.append(Assignment(name,value))
            else:
                self.expect("SEMICOL")
                self.defaults.append(Assignment(name, is_signal=True))
        self.expect("RBRACE")

    def parse_group(self):
        self.expect("GROUP")
        name = self.expect("IDENT").value

        pattern = self.parse_pattern_expr()

        self.expect("LBRACE")
        assigns = []
        
        while self.peek().type != "RBRACE":
            target = self.expect("IDENT").value
            if self.peek().type == "COLON":
                self.advance()
                value_token = self.advance()
                assigns.append(("field", target, value_token.value))
                self.expect("SEMICOL")
            else:
                assigns.append(("signal", target, true))
                self.expect("SEMICOL")
        self.expect("RBRACE")

        group = Group(name, bitpattern, assignments)
        self.groups[name] = group

    def parse_pattern_expr(self):
        parts = []
        if self.peek().type == "PATTERN_STR":
            token = self.advance()
            return token.value.strip('"')

        while not self.at_end():
            token = self.peek()
            if token.type == "NUMBER":
                parts.append(self.advance().value)
                continue
            if token.type == "LBRACE":
                if (
                        self.tokens[self.pointer + 1].type == "IDENT"
                        and self.tokens[self.pointer + 2].type == "COLON"
                        and self.tokens[self.pointer + 3].type == "NUMBER"
                        and self.tokens[self.pointer + 4].type == "RBRACE"
                ):
                    self.expect("LBRACE")
                    name = self.expect("IDENT").value
                    self.expect("COLON")
                    width = self.expect("NUMBER").value
                    self.expect("RBRACE")
                    parts.append(f"{{{name}:{width}}}")
                    continue
                else:
                    break
                break
            return "".join(parts)

    def parse_pattern(self):
        self.expect("PATTERN")
        token = self.advance()
        if token.type == "PATTERN_STR"

    def at_end(self):
        return self.pointer >= len(self.tokens)

    def peek(self):
        return self.tokens[self.pointer]

    def advance(self):
        token = self.tokens[self.pointer]
        self.pointer = self.pointer + 1
        return token
    
    def expect(self, kind):
        token = self.advance()
        if token.type != kind:
            return SyntaxError(f"Expected {kind}, got {token.type} at line {token.line}")
        return token
