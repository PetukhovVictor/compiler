# -*- coding: utf-8 -*-


class Environment:
    """ Compile-time environment """
    var_counter_root = 0    # Счетчик переменных для stack memory
    var_counter = 0         # Счетчик переменных для stack memory
    vars = {}               # Переменные в stack memory
    label_counter = 0       # Счетчик меток
    labels = {}             # Метки
    objects = {}            # Мапа, связывающая переменные с объектами, на которые они ссылаются

    current_function = None     # Тип данных возвращаемого значения из подпрограммы
    defined_object = None      # Ссылка на описанный объект (используется при компиляции конструкции присваивания)
    context_objects = []        # Ссылка на описанный объект (используется при компиляции конструкции присваивания)

    def set_return_type(self, type):
        if self.current_function is None:
            return

        self.labels[self.current_function]['return_type'] = type

    def get_return_type(self, name):
        return self.labels[name]['return_type']

    def start_function(self, name):
        self.var_counter_root = self.var_counter
        self.var_counter = 0
        start_function = self.label(name)
        self.current_function = name

        return start_function

    def finish_function(self):
        self.var_counter = self.var_counter_root
        self.current_function = None

    def set_link_object(self, var_name, object_name):
        self.objects[var_name] = object_name

    def get_object_name(self, var_name):
        return self.objects[var_name]

    def get_object_property(self, obj_name, property_name, type):
        return self.var(type, property_name, object_namespace=obj_name)

    def label(self, name=None):
        """ Создание новой метки """
        label_number = self.label_counter
        if name:
            self.labels[name] = {
                'number': label_number,
                'return_type': None
            }
        self.label_counter += 1
        return label_number

    def create_var(self, type=None, alias=None, double_size=False, object_namespace=None):
        var_number = self.var_counter
        if alias is not None:
            if object_namespace is not None:
                alias = '!o' + str(object_namespace) + '!' + str(alias)
            elif self.current_function is not None:
                alias = '!' + str(self.current_function) + '!' + str(alias)
            self.vars[alias] = {
                'number': var_number
            }
        self.vars[var_number] = {
            'type': type
        }
        if double_size:
            self.var_counter += 2
        else:
            self.var_counter += 1
        return var_number

    def var(self, type=None, alias=None, double_size=False, object_namespace=None):
        """
        Создание новой переменной в stack memory
        Если name не передано, просто инкрементируем счетчик
        """
        # Если переменная уже существует, возвращаем её
        if self.is_exist_var(alias, object_namespace):
            var_number = self.get_var(alias, object_namespace)
            if type is not None and type != 9:
                self.set_type(var_number, type)
            return var_number
        else:
            return self.create_var(type, alias, double_size, object_namespace)

    def get_label(self, name):
        """ Получение метки по имени """
        return self.labels[name]['number']

    def get_var(self, name, object_namespace=None, is_root=False):
        """ Получение переменной по имени """
        if object_namespace is not None and not is_root:
            name = '!o' + str(object_namespace) + '!' + str(name)
        elif self.current_function is not None and not is_root:
            name = '!' + str(self.current_function) + '!' + str(name)
        if name in self.vars:
            return self.vars[name]['number']
        else:
            return None

    def get_type(self, number):
        """ Получение переменной по имени """
        if number in self.vars:
            return self.vars[number]['type']
        else:
            return None

    def set_type(self, number, type):
        """ Получение переменной по имени """
        if number in self.vars:
            self.vars[number]['type'] = type

    def is_exist_var(self, name, object_namespace=None):
        """ Проверка переменной на существование """
        if object_namespace is not None:
            name = '!o' + str(object_namespace) + '!' + str(name)
        elif self.current_function is not None:
            name = '!' + str(self.current_function) + '!' + str(name)
        return name in self.vars
