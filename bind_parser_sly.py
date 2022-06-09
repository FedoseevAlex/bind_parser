import re
from sly import Parser

from bind_lexer_sly import BindLexer


class BindParser(Parser):
    debugfile = "parser.out"
    origin_domain = ""
    local_domain = ""
    default_ttl = 1000
    tokens = BindLexer.tokens

    @_(
        "record",
        "ttl",
        "origin"
    )
    def zone(self, p):
        return [p[0]]

    @_(
        "zone record",
        "zone ttl",
        "zone origin",
    )
    def zone(self, p):
        p.zone.append(p[1])
        return p.zone

    @_("record_header record_content")
    @_("record_content")
    def record(self, p):
        record_header = {}
        if hasattr(p, 'record_header'):
            record_header = p.record_header
        else:
            record_header['ttl'] = self.default_ttl
            record_header['name'] = ".".join([self.local_domain, self.origin_domain])

        return dict(
            **record_header,
            **p.record_content,
        )

    @_(
        "soa_content",
        "a_content",
        "aaaa_content",
        "ns_content",
        "cname_content",
        "mx_content",
        "txt_content",
        "srv_content",
    )
    def record_content(self, p):
        return p[0]

    @_("DOMAIN_NAME INTEGER CLASS")
    @_("INTEGER CLASS")
    @_("CLASS")
    @_("DOMAIN_NAME CLASS")
    @_("DOMAIN_NAME")
    def record_header(self, p):
        if hasattr(p, 'DOMAIN_NAME'):
            self.local_domain = p.DOMAIN_NAME

        if self.local_domain == '@':
            domain_name = self.origin_domain
        else:
            domain_name = ".".join([self.local_domain, self.origin_domain])

        return dict(
            name= domain_name,
            ttl=getattr(p, "INTEGER", self.default_ttl),
        )

    @_("NS DOMAIN_NAME")
    def ns_content(self, p):
        return dict(content=p.DOMAIN_NAME, type=p.NS)

    @_("CNAME DOMAIN_NAME")
    def cname_content(self, p):
        return dict(content=p.DOMAIN_NAME, type=p.CNAME)

    @_("SOA DOMAIN_NAME DOMAIN_NAME INTEGER INTEGER INTEGER INTEGER INTEGER")
    def soa_content(self, p):
        return dict(
            ns=p.DOMAIN_NAME0,
            email=p.DOMAIN_NAME1,
            serial=p.INTEGER0,
            refresh=p.INTEGER1,
            retry=p.INTEGER2,
            expire=p.INTEGER3,
            minimum=p.INTEGER4,
            type=p.SOA,
        )

    @_("SRV INTEGER INTEGER INTEGER DOMAIN_NAME")
    def srv_content(self, p):
        return dict(
            priority=p.INTEGER0,
            weight=p.INTEGER1,
            port=p.INTEGER2,
            target=p.DOMAIN_NAME,
            type=p.SRV,
        )

    @_("MX INTEGER DOMAIN_NAME")
    def mx_content(self, p):
        return dict(
            content=p.DOMAIN_NAME,
            priority=p.INTEGER,
            type=p.MX,
        )

    @_("AAAA IPV6")
    def aaaa_content(self, p):
        return dict(content=p.IPV6, type=p.AAAA)

    @_("A IPV4")
    def a_content(self, p):
        return dict(content=p.IPV4, type=p.A)

    @_("TXT TEXT")
    def txt_content(self, p):
        return dict(content=p.TEXT.strip('"'), type=p.TXT)

    @_("ORIGIN DOMAIN_NAME")
    def origin(self, p):
        self.origin_domain = p.DOMAIN_NAME
        print(f"{self.origin_domain=}")
        return ('origin', p.DOMAIN_NAME)

    @_("TTL INTEGER")
    def ttl(self, p):
        self.default_ttl = p.INTEGER
        print(f"{self.default_ttl=}")
        return ('ttl', p.INTEGER)
