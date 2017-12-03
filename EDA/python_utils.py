from lib2to3 import refactor
from nbconvert import PythonExporter
import nbformat
import ast, gast

fixers = set(refactor.get_fixers_from_package('lib2to3.fixes'))
exporter = PythonExporter()


def fix_python2(code):
    tool = refactor.RefactoringTool(fixers, {}, explicit=True)

    return str(tool.refactor_string(code + '\n', 'test'))


def ipynb_to_code(ipynb):
    notebook = nbformat.reads(ipynb, as_version=4)
    code, meta = exporter.from_notebook_node(notebook)

    return code

class FuncCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self._name = deque()

    @property
    def name(self):
        return '.'.join(self._name)

    @name.deleter
    def name(self):
        self._name.clear()

    def visit_Module(self, node):
        print("Module : %s" % node)

    def visit_Name(self, node):
        self._name.appendleft(node.id)

    def visit_Attribute(self, node):
        try:
            self._name.appendleft(node.attr)
            self._name.appendleft(node.value.id)
        except AttributeError:
            self.generic_visit(node)

def extract_imports(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
#         print(file.filename)
# #                 print(code)
# #                 print('YO')
# #             except ParserError:
        try:
            code = fix_python2(code + '\n')
#                  %pdb
#                 print(code)
            tree = ast.parse(code)
        except Exception as e:
            # print(e)
            return 'Error'

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            module = ''
        elif isinstance(node, ast.ImportFrom):
            module = node.module
        else:
            continue

        for n in node.names:
            yield (module, n.name, n.asname)

def get_func_calls(tree):
    func_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            callvisitor = FuncCallVisitor()
            callvisitor.visit(node.func)
            func_calls.append(callvisitor.name)

    return func_calls

#
# def extract_import(code):
#     tree = ast.parse(code)
#     # ast.dump(tree)
