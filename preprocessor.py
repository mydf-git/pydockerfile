#!/usr/bin/env python3
import sys
from textx import metamodel_from_str, get_children_of_type
from dataclasses import dataclass
import textwrap

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
PIP: /(?i)PIP / /(\n|.)*?[^\\]\n/;
"""

def convert_pydf_to_df(pydf):
    root = parse_pydf(pydf)
    stringifier = Stringifier(preprocess=True)
    return stringifier(root)

def stringify_pycommand(node):
    assert isinstance(node, str)
    return node

def preprocess_pycommand(node):
    assert isinstance(node, str)
    commands = node.replace('\\\n', ' ').split()
    if commands[0].lower() == 'pip':
        out = f"RUN pip install {' '.join(commands[1:])}"
        return textwrap.fill(out, width=70, subsequent_indent='  ',
                break_long_words=False, break_on_hyphens=False).replace('\n', ' \\\n')
    else:
        assert False, node
    return 

@dataclass
class Stringifier:
    preprocess: bool

    def __call__(self, node,):
        if isinstance(node, list): return '\n'.join(self(i) for i in node)
        if node is None: return ''
        elif isinstance(node, str): return node
        elif isinstance(node, VirtualLine):
            return self(node.comment) + self(node.command) + self(node.empty)
        elif isinstance(node, FullCommand):
            if node.pycommand:
                return preprocess_pycommand(node.pycommand) if self.preprocess else stringify_pycommand(node.pycommand)
            if node.originalcommand: return self(node.originalcommand)
            assert False, node
        else:
            import ipdb;ipdb.set_trace()
            assert False, node

class VirtualLine(Node): pass
class FullCommand(Node): pass

def parse_pydf(pydf):
    MM = metamodel_from_str(GRAMMAR, skipws=False, debug=False, classes=[VirtualLine, FullCommand, ])
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

def test_preprocessor_pip():
    pydf = r"""
FROM alpine
PiP fred lib1 \
        lib2 lib3 lib4 lib5 lib6 lib7 lib8 lib9 lib10 lib11  lib12 lib13 lib14  lib15 lib16 lib17
"""
    OUT = (r'''
FROM alpine
RUN pip install fred lib1 lib2 lib3 lib4 lib5 lib6 lib7 lib8 lib9 \
  lib10 lib11 lib12 lib13 lib14 lib15 lib16 lib17
''')

    root = parse_pydf(pydf)

    stringifier = Stringifier(preprocess=False)
    assert ''.join(stringifier(n) for n in root) == pydf
    stringifier.preprocess = True
    assert ''.join(stringifier(n) for n in root).strip() == OUT.strip()

def test_stringify_normal_dockerfiles():
    import glob
    for file in glob.glob('tests/sample*.dockerfile'):
        with open(file) as f: pydf = f.read()
        root = parse_pydf(pydf)
        stringifier = Stringifier(preprocess=False)
        assert ''.join(stringifier(n) for n in root) == pydf


if __name__ == '__main__':
    main()
