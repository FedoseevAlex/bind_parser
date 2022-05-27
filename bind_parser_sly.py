from sly import Parser


class BindParser(Parser):
    debugfile = "parser.out"
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
        "COMMENT",
    }

    @_(
        "record",
        "comment",
    )
    def zone(self, p):
        return [p[0]]

    @_(
        "zone comment",
        "zone record",
    )
    def zone(self, p):
        p.zone.append(p[1])
        return p.zone

    @_(
        "soa_record",
        "a_record",
        "aaaa_record",
        "ns_cname_record",
        "mx_record",
        "txt_record",
        "srv_record",
    )
    def record(self, p):
        return p[0]

    @_("DOMAIN_NAME INTEGER CLASS RECORD_TYPE")
    def record_header(self, p):
        return dict(
            name=p.DOMAIN_NAME,
            ttl=p.INTEGER,
            type=p.RECORD_TYPE,
        )

    @_("record_header soa_content")
    def soa_record(self, p):
        return dict(
            **p.record_header,
            **p.soa_content,
        )

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

    @_("record_header INTEGER INTEGER INTEGER DOMAIN_NAME")
    def srv_record(self, p):
        return dict(
            **p.record_header,
            priority=p.INTEGER0,
            weight=p.INTEGER1,
            port=p.INTEGER2,
            target=p.DOMAIN_NAME,
        )

    @_("record_header INTEGER DOMAIN_NAME")
    def mx_record(self, p):
        return dict(
            **p.record_header,
            content=p.DOMAIN_NAME,
            priority=p.INTEGER,
        )

    @_("record_header DOMAIN_NAME")
    def ns_cname_record(self, p):
        return dict(
            **p.record_header,
            content=p.DOMAIN_NAME,
        )

    @_("record_header IPV6")
    def aaaa_record(self, p):
        return dict(
            **p.record_header,
            content=p.IPV6,
        )

    @_("record_header IPV4")
    def a_record(self, p):
        return dict(
            **p.record_header,
            content=p.IPV4,
        )

    @_("record_header TEXT")
    def txt_record(self, p):
        return dict(**p.record_header, content=p.TEXT.strip('"'))

    @_("COMMENT")
    def comment(self, p):
        return dict(comment=p.COMMENT)
