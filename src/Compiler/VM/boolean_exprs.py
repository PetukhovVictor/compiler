# -*- coding: utf-8 -*-

from src.VM.commands import *

from Helpers.environment import *
from Helpers.assembler import Commands

def relop_bexp(commands, env, op, left, right):
    left.compile_vm(commands, env)
    right.compile_vm(commands, env)
    if op == '==':
        value = Commands.gen(Compare, 0)
    elif op == '!=':
        value = Commands.gen(Compare, 1)
    elif op == '<':
        value = Commands.gen(Compare, 2)
    elif op == '>':
        value = Commands.gen(Compare, 3)
    elif op == '<=':
        value = Commands.gen(Compare, 4)
    elif op == '>=':
        value = Commands.gen(Compare, 5)
    else:
        raise RuntimeError('unknown operator: ' + op)
    commands.append(value)

def and_bexp(commands, env, left, right):
    end_bexp_label = Environment.create_label(env)
    end_bexp_false_label = Environment.create_label(env)
    left.compile_vm(commands, env)
    commands.add(Push, 0)
    commands.add(Compare, 0)

    # Если первый операнд == 0, второй уже не проверяем,
    # а сразу переходим к метке ложного результата.
    commands.add(Jnz, end_bexp_false_label)

    # Иначе будем проверять и второй.
    right.compile_vm(commands, env)
    commands.add(Push, 0)
    commands.add(Compare, 0)

    # Если второй операнд == 0, то переходим к метке ложного результата.
    commands.add(Jnz, end_bexp_false_label)

    # Если оба операнда = 1, то в целом результат выполнения && - 1 - его и пишем в стек
    # и переходим к метке полного завершения выполнения && (минуя секцию ложного результата).
    commands.add(Push, 1)
    commands.add(Jump, end_bexp_label)

    # Секция ложного результата, пишем в стек 0.
    commands.add(Label, end_bexp_false_label)
    commands.add(Push, 0)

    # Полное завершения выполнения &&.
    commands.add(Label, end_bexp_label)

def or_bexp(commands, env, left, right):
    end_bexp_label = Environment.create_label(env)
    end_bexp_true_label = Environment.create_label(env)
    left.compile_vm(commands, env)
    commands.add(Push, 0)
    commands.add(Compare, 1)

    # Если первый операнд != 0, второй уже не проверяем,
    # а сразу переходим к метке истинного результата.
    commands.add(Jnz, end_bexp_true_label)

    # Иначе будем проверять и второй.
    right.compile_vm(commands, env)
    commands.add(Push, 0)
    commands.add(Compare, 1)

    # Если второй операнд != 0, то переходим к метке истинного результата.
    commands.add(Jnz, end_bexp_true_label)

    # Если оба операнда = 0, то в целом результат выполнения or - 0 - его и пишем в стек
    # и переходим к метке полного завершения выполнения or (минуя секцию истинного результата).
    commands.add(Push, 0)
    commands.add(Jump, end_bexp_label)

    # Секция истинного результата, пишем в стек 1.
    commands.add(Label, end_bexp_true_label)
    commands.add(Push, 1)

    # Полное завершения выполнения or.
    commands.add(Label, end_bexp_label)

def not_bexp(commands, env, exp):
    end_bexp_label = Environment.create_label(env)
    end_bexp_false_label = Environment.create_label(env)
    exp.compile_vm(commands, env)
    commands.add(Push, 0)
    commands.add(Compare, 0)

    # Если операнд == 0, переходим в секцию ложного результата.
    commands.add(Jnz, end_bexp_false_label)

    # Секция истинного результата, пишем в стек 1.
    commands.add(Push, 1)
    commands.add(Jump, end_bexp_label)

    # Секция ложного результата, пишем в стек 0.
    commands.add(Label, end_bexp_false_label)
    commands.add(Push, 0)

    # Полное завершения выполнения оператора not.
    commands.add(Label, end_bexp_label)
