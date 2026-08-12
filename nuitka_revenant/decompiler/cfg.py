"""
Control Flow Graph (CFG) and SSA/Value Track Engine for REVENANT.
Structures disassembler instructions into basic blocks and tracks register states.
"""

from typing import Dict, List, Set, Tuple, Optional, Any


class BasicBlock:
    def __init__(self, start_addr: int):
        self.start_addr: int = start_addr
        self.end_addr: int = start_addr
        self.instructions: List[Any] = []
        self.predecessors: Set[int] = set()
        self.successors: Set[int] = set()
        self.is_terminal: bool = False

    def add_instruction(self, insn: Any):
        self.instructions.append(insn)
        self.end_addr = insn.address + insn.size

    def __repr__(self):
        return f"<BasicBlock 0x{self.start_addr:x}..0x{self.end_addr:x} (insns={len(self.instructions)})>"


class ControlFlowGraph:
    def __init__(self, entry_addr: int = 0):
        self.entry_addr: int = entry_addr
        self.blocks: Dict[int, BasicBlock] = {}

    def get_or_create_block(self, start_addr: int) -> BasicBlock:
        if start_addr not in self.blocks:
            self.blocks[start_addr] = BasicBlock(start_addr)
        return self.blocks[start_addr]

    def build_from_instructions(self, instructions: List[Any]) -> 'ControlFlowGraph':
        if not instructions:
            return self

        self.entry_addr = instructions[0].address
        
        # 1. Identify block split targets (jump destinations and instructions after branches)
        split_addrs: Set[int] = {self.entry_addr}
        
        branch_mnemonics = {
            'jmp', 'je', 'jne', 'jz', 'jnz', 'js', 'jns', 'jo', 'jno',
            'jb', 'jnb', 'jae', 'jbe', 'ja', 'jl', 'jle', 'ge', 'g', 'call', 'ret'
        }

        for i, insn in enumerate(instructions):
            mnemonic = insn.mnemonic.lower()
            if mnemonic in branch_mnemonics:
                # Target operand if direct jump
                try:
                    if insn.op_str.startswith('0x'):
                        target = int(insn.op_str, 16)
                        split_addrs.add(target)
                except ValueError:
                    pass

                # Next instruction after branch is a split start
                if i + 1 < len(instructions):
                    split_addrs.add(instructions[i + 1].address)

        # 2. Form basic blocks
        current_block: Optional[BasicBlock] = None

        for insn in instructions:
            addr = insn.address
            if addr in split_addrs or current_block is None:
                if current_block and not current_block.instructions:
                    pass
                current_block = self.get_or_create_block(addr)

            current_block.add_instruction(insn)

            mnemonic = insn.mnemonic.lower()
            if mnemonic == 'ret':
                current_block.is_terminal = True
            elif mnemonic in branch_mnemonics and mnemonic != 'call':
                try:
                    if insn.op_str.startswith('0x'):
                        target = int(insn.op_str, 16)
                        succ = self.get_or_create_block(target)
                        current_block.successors.add(target)
                        succ.predecessors.add(current_block.start_addr)
                except ValueError:
                    pass

                if mnemonic != 'jmp':
                    # Fall-through successor
                    next_addr = insn.address + insn.size
                    succ = self.get_or_create_block(next_addr)
                    current_block.successors.add(next_addr)
                    succ.predecessors.add(current_block.start_addr)

        return self

    def get_topological_order(self) -> List[BasicBlock]:
        """Returns basic blocks sorted by address order."""
        return [self.blocks[k] for k in sorted(self.blocks.keys())]

    def detect_loops(self) -> List[Tuple[int, int]]:
        """
        Detects back-edges (successors pointing to an earlier basic block address).
        Returns list of (source_addr, target_header_addr).
        """
        loops = []
        for block_addr, block in self.blocks.items():
            for succ_addr in block.successors:
                if succ_addr <= block_addr:
                    loops.append((block_addr, succ_addr))
        return loops


class RegisterStateTracker:
    """
    Simulates register and stack state during disassembly execution.
    """
    def __init__(self):
        self.registers: Dict[str, Any] = {}
        self.stack_slots: Dict[int, Any] = {}

    def set_register(self, reg_name: str, value: Any):
        self.registers[reg_name.lower()] = value

    def get_register(self, reg_name: str, default: Any = None) -> Any:
        return self.registers.get(reg_name.lower(), default)

    def set_stack(self, offset: int, value: Any):
        self.stack_slots[offset] = value

    def get_stack(self, offset: int, default: Any = None) -> Any:
        return self.stack_slots.get(offset, default)

    def clear(self):
        self.registers.clear()
        self.stack_slots.clear()
