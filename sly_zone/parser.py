from sly import Parser

from sly_zone.lexer import ZoneLexer


class ZoneParser(Parser):
    debugfile: str = "parser.out"
    origin_domain: str = ""
    previous_domain: str = ""
    default_ttl: int = 1000
    tokens: set = ZoneLexer.tokens

    @_("record", "ttl", "origin")
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
        if hasattr(p, "record_header"):
            record_header = p.record_header
        else:
            record_header["ttl"] = self.default_ttl
            record_header["name"] = ".".join([self.previous_domain, self.origin_domain])

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
        "alias_content",
    )
    def record_content(self, p):
        return p[0]

    @_("domain_name INTEGER CLASS")
    @_("domain_name INTEGER")
    @_("INTEGER CLASS")
    @_("CLASS")
    @_("domain_name CLASS")
    @_("domain_name")
    def record_header(self, p):
        domain_name = self.previous_domain
        if hasattr(p, "domain_name"):
            domain_name = p.domain_name

        return dict(
            name=domain_name,
            ttl=getattr(p, "INTEGER", self.default_ttl),
        )

    @_("NS domain_name")
    def ns_content(self, p):
        return dict(content=p.domain_name, type=p.NS)

    @_("CNAME domain_name")
    def cname_content(self, p):
        return dict(content=p.domain_name, type=p.CNAME)

    @_("ALIAS domain_name")
    def alias_content(self, p):
        return dict(content=p.domain_name, type=p.ALIAS)

    @_("SOA domain_name domain_name INTEGER INTEGER INTEGER INTEGER INTEGER")
    def soa_content(self, p):
        return dict(
            ns=p.domain_name0,
            email=p.domain_name1,
            serial=p.INTEGER0,
            refresh=p.INTEGER1,
            retry=p.INTEGER2,
            expire=p.INTEGER3,
            minimum=p.INTEGER4,
            type=p.SOA,
        )

    @_("SRV INTEGER INTEGER INTEGER domain_name")
    def srv_content(self, p):
        return dict(
            priority=p.INTEGER0,
            weight=p.INTEGER1,
            port=p.INTEGER2,
            target=p.domain_name,
            type=p.SRV,
        )

    @_("MX INTEGER domain_name")
    def mx_content(self, p):
        return dict(
            content=p.domain_name,
            priority=p.INTEGER,
            type=p.MX,
        )

    @_("AAAA IPV6")
    def aaaa_content(self, p):
        return dict(content=p.IPV6, type=p.AAAA)

    @_("A IPV4")
    def a_content(self, p):
        return dict(content=p.IPV4, type=p.A)

    @_("TXT text")
    def txt_content(self, p):
        return dict(content=p.text, type=p.TXT)

    @_("TEXT")
    @_("text TEXT")
    def text(self, p):
        return getattr(p, "text", "") + p.TEXT.strip('"')

    @_("ORIGIN domain_name")
    def origin(self, p):
        self.origin_domain = p.domain_name
        print(f"{self.origin_domain=}")
        return ("origin", p.domain_name)

    @_("TTL INTEGER")
    def ttl(self, p):
        self.default_ttl = p.INTEGER
        print(f"{self.default_ttl=}")
        return ("ttl", p.INTEGER)

    @_("DOMAIN_NAME")
    def domain_name(self, p):
        domain_name: str = p.DOMAIN_NAME
        if domain_name == "@":
            domain_name = self.origin_domain

        if not domain_name.endswith(self.origin_domain):
            domain_name = ".".join([domain_name, self.origin_domain])

        self.previous_domain = domain_name
        return domain_name
