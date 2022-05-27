from sly import Parser


class BindParser(Parser):
    debugfile = 'parser.out'
    tokens = {
        'INTEGER',
        'DOMAIN_NAME',
        'CLASS',
        'RECORD_TYPE',
        'TTL',
        'ORIGIN',
        'TEXT',
        'IPV4',
        'IPV6',
        'COMMENT',
    }

    @_(
        'record',
        'comment',
    )
    def zone(self, p):
        return [p[0]]

    @_(
        'zone comment',
        'zone record',
    )
    def zone(self, p):
        p.zone.append(p[1])
        return p.zone

    @_(
        'soa_record',
        'a_record',
        'aaaa_record',
        'ns_cname_record',
        'mx_record',
        'txt_record',
        'srv_record',
    )
    def record(self, p):
        return p[0]

    # @_('DOMAIN_NAME INTEGER CLASS RECORD_TYPE')
    # def record_header(self, p):
    #     return {
    #         "name": p.DOMAIN_NAME0,
    #         "ttl": p.INTEGER0,
    #         "type": p.RECORD_TYPE,
    #     }

    @_('DOMAIN_NAME INTEGER CLASS RECORD_TYPE DOMAIN_NAME DOMAIN_NAME INTEGER INTEGER INTEGER INTEGER INTEGER')
    def soa_record(self, p):
        return {
            "name": p.DOMAIN_NAME0,
            "ttl": p.INTEGER0,
            "type": p.RECORD_TYPE,
            "ns": p.DOMAIN_NAME1,
            "email": p.DOMAIN_NAME2,
            "serial": p.INTEGER1,
            "refresh": p.INTEGER2,
            "retry": p.INTEGER3,
            "expire": p.INTEGER4,
            "minimum": p.INTEGER5,
            }

    @_('DOMAIN_NAME INTEGER CLASS RECORD_TYPE INTEGER INTEGER INTEGER DOMAIN_NAME')
    def srv_record(self, p):
        return {
            "name": p.DOMAIN_NAME0,
            "ttl": p.INTEGER0,
            "type": p.RECORD_TYPE,
            "priority": p.INTEGER1,
            "weight": p.INTEGER2,
            "port": p.INTEGER3,
            "target": p.DOMAIN_NAME1,
            }

    @_('DOMAIN_NAME INTEGER CLASS RECORD_TYPE INTEGER DOMAIN_NAME')
    def mx_record(self, p):
        return {
            "name": p.DOMAIN_NAME0,
            "ttl": p.INTEGER0,
            "type": p.RECORD_TYPE,
            "content": p.DOMAIN_NAME1,
            "priority": p.INTEGER1,
            }

    @_('DOMAIN_NAME INTEGER CLASS RECORD_TYPE DOMAIN_NAME')
    def ns_cname_record(self, p):
        return {
            "name": p.DOMAIN_NAME0,
            "ttl": p.INTEGER,
            "type": p.RECORD_TYPE,
            "content": p.DOMAIN_NAME1,
            }

    @_('DOMAIN_NAME INTEGER CLASS RECORD_TYPE IPV6')
    def aaaa_record(self, p):
        return {
            "name": p.DOMAIN_NAME,
            "ttl": p.INTEGER,
            "type": p.RECORD_TYPE,
            "content": p.IPV6,
            }

    @_('DOMAIN_NAME INTEGER CLASS RECORD_TYPE IPV4')
    def a_record(self, p):
        return {
            "name": p.DOMAIN_NAME,
            "ttl": p.INTEGER,
            "type": p.RECORD_TYPE,
            "content": p.IPV4,
            }

    @_('DOMAIN_NAME INTEGER CLASS RECORD_TYPE TEXT')
    def txt_record(self, p):
        return {
            "name": p.DOMAIN_NAME,
            "ttl": p.INTEGER,
            "type": p.RECORD_TYPE,
            "content": p.TEXT.strip("\""),
            }

    @_('COMMENT')
    def comment(self, p):
        return {"comment": p.COMMENT}


#     def error(self, p):
#         if p:
#              print("Hmmmm")
#              print(f"{p.type=}")
#              print(f"{p.value=}")
#              print(f"{p.lineno=}")
#              print(f"{p.index=}")
#              # Just discard the token and tell the parser it's okay.
#              self.errok()
#         else:
#              print("Syntax error at EOF")


# S	→	e B b A
# S	→	e A
# A	→	a
# A	→	ε
# B	→	a
# B	→	a D
# D	→	b
#
# S	→	e a D b A
# S	→	e a b A
# S	→	e A
# A	→	a
# A	→	ε
# D	→	b

