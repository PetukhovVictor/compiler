from .code import Code
from .commands import Commands
from .environment import Environment
from .labels import Labels
from .registers import Registers
from .types import Types
from .vars import Vars
from .config import ASM_COMMANDS_SEPARATOR


class Compiler:
    entry_point_label = '_main'
    exit_interrupt = 0x80

    def __init__(self):
        self.environment = Environment()
        self.code = Code(self)
        self.labels = Labels()
        self.vars = Vars(self, self.code, self.environment)
        self.types = Types(self)
        self.target_register = None
        self.runtime = []
        self.externs = []

    def exit(self):
        self.code.add(Commands.PUSH, [0])
        self.code.add(Commands.MOV, [Registers.EAX, 1])
        self.code.add(Commands.SUB, [Registers.ESP, 1])
        self.code.add(Commands.INT, [self.exit_interrupt])

    def add_extern(self, code, names):
        if isinstance(names, list):
            self.externs += names
        else:
            self.externs.append(names)
        self.runtime.append(code)

    def get_externs(self, externs):
        return ''.join(map(lambda f: 'EXTERN %s%s' % (f, ASM_COMMANDS_SEPARATOR), externs))

    def get_section(self, section_name, content):
        return '%sSECTION .%s %s%s' % (ASM_COMMANDS_SEPARATOR, section_name, ASM_COMMANDS_SEPARATOR,
                                       ASM_COMMANDS_SEPARATOR.join(content))

    def get_content(self, content):
        return ASM_COMMANDS_SEPARATOR + ASM_COMMANDS_SEPARATOR.join(content) + ASM_COMMANDS_SEPARATOR

    def get_result(self):
        self.exit()

        externs = self.get_externs(self.externs)
        global_decl = '%sglobal %s' % (ASM_COMMANDS_SEPARATOR, self.entry_point_label)

        labels = self.get_content(self.labels)
        self.code.allocate_stack_memory(self.environment.list['root']['memory'], place=0)
        self.code.add_label(self.entry_point_label, place=0)
        code = self.get_content(self.code.assemble())
        bss = "" if len(self.vars.bss) == 0 else self.get_section("bss", self.vars.bss)

        if len(self.vars.bss) != 0:
            global_decl = "%sSECTION .text%s" % (ASM_COMMANDS_SEPARATOR, ASM_COMMANDS_SEPARATOR) + global_decl

        return externs + bss + global_decl + labels + code

    def get_runtime(self):
        return ASM_COMMANDS_SEPARATOR.join(self.runtime)
