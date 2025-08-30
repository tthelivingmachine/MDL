from lexer import Lexer

lex = Lexer()

with open("syntax_example.txt", "r") as file:
    content = file.read()

tokens = lex.tokenize(content)

for token in tokens:
    print(f"'{token.type}' : '{token.value}'    line: {token.line} col: {token.column}")
