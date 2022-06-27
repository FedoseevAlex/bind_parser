from sly import Parser

from sly_zone.lexer import ZoneLexer


class ZoneParser(Parser):
    debugfile: str = "parser.out"
    origin_domain: str = ""
    previous_domain: str = ""
    default_ttl: int = 1000
    tokens: set = ZoneLexer.tokens

    @_("record", "ttl", "origin")
    def zone(self, pattern_match):
        return [pattern_match[0]]

    @_(
        "zone record",
        "zone ttl",
        "zone origin",
    )
    def zone(self, pattern_match):
        pattern_match.zone.append(pattern_match[1])
        return pattern_match.zone

    @_("record_header record_content")
    @_("record_content")
    def record(self, pattern_match):
        record_header = {}
        if hasattr(pattern_match, "record_header"):
            record_header = pattern_match.record_header
        else:
            record_header["ttl"] = self.default_ttl
            record_header["name"] = ".".join([self.previous_domain, self.origin_domain])

        return dict(
            **record_header,
            **pattern_match.record_content,
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
    def record_content(self, pattern_match):
        return pattern_match[0]

    @_("domain_name INTEGER CLASS")
    @_("domain_name INTEGER")
    @_("INTEGER CLASS")
    @_("CLASS")
    @_("domain_name CLASS")
    @_("domain_name")
    def record_header(self, pattern_match):
        domain_name = self.previous_domain
        if hasattr(pattern_match, "domain_name"):
            domain_name = pattern_match.domain_name

        return dict(
            name=domain_name,
            ttl=getattr(pattern_match, "INTEGER", self.default_ttl),
        )

    @_("NS domain_name")
    def ns_content(self, pattern_match):
        return dict(content=pattern_match.domain_name, type=pattern_match.NS)

    @_("CNAME domain_name")
    def cname_content(self, pattern_match):
        return dict(content=pattern_match.domain_name, type=pattern_match.CNAME)

    @_("ALIAS domain_name")
    def alias_content(self, pattern_match):
        return dict(content=pattern_match.domain_name, type=pattern_match.ALIAS)

    @_("SOA domain_name domain_name INTEGER INTEGER INTEGER INTEGER INTEGER")
    def soa_content(self, pattern_match):
        return dict(
            ns=pattern_match.domain_name0,
            email=pattern_match.domain_name1,
            serial=pattern_match.INTEGER0,
            refresh=pattern_match.INTEGER1,
            retry=pattern_match.INTEGER2,
            expire=pattern_match.INTEGER3,
            minimum=pattern_match.INTEGER4,
            type=pattern_match.SOA,
        )

    @_("SRV INTEGER INTEGER INTEGER domain_name")
    def srv_content(self, pattern_match):
        return dict(
            priority=pattern_match.INTEGER0,
            weight=pattern_match.INTEGER1,
            port=pattern_match.INTEGER2,
            target=pattern_match.domain_name,
            type=pattern_match.SRV,
        )

    @_("MX INTEGER domain_name")
    def mx_content(self, pattern_match):
        return dict(
            content=pattern_match.domain_name,
            priority=pattern_match.INTEGER,
            type=pattern_match.MX,
        )

    @_("AAAA IPV6")
    def aaaa_content(self, pattern_match):
        return dict(content=pattern_match.IPV6, type=pattern_match.AAAA)

    @_("A IPV4")
    def a_content(self, pattern_match):
        return dict(content=pattern_match.IPV4, type=pattern_match.A)

    @_("TXT text")
    def txt_content(self, pattern_match):
        return dict(content=pattern_match.text, type=pattern_match.TXT)

    @_("TEXT")
    @_("text TEXT")
    def text(self, pattern_match):
        return getattr(pattern_match, "text", "") + pattern_match.TEXT.strip('"')

    @_("ORIGIN domain_name")
    def origin(self, pattern_match):
        self.origin_domain = pattern_match.domain_name
        print(f"{self.origin_domain=}")
        return ("origin", pattern_match.domain_name)

    @_("TTL INTEGER")
    def ttl(self, pattern_match):
        self.default_ttl = pattern_match.INTEGER
        print(f"{self.default_ttl=}")
        return ("ttl", pattern_match.INTEGER)

    @_("DOMAIN_NAME")
    def domain_name(self, pattern_match):
        domain_name: str = pattern_match.DOMAIN_NAME
        if domain_name == "@":
            domain_name = self.origin_domain

        self.previous_domain = domain_name
        return domain_name
