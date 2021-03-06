from .types import Types


class Environment:
    counter = 0         # Function counter
    var_counter = 0     # Function counter
    list = {            # Function list
        'root': {
            'memory': 0,
            'vars': {}
        }
    }
    objects = {}            # Мапа, связывающая переменные с объектами, на которые они ссылаются
    object_list = []
    object_counter = 0
    defined_object = None
    current = None      # The name of the function in which we are currently

    def add_object(self):
        self.object_counter += 1
        return self.object_counter

    def set_return_type(self, type):
        if self.current is None:
            return

        self.list[self.current]['return_type'] = type

    def get_return_type(self, name):
        return self.list[name]['return_type']

    def set_link_object(self, var_name, object_name):
        self.objects[var_name] = object_name

    def get_object_name(self, var_name):
        return self.objects[var_name]

    def get_object_property(self, obj_name, property_name, type):
        return self.var(type, property_name, object_namespace=obj_name)

    def set_args(self, args):
        if self.current is None:
            return

        self.list[self.current]['args'] = args

    def get_args(self, name=None):
        if name is None:
            name = self.current

        return self.list[name]['args'] if name in self.list else None

    def start(self, name):
        self.counter += 1
        self.list[name] = {
            'memory': 0,
            'vars': {},
            'args': None,
            'return_type': Types.NOTHING,
            'number': self.counter,
            'parent': self.list[self.current if self.current else 'root']
        }
        self.current = name

        return self.counter

    def get_parent_local_var(self, name=None, as_object=True):
        env = self.list[self.current if self.current else 'root']

        env = env['parent']
        if name in env['vars']:
            stack_pointer = env['vars'][name]['stack_pointer']
            if as_object:
                var_pointer = {'pointer': 'ebp', 'offset': stack_pointer + 4}
            else:
                var_pointer = 'dword [ebp-%s]' % stack_pointer + 4
        elif 'args' in env:
            var_pointer = 'dword [ebp+%s]' % (env['args'][name] + 2) * 8 - 4 \
                if name in env['args'] else None
        else:
            var_pointer = None

        return var_pointer

    def finish(self):
        need_memory = self.list[self.current]['memory']
        self.current = None

        return need_memory

    def get_number(self, name):
        return self.list[name]['number'] if name in self.list else None

    def get_all_vars(self):
        env = self.list[self.current if self.current else 'root']

        return env['vars']

    def add_parent_local_var(self, type=None, name=None, size=None, object_namespace=None):
        env = self.list[self.current if self.current else 'root']
        env = env['parent']

        if name is None:
            if object_namespace is not None:
                name = 'var_%s_%s' % (object_namespace, self.var_counter)
            else:
                name = 'var_%s' % self.var_counter
            self.var_counter += 1

        if object_namespace is not None:
            name = 'var_%s_%s' % (object_namespace, name)

        if name in env['vars']:
            return self.get_local_var(name, as_object=type is None)

        stack_pointer = env['memory'] + Types.SIZE
        size = size + Types.SIZE * 2 if size else Types.SIZE * 2
        env['vars'][name] = {
            'stack_pointer': stack_pointer,
            'size': size,
            'type': type
        }
        env['memory'] += size

        return self.get_parent_local_var(name)

    def add_local_var(self, type=None, name=None, size=None, object_namespace=None):
        env = self.list[self.current if self.current else 'root']

        if name is None:
            if object_namespace is not None:
                name = 'var_%s_%s' % (object_namespace, self.var_counter)
            else:
                name = 'var_%s' % self.var_counter
            self.var_counter += 1

        if object_namespace is not None:
            name = 'var_%s_%s' % (object_namespace, name)

        if name in env['vars']:
            return self.get_local_var(name, as_object=type is None)

        stack_pointer = env['memory'] + Types.SIZE
        size = size + Types.SIZE * 2 if size else Types.SIZE * 2

        env['vars'][name] = {
            'stack_pointer': stack_pointer,
            'size': size,
            'type': type
        }
        env['memory'] += size

        return self.get_local_var(name, as_object=type is None)

    def get_local_var(self, name=None, as_object=False, env=None):
        env = self.list[self.current if self.current else 'root'] if env is None else env

        if name in env['vars']:
            stack_pointer = env['vars'][name]['stack_pointer']
            if as_object:
                var_pointer = {'pointer': 'ebp', 'offset': stack_pointer + 4}
            else:
                var_pointer = 'dword [ebp-%d]' % (stack_pointer + 4)
        elif 'args' in env:
            var_pointer = 'dword [ebp+%d]' % ((env['args'][name] + 2) * 8 - 4)\
                if name in env['args'] else None
        else:
            var_pointer = None

        return var_pointer

    def update_local_var_type(self, name, type):
        env = self.list[self.current if self.current else 'root']

        if name in env['vars']:
            env['vars'][name]['type'] = type

    def get_arg(self, name=None):
        env = self.list[self.current if self.current else 'root']
        return 'dword [ebp+%d]' % ((env['args'][name] + 2) * 8 - 4)\
            if name in env['args'] else None

    def get_arg_runtime_type(self, name=None):
        env = self.list[self.current if self.current else 'root']
        return 'dword [ebp+%d]' % ((env['args'][name] + 2) * 8 - 8)\
            if name in env['args'] else None

    def get_local_var_runtime_type(self, name=None, as_object=False):
        env = self.list[self.current if self.current else 'root']
        if name in env['vars']:
            type = env['vars'][name]['type']
            stack_pointer = env['vars'][name]['stack_pointer']
            if as_object:
                var_pointer = {'pointer': 'ebp', 'offset': stack_pointer}
            elif type:
                var_pointer = 'dword [ebp-%d]' % stack_pointer
            else:
                var_pointer = 'dword [ebp-%d]' % stack_pointer
        elif 'args' in env:
            var_pointer = self.get_arg_runtime_type(name)
        else:
            var_pointer = None

        return var_pointer

    def get_local_var_type(self, name=None):
        env = self.list[self.current if self.current else 'root']

        return env['vars'][name]['type'] if name in env['vars'] else Types.INT

    def is_exist_local_var(self, name=None):
        env = self.list[self.current if self.current else 'root']

        return name in env['vars']
