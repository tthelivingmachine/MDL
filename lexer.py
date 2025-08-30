import re
from collections import namedtuple

TOKEN_SPEC = [
    # Keywords
    ("PATTERN",     r"pattern\b"),
    ("SIGNAL",      r"signal\b"),
    ("FIELD",       r"field\b"),
    ("CONST",       r"const\b"),
    ("FOR",         r"for\b"),
    ("IN",          r"in\b"),
    ("GROUP",       r"group\b"),
    ("DEFAULT",     r"default\b"),

    # Literals
    ("PATTERN_STR", r'"[01{}:\-]+"'), # Pattern strings with 0,1,{},-
    ("BIN_NUMBER",  r"0b[01]+"),
    ("HEX_NUMBER",  r"0x[0-9A-Fa-f]+"),
    ("NUMBER",      r"\d+"),
    ("IDENT",       r"[A-Za-z_]\w*"),

    # Operators and delimiters
    ("COLON",       r":"),
    ("COMMA",       r","),
    ("LBRACE",      r"\{"),
    ("RBRACE",      r"\}"),
    ("LBRACKET",    r"\["),
    ("RBRACKET",    r"\]"),
    ("SEMICOL",     r";"),
    ("ASSIGN",      r"="),
    ("OR",          r"\|"),
    ("PLUS",        r"\+"),
    ("MINUS",       r"-"),
    ("MULT",        r"\*"),
    ("RANGE",       r"\.\."),

    # Whitespace and comments
    ("SKIP",        r"[ \t]+"),
    ("COMMENT",     r"//.*|/\*.*?\*/"),
    ("NEWLINE",     r"\n"),
]

Token = namedtuple('Token', ['type', 'value', 'line', 'column'])

class Lexer:
    def __init__(self):
        # Combine all regex patterns
        self.token_spec = TOKEN_SPEC
        self.keywords = {
            'pattern', 'signal', 'field', 'const', 'for', 'in', 'group', 'default'
        }

        # Create master regex
        self.regex = re.compile(
            '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_spec),
            re.MULTILINE | re.DOTALL
        )

    def tokenize(self, code):
        line_num = 1
        line_start = 0
        tokens = []

        for match in self.regex.finditer(code):
            kind = match.lastgroup
            value = match.group()
            column = match.start() - line_start

            if kind in ['SKIP', 'COMMENT']:
                continue
            elif kind == 'NEWLINE':
                line_start = match.end()
                line_num += 1
                continue
            elif kind == 'IDENT' and value in self.keywords:
                kind = value.upper()

            tokens.append(Token(kind, value, line_num, column))

        tokens.append(Token('EOF', '', line_num, 0))
        return tokens
