from ipaddress import IPv4Address, IPv6Address

from sly import Lexer


class ZoneLexer(Lexer):
    scope = 0
    record_types = {
        "SOA",
        "NS",
        "A",
        "AAAA",
        "MX",
        "TXT",
        "CNAME",
        "SRV",
        "ALIAS",
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

    _IPV4_SEGMENT = r"((2[0-5]{2})|(1[0-9]{2})|([1-9]?[0-9]))"

    @_(r"({0}\.){{3}}({0})".format(_IPV4_SEGMENT))
    def IPV4(self, token):
        token.value = IPv4Address(token.value)
        return token

    @_(r"([a-fA-F0-9]{0,4}:){2,7}[a-fA-F0-9]{0,4}")
    def IPV6(self, token):
        token.value = IPv6Address(token.value)
        return token

    @_(r"([0-9]+)")
    def INTEGER(self, token):
        token.value = int(token.value)
        return token

    CLASS = r"(IN|CH|CS|HS)"
    TTL = r"\$TTL"
    ORIGIN = r"(\$ORIGIN)"
    AAAA = "AAAA"
    ALIAS = "ALIAS"
    A = "A"
    SOA = "SOA"
    TXT = "TXT"
    SRV = "SRV"
    CNAME = "CNAME"
    NS = "NS"
    MX = "MX"
    TEXT = r'"[\w\s\W]*?"'
    DOMAIN_NAME = r"((\*\.)?[\w\-\.]+|@)"

    @_(r"\n+")
    def ignore_newline(self, token):
        self.lineno += token.value.count("\n")

    @_(r"\(")
    def ingnore_lparent(self, token):
        self.scope += 1

    @_(r"\)")
    def ingnore_rparent(self, token):
        self.scope -= 1

    ignore_whitespace = r"\s+"

    @_(r";.*")
    def ignore_comments(self, token):
        self.lineno += token.value.count("\n")

    def error(self, token):
        print(f'Line {self.lineno}: Bad character "{token.value[0]}"\n')
        self.index += 1
