import contextlib
import pathlib
from pprint import pprint

from sly_zone.lexer import  ZoneLexer
from sly_zone.parser import ZoneParser

if __name__ == "__main__":
    for zone_file in pathlib.Path('example_files').iterdir():
        print("---" * 80)
        print(zone_file)
        data = zone_file.read_text()

        lexer = ZoneLexer()
        tokens = list(lexer.tokenize(data))

        tokens_for_print = [f"{tok.type}: {tok.value}" for tok in tokens]
        pprint(tokens_for_print, compact=True, width=120)

        with contextlib.suppress(EOFError):
            tokens = lexer.tokenize(data)
            parser = ZoneParser()
            result = parser.parse(tokens)
            pprint(result, width=360)
