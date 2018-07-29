# -*- coding: utf-8 -*-

from .types import Types
from ..Helpers.commands import Dup, Store, Push, BLoad, Load, Add, DBLoad, Label, Jump, Pop, Jz


class Loop:
    """ Генератор команд для организации циклов """
    load_commands = {
        'stack': BLoad,
        'heap': DBLoad
    }

    @staticmethod
    def base(commands, data, check_break_condition, callback, load_counter=True, return_counter=False):
        """
        Генерация команд для организации цикла.
        Условие останова - динамическое, передается извне.
        """
        # Создаем метки и переменные, необходимые для прохождения цикла.
        counter = data.var(Types.INT)

        start_label = data.label()
        finish_label = data.label()
        continue_label = data.label()

        # Инициализируем счетчик цикла
        commands.add(Push, 0) \
            .add(Store, counter) \
            .add(Label, start_label)

        # Выполняем тело цикла
        if callback is not None:
            callback(counter, finish_label, continue_label)

        commands.add(Label, continue_label)

        # Инкрементируем счетчик цикла
        commands.add(Load, counter) \
            .add(Push, 1) \
            .add(Add) \
            .add(Store, counter)

        # Выполняем переданное условие останова
        if check_break_condition is not None:
            check_break_condition(start_label, finish_label, counter)

        commands.add(Jump, start_label) \
            .add(Label, finish_label)

        # Если требуется, загружаем на стек количество совершенных итераций
        if load_counter:
            commands.add(Load, counter)

        # Если требуется, возвращаем переменную, в которой содержится кол-во совершенных итераций
        if return_counter:
            return counter

    @staticmethod
    def simple(commands, data, callback, return_counter=False):
        """
        Генерация команд для организация произвольного цикла.
        Критерий отстанова и сам останов должен реализовываться внутри callback.
        """
        return Loop.base(commands, data, None, callback, False, return_counter)

    @staticmethod
    def stack(commands, data, callback, load_counter=True, return_counter=False):
        """
        Генерация команд для организация цикла на стеке.
        Цикл завершается, если на стеке оказалось 0.
        """
        def check_break_condition(a, finish_label, b):
            # Если после выполнения callback на стеке 0 - завершаем цикл.
            commands.add(Dup).add(Jz, finish_label)

        result = Loop.base(commands, data, check_break_condition, callback, load_counter, return_counter)

        # Очищаем оставшийся на стеке 0 (поскольку перед Jz использовали Dup).
        commands.add(Pop)

        return result

    @staticmethod
    def data(commands, data, start_pointer, callback=None, load_counter=True, return_counter=False, memory_type='heap'):
        """
        Генерация команд для организация цикла в памяти.
        Цикл завершается, если в очередной ячейке стековой памяти оказалось 0.
        """
        def check_break_condition(a, finish_label, _counter):
            # Если после выполнения callback в ячейке памяти 0 - завершаем цикл.
            commands.add(Load, start_pointer) \
                .add(Load, _counter) \
                .add(Add) \
                .add(Loop.load_commands[memory_type], 0) \
                .add(Jz, finish_label)

        return Loop.base(commands, data, check_break_condition, callback, load_counter, return_counter)

    @staticmethod
    def data_stack(commands, data, start_pointer, callback=None, load_counter=True, return_counter=False):
        """
        Генерация команд для организация цикла в памяти.
        Цикл завершается, если в очередной ячейке стековой памяти оказалось 0.
        """
        return Loop.data(commands, data, start_pointer, callback, load_counter, return_counter, memory_type='stack')

    @staticmethod
    def data_heap(commands, data, start_pointer, callback=None, load_counter=True, return_counter=False):
        """
        Генерация команд для организация цикла в памяти.
        Цикл завершается, если в очередной ячейке heap-памяти оказалось 0.
        """
        return Loop.data(commands, data, start_pointer, callback, load_counter, return_counter)
