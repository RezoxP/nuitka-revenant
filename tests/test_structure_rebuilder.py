import ast
import pytest
from nuitka_revenant.decompiler.cfg import ControlFlowGraph, BasicBlock
from nuitka_revenant.decompiler.structure_rebuilder import StructureRebuilder


class MockInsn:
    def __init__(self, address, mnemonic, op_str="", size=4):
        self.address = address
        self.mnemonic = mnemonic
        self.op_str = op_str
        self.size = size


def test_structure_rebuilder_linear():
    insns = [
        MockInsn(0x1000, "mov", "rax, rbx"),
        MockInsn(0x1004, "call", "0x2000"),
        MockInsn(0x1008, "ret", ""),
    ]

    cfg = ControlFlowGraph()
    cfg.build_from_instructions(insns)

    rebuilder = StructureRebuilder()
    stmts = rebuilder.restructure_cfg(cfg)

    module = ast.Module(body=stmts, type_ignores=[])
    code = ast.unparse(module)

    assert "rax = rbx" in code
    assert "helper_func()" in code or "0x2000" in code
    assert "return" in code


def test_structure_rebuilder_if_else():
    insns = [
        MockInsn(0x1000, "cmp", "rax, 0"),
        MockInsn(0x1004, "je", "0x1010"),
        MockInsn(0x1008, "mov", "rcx, 1"),
        MockInsn(0x100c, "ret", ""),
        MockInsn(0x1010, "mov", "rcx, 2"),
        MockInsn(0x1014, "ret", ""),
    ]

    cfg = ControlFlowGraph()
    cfg.build_from_instructions(insns)

    rebuilder = StructureRebuilder()
    stmts = rebuilder.restructure_cfg(cfg)

    module = ast.Module(body=stmts, type_ignores=[])
    code = ast.unparse(module)

    assert "if branch_cond is not None:" in code
    assert "rcx = var_1" in code or "rcx = var_2" in code


def test_structure_rebuilder_loop():
    insns = [
        MockInsn(0x1000, "add", "rax, 1"),
        MockInsn(0x1004, "jmp", "0x1000"),
    ]

    cfg = ControlFlowGraph()
    cfg.build_from_instructions(insns)

    rebuilder = StructureRebuilder()
    stmts = rebuilder.restructure_cfg(cfg)

    module = ast.Module(body=stmts, type_ignores=[])
    code = ast.unparse(module)

    assert "while True:" in code
