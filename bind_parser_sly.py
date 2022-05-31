from sly import Parser


class BindParser(Parser):
    debugfile = "parser.out"
    origin_domain = "lol.no.origin.domain.try.to.specify.origin."
    default_ttl = 1000
    tokens = {
        "INTEGER",
        "DOMAIN_NAME",
        "CLASS",
        "RECORD_TYPE",
        "TTL",
        "ORIGIN",
        "TEXT",
        "IPV4",
        "IPV6",
    }
    # precedence = (
    #     ('left', 'DOMAIN_NAME'),
    #     ('left', 'RECORD_TYPE'),
    # )

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
    def record(self, p):
        return dict(
            **p.record_header,
            **p.record_content,
        )

    @_(
        "soa_content",
        "a_content",
        "aaaa_content",
        "ns_cname_content",
        "mx_content",
        "txt_content",
        "srv_content",
    )
    def record_content(self, p):
        return p[0]

    @_("DOMAIN_NAME INTEGER CLASS RECORD_TYPE")
    @_("INTEGER CLASS RECORD_TYPE")
    @_("CLASS RECORD_TYPE")
    @_("RECORD_TYPE")
    @_("DOMAIN_NAME CLASS RECORD_TYPE")
    @_("DOMAIN_NAME RECORD_TYPE")
    def record_header(self, p):
        return dict(
            name=getattr(p, "DOMAIN_NAME", self.origin_domain),
            ttl=getattr(p, "INTEGER", self.default_ttl),
            type=p.RECORD_TYPE,
        )

    @_("DOMAIN_NAME")
    def ns_cname_content(self, p):
        return dict(content=p.DOMAIN_NAME)

    @_("DOMAIN_NAME DOMAIN_NAME INTEGER INTEGER INTEGER INTEGER INTEGER")
    def soa_content(self, p):
        return dict(
            ns=p.DOMAIN_NAME0,
            email=p.DOMAIN_NAME1,
            serial=p.INTEGER0,
            refresh=p.INTEGER1,
            retry=p.INTEGER2,
            expire=p.INTEGER3,
            minimum=p.INTEGER4,
        )

    @_("INTEGER INTEGER INTEGER DOMAIN_NAME")
    def srv_content(self, p):
        return dict(
            priority=p.INTEGER0,
            weight=p.INTEGER1,
            port=p.INTEGER2,
            target=p.DOMAIN_NAME,
        )

    @_("INTEGER DOMAIN_NAME")
    def mx_content(self, p):
        return dict(
            content=p.DOMAIN_NAME,
            priority=p.INTEGER,
        )

    @_("IPV6")
    def aaaa_content(self, p):
        return dict(content=p.IPV6)

    @_("IPV4")
    def a_content(self, p):
        return dict(content=p.IPV4)

    @_("TEXT")
    def txt_content(self, p):
        return dict(content=p.TEXT.strip('"'))

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
