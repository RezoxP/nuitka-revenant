import pytest
from nuitka_revenant.decompiler.cfg import ControlFlowGraph, RegisterStateTracker, BasicBlock


class MockInsn:
    def __init__(self, address, mnemonic, op_str="", size=4):
        self.address = address
        self.mnemonic = mnemonic
        self.op_str = op_str
        self.size = size


def test_basic_block_and_cfg():
    insns = [
        MockInsn(0x1000, "mov", "rax, rbx"),
        MockInsn(0x1004, "cmp", "rax, 0"),
        MockInsn(0x1008, "je", "0x1014"),
        MockInsn(0x100c, "add", "rax, 1"),
        MockInsn(0x1010, "jmp", "0x1018"),
        MockInsn(0x1014, "sub", "rax, 1"),
        MockInsn(0x1018, "ret", ""),
    ]

    cfg = ControlFlowGraph()
    cfg.build_from_instructions(insns)

    blocks = cfg.get_topological_order()
    assert len(blocks) >= 3
    assert 0x1000 in cfg.blocks
    assert 0x1014 in cfg.blocks
    assert 0x1018 in cfg.blocks


def test_register_state_tracker():
    tracker = RegisterStateTracker()
    tracker.set_register("rax", 0x1234)
    assert tracker.get_register("RAX") == 0x1234

    tracker.set_stack(0x20, "PyObject*")
    assert tracker.get_stack(0x20) == "PyObject*"

    tracker.clear()
    assert tracker.get_register("rax") is None
    assert tracker.get_stack(0x20) is None
