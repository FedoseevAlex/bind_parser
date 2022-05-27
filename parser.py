from pyrser import grammar, meta
from pyrser.directives import ignore
from pyrser.hooks import dump_nodes
from pyrser.hooks.echo import echo_nodes
from pyrser.passes import to_yml
import ipaddress

text = """
10.100.0.1
"""

class Bind(grammar.Grammar):
    entry = "zone"
    grammar="""
        zone = [ [ipv4 | octet]:>_ eof? #dump_nodes]
        ipv4 = [ [octet '.' octet '.' octet '.' octet]:ipv4 #is_ipv4(_, ipv4) ]
        octet = [ 
            [ '2' [ '0'..'5' ] [ '0'..'5' ] |
              '1' [ '0'..'9' ] [ '0'..'9' ] |
              [ '1'..'9' ] [ '0'..'9' ] |
              [ '0'..'9' ]
            ]: octet #is_int(_, octet)
            #dump_nodes
        ]
    """
    
@meta.hook(Bind)
def is_int(self, ast, octet):
    ast.node = int(self.value(octet))
    return True

@meta.hook(Bind)
def is_ipv4(self, ast, ipv4):
    print(f"{ipv4.node=}")
    ast.node = ipaddress.IPv4Address(self.value(ipv4))
    return True

if __name__ == "__main__":
    bind = Bind()
    x = bind.parse('201')