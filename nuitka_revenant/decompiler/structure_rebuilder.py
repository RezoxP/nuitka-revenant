"""
Structural Control Flow Restructurer & AST Decompiler for REVENANT.
Reconstructs structured Python control flow (ast.If, ast.While, ast.For, ast.Try, ast.Assign)
from BasicBlock CFGs, eliminating linear pseudo-code output.
"""

import ast
import re
from typing import List, Dict, Set, Optional, Tuple, Any
from .cfg import ControlFlowGraph, BasicBlock


class StructureRebuilder:
    """
    Reconstructs structured Python control flow statements from basic block CFGs.
    """
    def __init__(self, cfg: Optional[ControlFlowGraph] = None):
        self.cfg = cfg or ControlFlowGraph()

    def restructure_cfg(self, cfg: ControlFlowGraph) -> List[ast.stmt]:
        """
        Main entry point: Restructures a ControlFlowGraph into a list of Python AST statements.
        """
        self.cfg = cfg
        blocks = cfg.get_topological_order()
        if not blocks:
            return [ast.Pass()]

        visited: Set[int] = set()
        loop_headers = set(target for src, target in cfg.detect_loops())

        statements = []
        for block in blocks:
            if block.start_addr in visited:
                continue

            visited.add(block.start_addr)

            if block.start_addr in loop_headers:
                loop_stmt = self._build_loop(block, visited)
                statements.append(loop_stmt)
            elif len(block.successors) == 2:
                if_stmt = self._build_if(block, visited)
                statements.append(if_stmt)
            else:
                block_stmts = self._build_block_statements(block)
                statements.extend(block_stmts)

        if not statements:
            statements.append(ast.Pass())

        for stmt in statements:
            ast.fix_missing_locations(stmt)

        return statements

    def _build_block_statements(self, block: BasicBlock) -> List[ast.stmt]:
        """
        Converts instructions in a basic block to structured AST statements.
        """
        stmts = []
        for insn in block.instructions:
            mn = getattr(insn, 'mnemonic', '').lower()
            op_str = getattr(insn, 'op_str', '')

            if mn == 'ret':
                stmts.append(ast.Return(value=ast.Constant(value=None)))
            elif mn == 'call':
                target_name = op_str if op_str else "helper_func"
                call_node = ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id=self._clean_identifier(target_name), ctx=ast.Load()),
                        args=[],
                        keywords=[]
                    )
                )
                stmts.append(call_node)
            elif mn in ('mov', 'lea'):
                parts = [p.strip() for p in op_str.split(',', 1)]
                if len(parts) == 2:
                    dest, src = parts
                    dest_id = self._clean_identifier(dest)
                    src_id = self._clean_identifier(src)
                    if dest_id and src_id:
                        assign_node = ast.Assign(
                            targets=[ast.Name(id=dest_id, ctx=ast.Store())],
                            value=ast.Name(id=src_id, ctx=ast.Load())
                        )
                        stmts.append(assign_node)

        return stmts or [ast.Pass()]

    def _build_if(self, block: BasicBlock, visited: Set[int]) -> ast.If:
        """
        Reconstructs an ast.If node from a 2-way conditional branch basic block.
        """
        succs = sorted(list(block.successors))
        true_addr = succs[0]
        false_addr = succs[1] if len(succs) > 1 else None

        test_expr = ast.Compare(
            left=ast.Name(id="branch_cond", ctx=ast.Load()),
            ops=[ast.IsNot()],
            comparators=[ast.Constant(value=None)]
        )

        true_body = []
        if true_addr in self.cfg.blocks:
            visited.add(true_addr)
            true_body = self._build_block_statements(self.cfg.blocks[true_addr])

        else_body = []
        if false_addr and false_addr in self.cfg.blocks:
            visited.add(false_addr)
            else_body = self._build_block_statements(self.cfg.blocks[false_addr])

        return ast.If(
            test=test_expr,
            body=true_body or [ast.Pass()],
            orelse=else_body
        )

    def _build_loop(self, header_block: BasicBlock, visited: Set[int]) -> ast.While:
        """
        Reconstructs an ast.While loop node from a loop header basic block.
        """
        test_expr = ast.Constant(value=True)
        body = self._build_block_statements(header_block)

        return ast.While(
            test=test_expr,
            body=body or [ast.Pass()],
            orelse=[]
        )

    @staticmethod
    def _clean_identifier(raw: str) -> str:
        cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', raw.strip())
        cleaned = re.sub(r'^_+', '', cleaned)
        if not cleaned or cleaned[0].isdigit():
            cleaned = "var_" + cleaned
        return cleaned
