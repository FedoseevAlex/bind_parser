from ipaddress import IPv4Address, IPv6Address

from sly import Lexer


class BindLexer(Lexer):
    record_types = {
        "RECORD_TYPE",
        "SOA",
        "NS",
        "A",
        "AAAA",
        "MX",
        "TXT",
        "CNAME",
        "SRV",
    }
    tokens = {
        "INTEGER",
        "DOMAIN_NAME",
        "CLASS",
        "TTL",
        "ORIGIN",
        "TEXT",
        "IPV4",
        "IPV6",
    }
    # add record type tokens
    tokens.update(record_types)

    RECORD_TYPE['SOA'] = "SOA"
    RECORD_TYPE['NS'] = "NS"
    RECORD_TYPE['A'] = "A"
    RECORD_TYPE['AAAA'] = "AAAA"
    RECORD_TYPE['MX'] = "MX"
    RECORD_TYPE['TXT'] = "TXT"
    RECORD_TYPE['CNAME'] = "CNAME"
    RECORD_TYPE['SRV'] = "SRV"

    scope = 0

    _IPV4_SEGMENT = r"((2[0-5]{2})|(1[0-9]{2})|([1-9]?[0-9]))"

    @_(r"({0}\.){{3}}({0})".format(_IPV4_SEGMENT))
    def IPV4(self, t):
        t.value = IPv4Address(t.value)
        return t

    @_(r"([a-fA-F0-9]{0,4}:){2,7}[a-fA-F0-9]{0,4}")
    def IPV6(self, t):
        t.value = IPv6Address(t.value)
        return t

    @_(r"([0-9]+)")
    def INTEGER(self, t):
        t.value = int(t.value)
        return t

    CLASS = r"(IN|CH|CS|HS)"
    TTL = r"\$TTL"
    ORIGIN = r"(\$ORIGIN)"
    RECORD_TYPE = r"(AAAA|A|SOA|TXT|SRV|CNAME|ANAME|NS|MX)"
    TEXT = r'"[\w\s\W]*?"'
    DOMAIN_NAME = r"((\*\.)?[\w\-\.]+|@)"

    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    @_(r"\(")
    def ingnore_lparent(self, t):
        self.scope += 1

    @_(r"\)")
    def ingnore_rparent(self, t):
        self.scope -= 1

    ignore_whitespace = r"\s+"

    @_(r";.*")
    def ignore_comments(self, t):
        self.lineno += t.value.count("\n")

    def error(self, t):
        print(f'Line {self.lineno}: Bad character "{t.value[0]}"\n')
        self.index += 1
