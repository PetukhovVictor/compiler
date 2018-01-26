# -*- coding: utf-8 -*-

from .Deep.functions import *


def function(commands, data, name, args, body):
    """ Компиляция функций (объявление, вызов, исполнение, возврат к месту вызова) """
    start_function = data.start_function(name)
    finish_function = data.label()

    # При последовательном выполнении пропускаем выполнение тела функции,
    # т. к. в этом случае это лишь объвление функции, вызов будет позже
    commands.add(Jump, finish_function)

    # На эту метку переходим при вызове
    commands.add(Function, start_function)

    FunctionCompiler.args_write(commands, data, args)

    # Компилируем код тела функции
    body.compile_vm(commands, data)

    # Компилируем конструкцию возврата к месту вызова
    commands.add(Return)\
        .add(Label, finish_function)

    data.finish_function()


def return_statement(commands, data, expr):
    """ Компиляция выражения возврата к месту вызова """
    return_type = expr.compile_vm(commands, data)
    data.set_return_type(return_type)


def call_statement(commands, data, name, args):
    """ Компиляция выражения вызова функции """
    for arg in args.elements:
        arg.compile_vm(commands, data)
    commands.add(Call, data.get_label(name))

    return data.get_return_type(name)
