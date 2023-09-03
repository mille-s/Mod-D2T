# Purpose: Parse BUDDY structures in .str format
# Author: François Lareau

from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from pprint import pprint

DEFAULT_ENCODING = 'utf-8'

grammar = Grammar(
    r"""
    strucs      = struc+
    struc       = struchead lbr _ nodes rbr _

    struchead   = 'structure' ws level ws name _
    level       = name

    nodes       = node*
    node        = nodehead lbr _ nodebody rbr _
    nodehead    = label nodeid _
    nodeid      = colon num
    nodebody    = (feature / coreference / precedence / edge / nodehead)*

    feature     = name _ eq _ label _
    coreference = coref _ nodehead
    precedence  = prec _ nodehead
    edge        = label rarr _ nodehead

    label   = name / quoted
    name    = ~r'\w+'
    quoted  = ~r'"[^"]*"'

    colon   = ':'
    eq      = '='
    rarr    = '->'
    coref   = '<->' / 'coref->'
    prec    = '~' / 'b->'
    lbr     = '{'
    rbr     = '}'
    num     = ~r'\d+'
    any     = ~r'.'
    _       = ws?
    ws      = ~r'\s+'
    """
)


class StrucVisitor(NodeVisitor):

    def visit_strucs(self, parsenode, strucs):
        return strucs

    def visit_struc(self, parsenode, struc):
        struchead, _, _, nodes, _, _ = struc
        return struchead, nodes

    def visit_struchead(self, parsenode, struchead):
        _, _, level, _, name, _ = struchead
        return level, name

    def visit_level(self, parsenode, _):
        return parsenode.text

    def visit_nodes(self, parsenode, nodes):
        return nodes

    def visit_node(self, parsenode, node):
        nodehead, _, _, nodebody, _, _ = node
        return nodehead, nodebody

    def visit_nodehead(self, parsenode, nodehead):
        label, nodeid, _ = nodehead
        return ('node', label, nodeid)

    def visit_nodeid(self, parsenode, nodeid):
        _, num = nodeid
        return num

    def visit_nodebody(self, parsenode, nodebody):
        return sum(nodebody, []) # Flatten list

    def visit_feature(self, _, feature):
        key, _, _, _, value, _ = feature
        return ('feature', key, value)

    def visit_coreference(self, _, coreference):
        _, _, nodehead = coreference
        return ('coref', nodehead)

    def visit_precedence(self, _, precedence):
        _, _, nodehead = precedence
        return ('prec', nodehead)

    def visit_edge(self, _, edge):
        label, _, _, nodehead = edge
        return ('edge', label, nodehead)

    def visit_num(self, parsenode, _):
        return int(parsenode.text)

    def visit_label(self, _, text):
        return text[0]                      # there's only one child

    def visit_name(self, parsenode, _):
        return parsenode.text

    def visit_quoted(self, parsenode, _):
        return parsenode.text[1:-1].replace("''", '"')  # strip quotes and put back escaped quotes

    def generic_visit(self, _, children):
        return children

def normalize(text):
    return text.replace('\\"', "''")

def parse(file, encoding=DEFAULT_ENCODING):
    """
    Parse a MATE structure file and return a list of structures.
    Args:
        file (str):     path to file
        encoding (str): file encoding
    """
    try:
        assert isinstance(file, str)
    except:
        raise TypeError('Filename must be a string')
    with open(file, 'r', encoding=encoding) as f:
        text = normalize(f.read().strip())
    try:
        parsetree = grammar.parse(text)
        visitor = StrucVisitor()
        strucs = visitor.visit(parsetree)
    except:
        raise SyntaxError(f'Unable to parse {file}')
    return strucs


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file = sys.argv[1]
        encoding = DEFAULT_ENCODING
        if len(sys.argv) > 2:
            encoding = sys.argv[2]
        strucs = parse(file, encoding)
        pprint(strucs)
    else:
        print('Usage: python matestruc.py <file> [encoding]')
