import pathlib
from pprint import pprint

from bind_lexer_sly import BindLexer
from bind_parser_sly import BindParser

if __name__ == '__main__':
    data = pathlib.Path('example_files/example_3.zone').read_text()
    # data = "boba.ru. 86400 IN A 1.2.3.4"

    lexer = BindLexer()
    tokens = lexer.tokenize(data)
    for tok in tokens:
        print('type=%r, value=%r' % (tok.type, tok.value))

    parser = BindParser()
    try:
        tokens = lexer.tokenize(data)
        print(f"{tokens=}")
        result = parser.parse(tokens)
        pprint(result)
    except EOFError:
        pass