import contextlib
import pathlib
from pprint import pprint

from bind_lexer_sly import BindLexer
from bind_parser_sly import BindParser

if __name__ == "__main__":
    for zone_file in pathlib.Path('example_files').iterdir():
        print("---" * 80)
        data = zone_file.read_text()

        lexer = BindLexer()
        tokens = list(lexer.tokenize(data))

        tokens_for_print = [f"{tok.type}: {tok.value}" for tok in tokens]
        pprint(tokens_for_print, compact=True, width=120)

        with contextlib.suppress(EOFError):
            tokens = lexer.tokenize(data)
            parser = BindParser()
            result = parser.parse(tokens)
            pprint(result, width=360)
