#!/usr/bin/env python3
import sys
from textx import metamodel_from_str, get_children_of_type
from dataclasses import dataclass

def main():
    pydf = sys.stdin.read()
    df = convert_pydf_to_df(pydf)
    sys.stdout.write(df)

class Node:
    def __init__(self, **kw):
        del self.parent



# http://textx.github.io/textX/latest/grammar/
GRAMMAR = r"""
Root: root+=VirtualLine;
VirtualLine: (comment=Comment_ | command=FullCommand | empty=EMPTY);
EMPTY: /^\s*\n/;
//EOL: /[^\\]\n/;
FullCommand: /[ \t]*/ (pycommand=PyDockerfileCommands | !PyDockerfileCommandsKeywords originalcommand=/(?m)\S(\n|.)*?[^\\]\n/ );
Comment_: /^\s*#.*\n/;

PyDockerfileCommands: PIP;
PyDockerfileCommandsKeywords: /(?i)PIP/;
PIP: /(?i)PIP / /.*\n/;
"""

def convert_pydf_to_df(pydf):
    root = parse_pydf(pydf)
    return root

def stringify_pycommand(node):
    assert isinstance(node, str)
    return node

def preprocess_pycommand(node):
    return ''

@dataclass
class Stringifier:
    preprocess: bool

    def __call__(self, node,):
        if node is None: return ''
        elif isinstance(node, str): return node
        elif isinstance(node, VirtualLine):
            return self(node.comment) + self(node.command) + self(node.empty)
        elif isinstance(node, FullCommand):
            if node.pycommand:
                return preprocess_pycommand(node.pycommand) if self.preprocess else stringify_pycommand(node.pycommand)
            if node.originalcommand: return self(node.originalcommand)
            assert False
        else:
            assert node.__class__ == None

class VirtualLine(Node): pass
class FullCommand(Node): pass

def parse_pydf(pydf):
    MM = metamodel_from_str(GRAMMAR, skipws=False, debug=True, classes=[VirtualLine, FullCommand, ])
    model = MM.model_from_str(pydf)
    root = model.root
    return root

def test_preprocessor():
    pydf = r"""
FROM alpine
RUN this
# comment
RUN long \
run

RUN not a #comment
PiP fred
"""
    root = parse_pydf(pydf)
    assert root[0].empty
    assert root[1].command
    assert root[2].command
    assert root[3].comment
    assert root[4].command
    assert root[5].empty
    assert root[6].command
    assert root[7].command.pycommand

    stringifier = Stringifier(preprocess=False)
    assert ''.join(stringifier(n) for n in root) == pydf


if __name__ == '__main__':
    main()
