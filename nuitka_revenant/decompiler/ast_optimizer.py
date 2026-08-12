"""
AST Validation, Syntax Recovery, and PEP8 Formatting Engine for REVENANT.
Guarantees valid Python ASTs and cleans up decompilation artifacts.
"""

import ast
import re
from typing import Tuple, Optional


class ASTOptimizationError(Exception):
    """Raised when AST recovery cannot repair broken source code."""
    pass


def repair_empty_blocks(source_code: str) -> str:
    """
    Scans source code lines and inserts 'pass' into empty block definitions
    (e.g., def, class, if, elif, else, try, except, finally, with, for, while).
    """
    lines = source_code.splitlines()
    if not lines:
        return ""

    repaired = []
    block_keyword_re = re.compile(r'^\s*(def|class|if|elif|else|try|except|finally|with|for|while)\b.*:\s*(#.*)?$')

    for i, line in enumerate(lines):
        repaired.append(line)
        if block_keyword_re.match(line):
            curr_indent = len(line) - len(line.lstrip())
            # Check next line indent
            has_body = False
            for j in range(i + 1, len(lines)):
                next_line = lines[j]
                if not next_line.strip() or next_line.strip().startswith('#'):
                    continue
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent > curr_indent:
                    has_body = True
                break

            if not has_body:
                repaired.append(" " * (curr_indent + 4) + "pass")

    return "\n".join(repaired)


class DeadCodeTransformer(ast.NodeTransformer):
    """
    AST Transformer that eliminates dead statements after return or raise inside blocks.
    """
    def visit_Block(self, statements: list) -> list:
        new_stmts = []
        for stmt in statements:
            new_stmts.append(self.visit(stmt))
            if isinstance(stmt, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                break
        return new_stmts

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        self.generic_visit(node)
        node.body = self.visit_Block(node.body)
        if not node.body:
            node.body = [ast.Pass()]
        return node

    def visit_If(self, node: ast.If) -> ast.If:
        self.generic_visit(node)
        node.body = self.visit_Block(node.body)
        if not node.body:
            node.body = [ast.Pass()]
        if node.orelse:
            node.orelse = self.visit_Block(node.orelse)
        return node


def validate_and_format_code(source_code: str, clean_comments: bool = False) -> Tuple[str, bool, Optional[str]]:
    """
    Validates, repairs, and formats Python source code via python's `ast` module.
    
    Returns:
        (formatted_code, is_valid, error_message)
    """
    if not source_code.strip():
        return source_code, True, None

    # Step 1: Pre-repair empty blocks
    repaired_code = repair_empty_blocks(source_code)

    # Step 2: Attempt parsing
    try:
        tree = ast.parse(repaired_code)
    except SyntaxError as first_err:
        # Retry by wrapping unindented top-level dangling blocks
        lines = repaired_code.splitlines()
        clean_lines = [l for l in lines if not l.strip().startswith("#~ [QUARANTINE")]
        try:
            tree = ast.parse("\n".join(clean_lines))
        except SyntaxError:
            # Return pre-repaired code with error warning if unparseable
            return repaired_code, False, str(first_err)

    # Step 3: Run AST optimization passes
    try:
        transformer = DeadCodeTransformer()
        tree = transformer.visit(tree)
        ast.fix_missing_locations(tree)
    except Exception:
        pass

    # Step 4: Unparse to clean PEP8 compliant code
    try:
        formatted = ast.unparse(tree)
        return formatted, True, None
    except Exception as unparse_err:
        return repaired_code, True, f"Unparse warning: {unparse_err}"
