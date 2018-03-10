# -*- coding: utf-8 -*-

ARGS_SEPARATOR = ' '

Push = 'PUSH'
Pop = 'POP'
Nop = 'NOP'
Dup = 'DUP'
Load = 'LOAD'
BLoad = 'BLOAD'
DLoad = 'DLOAD'
DBLoad = 'DBLOAD'
Store = 'STORE'
BStore = 'BSTORE'
DStore = 'DSTORE'
DBStore = 'DBSTORE'
Add = 'ADD'
Mul = 'MUL'
Sub = 'SUB'
Div = 'DIV'
Mod = 'MOD'
Invert = 'INVERT'
Compare = 'COMPARE'
Label = 'LABEL'
Jump = 'JUMP'
Jz = 'JZ'
Jnz = 'JNZ'
Read = 'READ'
Write = 'WRITE'
Enter = 'ENTER'
Call = 'CALL'
Function = 'FUNCTION'
Return = 'RETURN'
Malloc = 'MALLOC'
DMalloc = 'DMALLOC'
Log = 'LOG'


class Commands(list):
    """ Добалвение команды в список команд для стековой машины """
    def add(self, command, argument=None):
        self.append(self.gen(command, argument))
        return self

    """ Генерация строкового представления заданной команды для стековой машины """
    @staticmethod
    def gen(command, argument=None):
        argument = '' if argument is None else ARGS_SEPARATOR + str(argument)
        return command + argument

    """ Генерация строкового представления заданной команды для стековой машины """
    def push_value(self, value, value_type):
        self.add(Push, value)
        self.add(Push, value_type)

    """ Генерация строкового представления заданной команды для стековой машины """
    def pop_value(self):
        self.add(Pop)
        self.add(Pop)

    """ Генерация строкового представления заданной команды для стековой машины """
    def load_value(self, variable, only_value=False):
        if not only_value:
            self.add(Load, variable)
        self.add(Load, variable + 1)

    """ Генерация строкового представления заданной команды для стековой машины """
    def store_value(self, variable, type=None, type_variable=None):
        if type is not None:
            self.add(Push, type)
        elif type_variable:
            self.add(Load, type_variable)
        self.add(Push, variable)
        self.add(BStore, 1)
        self.add(Store, variable)

    """ Генерация строкового представления заданной команды для стековой машины """
    def bload_value(self, data, only_value=False):
        variable = data.var()

        if not only_value:
            self.add(Dup)
            self.add(Store, variable)
            self.add(BLoad, 0)
            self.add(Load, variable)
        self.add(BLoad, 1)

    """ Генерация строкового представления заданной команды для стековой машины """
    def bstore_value(self, data):
        variable = data.var()

        self.add(Dup)
        self.add(Store, variable)
        self.add(BStore, 0)
        self.add(Load, variable)
        self.add(BStore, 1)

    """ Генерация строкового представления заданной команды для стековой машины """
    def dbload_value(self, value_type, value=0):
        self.add(DBLoad, value)
        self.add(Push, value_type)

    """ Генерация строкового представления заданной команды для стековой машины """
    def compare(self, compare_type):
        self.add(Compare, compare_type)
        self.add(Pop)

    def clean_type(self):
        self.add(Pop)

    def set_and_return_type(self, value_type):
        self.add(Push, value_type)

        return value_type

    def get_type(self, data):
        variable_type = data.var()
        self.add(Store, variable_type)
        return variable_type
