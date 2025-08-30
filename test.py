#!/usr/bin/env python3

from lexer import Lexer

with open("syntax_example2.txt", "r") as file:
    content = file.read()

test_lexer = Lexer()
tokens = test_lexer.tokenize(content)

for token in tokens:
    print(f"{token.type:10} {token.value:15} line {token.line:2} col {token.column:2}")
