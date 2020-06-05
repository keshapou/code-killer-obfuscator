import random
import string
import lorem
import re
import utils
import copy
import os
import numpy as np

import cfg
import clang_ast

class Transformer:
    def __init__(self):
        self.source_ = ""
        self.DATATYPES_ = ['int', 'char', 'double', 'float']
        self.OPERATORS_ = {'LOOP' : ['for', 'while', 'do'],
                           'CONDITION' : ['if', 'switch']}
        self.BINARY_OPERATORS_ = ['+', '-', '*', '/', '%']
        self.OPERATIONS_ = ['++', '--']
        self.LOGICAL_OPERATORS_ = ['&&', '||', '==', '<', '>', '<=', '>=']
        self.FUNCTIONS_ = []
        self.CONTEXT_ = {
            'vars' : [],
            'calls' : []          
        }


    def __set_source_file__(self, source):
        self.source_ = source

    def __read_source_code__(self):
        with open(self.source_) as fin:
            return fin.read()

    def __get_code_length__(self, data):
        return len(data)

    def __add_useless_variables__(self, data):
        new_data = ''
        for line in data.splitlines():
            num = random.randrange(1, 5)
            if re.match(r'.*;\s*$', line) and random.choice([True, False]):
                for _ in range(num):
                    var = Variable()
                    random_variable = f'{var.get_type()} {var.get_name()}'
                    random_init = random.choice(['', f'({var.get_value()})', f'={var.get_value()}'])
                    new_data += f'\n{random_variable}{random_init};'
                    new_data += '\n'
            new_data += line + '\n'

        return new_data

    def __gen_context_variables__(self, var_num, context):
        variables = []
        for _ in range(var_num):
            var = Variable()
            context['vars'].append(var)
            random_variable = f'{var.get_type()} {var.get_name()}'
            random_init = random.choice(['', f'({var.get_value()})', f'={var.get_value()}'])

            code = f'{random_variable}{random_init};'
            variables.append(code)

        return variables


    def __add_useless_comments__(self, data):
        new_data = ''
        for line in data.splitlines():
            if re.match(r'.*;\s*$', line) and random.choice([True, False]):
                random_comment = self.__generate_random_string__(3)
                new_data += line + f'/*{random_comment}*/'
            else:
                new_data += line
            
            new_data += '\n'

        return new_data

    def __add_useless_literals__(self, data):
        pass

    def __add_depth__(self, data):
        new_data = ''
        scopes_number = 10
        for i in data:
            if i == '{':
                new_data += i * scopes_number + '\n'
            elif i == '}':
                new_data += i * scopes_number + '\n'
            else:
                new_data += i

        return new_data


    # def __gen_useless_functions__(self, data, context):
    #     all_substr = re.findall(r'(#include\s*<[\s\w\d].*>\s*\n)|(#define\s*[\s\w\d].*\s*\n)', data)
    #     last_match = ''
    #     if all_substr[-1][0] != '':
    #         last_match = all_substr[-1][0]
    #     else:
    #         last_match = all_substr[-1][1]

    #     sub_index = data.find(last_match)
    #     index = data.find('\n', sub_index)+1

    #     random_func_number = random.randrange(20, 40)

    #     new_data = data[:index]
    #     for i in range(random_func_number):
    #         func = Function(context)
    #         function_signature = f'{func.get_type()} {func.get_name()} ({func.params_to_str()})\n{{\n\t{func.get_body()}\n}}'
    #         new_data += '\n\n' + function_signature
    #         self.FUNCTIONS_.append('{func}')
            
    #     new_data += data[index:]
    #     return new_data

    def __gen_context_functions__(self, func_num, context):
        gen_funcs = []
        for i in range(func_num):
            # print(i)
            func = Function(context)
            # struct = Structure()
            context['funcs'].append(func)
            code = f'{func.get_type()} {func.get_name()} ({func.params_to_str()})\n{{\n{func.get_body()}\n}}'
            gen_funcs.append(code)
            # code += f'\n{struct.get_structure()}\n'

        return gen_funcs

    def __gen_context_structs__(self, struct_num, context):
        gen_struct = []
        for i in range(struct_num):
            # print(i)
            struct = Structure()
            # context['structs'].append(func)
            gen_struct.append(struct.get_structure())

        return gen_struct

    def __gen_all_types_vars__(self, context):
        variables = []
        for t in self.DATATYPES_:
            var = Variable(t)
            context['vars'].append(var)
            random_variable = f'{var.get_type()} {var.get_name()}'
            random_init = random.choice(['', f'({var.get_value()})', f'={var.get_value()}'])

            code = f'{random_variable}{random_init};'
            variables.append(code)
        return variables

    def __generate_random_variable__(self, type_var=None):
        random_type = random.choice(self.DATATYPES_) if type_var is None else type_var
        random_name = self.__generate_random_string__()

        if random_type == 'int':
            random_value = f'{random.randint(-100, 100)}'

        if random_type == 'double' or random_type == 'float':
            random_value = f'{round(random.uniform(-100, 100), 2)}'

        if random_type == 'char':
            is_literal = random.choice([True, False])

            if is_literal:
                random_size = random.randrange(2, 10)
                random_value = f'"{self.__generate_random_string__(random_size)}"[{random.randrange(0, random_size)}]'
            else:
                random_value = f"'{random.choice(string.ascii_letters + string.digits + '_,.!?')}'"

        return random_type, random_name, random_value

    def __generate_random_variable_list__(self):
        num = random.randrange(1, 10)
        var_list = []
        for i in range(num):
            var_list.append(Variable())

        return var_list

    def __gen_useless_directives__(self):
        data = []
        for _ in range(random.randrange(5, 15)):
            random_name = self.__generate_random_string__()
            random_number = random.randrange(0, 10)
            code =f'#define {random_name} {random_number}'
            data.append(code)

        return data

    def __remove_comments__(self, data):
        # old_len = len(data)
        data = re.sub(re.compile(r"([\n\s]*\/\/.*)|(\/\*.*\*\/)"), "" , data)
        # print(old_len, len(data))
        return data

    def __rename_variables__(self, data):
        pass

    def __remove_tabs__(self):
        pass

    def __add_tabs__(self, data):
        new_data = ''
        for line in data.splitlines():
            tabs_num = random.randint(3, 10)
            new_data += '\t' * tabs_num + line

        return new_data

    def __add_semicolons__(self, data):
        new_data = ''
        for line in data.splitlines():
            semicolons_num = random.randint(40, 60)
            if line[-2] == ';':
                line += ';' * semicolons_num
                
            new_data += line

        return new_data

    def __find_ratio__(self):
        pass

    def __generate_random_string__(self, size=0):
        if size == 0:
            start = 2
            stop = 10
            size = random.randrange(start, stop)

        chars = string.ascii_letters + string.digits + '_'
        first_symbol = random.choice(string.ascii_letters)

        other_symbols = ''.join(random.choice(chars) for i in range(size))
        return first_symbol + other_symbols

    def __generate_random_function__(self, context):
        context = copy.deepcopy(context)
        random_type_return = random.choice(self.DATATYPES_ + ['void'])
        random_param_number = random.randrange(0, 5)
        random_params = []
        for _ in range(random_param_number):
            par = Variable()
            context['vars'].append(par)
            random_params.append(par)

        function_name = self.__generate_random_string__()

        function_body = self.__generate_random_function_body__(random_type_return, context)

        return random_type_return, function_name, random_params, function_body

    def __generate_random_function_body__(self, rettype, context):

        code = ""

        random_calls = random.choices(context['funcs'], k=utils.rand_count(1, 5, len(context['funcs'])))

        for call in random_calls:
            code += '\t'
            receive = None
            if call.type != 'void' and random.randint(0, 1) == 0:
                receive = Variable()
                receive.type = call.type
                receive.value = None
                code += f"{receive.type} {receive.name} = "

            code += call.name + "("
            for idx, par in enumerate(call.params):
                candidates = Variable.filter_by_type(context['vars'], par.type)
                arg = random.choice(candidates)
                code += arg.name
                if idx != len(call.params) - 1:
                    code += ', '
            code += ");\n"

            if receive is not None:
                context['vars'].append(receive)


            for _ in range(random.randint(0, 3)):
                local_var = Variable()
                context['vars'].append(local_var)
                init = random.choice(("", f" = {local_var.value}", f"({local_var.value})"))
                code += f"\t{local_var.type} {local_var.name}{init};\n"

            if_body = self.__generate_random_if__(context, rettype)

            code += if_body

            code += self.__generate_random_for__(context)

        if rettype == 'void':
            return code

        code += '\treturn '

        target_vars = Variable.filter_by_type(context['vars'], rettype)
        target_vars = [v.name for v in target_vars]
        if len(target_vars) <= 1 or random.randint(0, 2) == 0:
            code += random.choice(target_vars + ["{}"])
        else:
            target_vars = random.choices(target_vars, k=utils.rand_count(2, 4, len(target_vars)))
            for idx, v in enumerate(target_vars):
                code += v
                if idx != len(target_vars) - 1:
                    op = random.choice(Operation.filter_by_type(self.BINARY_OPERATORS_, rettype))
                    code += f" {op} "

        code += ';'
        return code

    def __generate_value_by_type__(self, vartype):
        if vartype == 'int':
            return random.randint(-100, 100)

        if vartype == 'double' or vartype == 'float':
            return round(random.uniform(-100, 100), 2)

        if vartype == 'char':
            return random.choice(string.ascii_letters + string.digits + '_,.!?')


    def __generate__random_operation__(self,context):
        operator = random.choice(self.OPERATORS_)
        operation = ''
        if operator == 'LOOP':
            loop = random.choice(operator[self.OPERATORS_[operator]])
            if loop == 'for':
                pass

            elif loop == 'while':
                pass

            elif loop == 'do':
                pass

        elif operator == 'CONDITION':
            cond = random.choice(operator[self.OPERATORS_[operator]])
            if cond == 'if':
                pass

            elif cond == 'switch':
                pass


    def __generate_random_if__(self, context, rettype):
        context = copy.deepcopy(context)

        if_body = 'if('

        if context['vars'] == []:
            return ''

        var = random.choice(context['vars'])
        if var.type == 'int' or var.type == 'double' or var.type == 'float':
            if_body += f'{var.name}'

            log_op = random.choice(self.LOGICAL_OPERATORS_)
            if_body += log_op
            if_body += '0)\n{\n'

            cond = ''
            if rettype != 'void':
                cond = self.__generate_value_by_type__(rettype)
                if rettype == 'char':
                    cond = f"'{cond}'"
            if_body += f'\treturn {cond};\n}}\n'
        else:
            return ''

        return if_body

    def __generate_random_for__(self, context):
        context = copy.deepcopy(context)
        for_body = 'for('
        type_it = random.choice(['size_t','int'])
        for_body += type_it
        it = self.__generate_random_string__(2)
        for_body += f' {it}=0;{it}'
        for_body += '<=' + f'{random.randint(0, 10)};++{it})\n{{\n'
        for_body += random.choice(context['funcs']).func_call()
        for_body += '\n}\n'

        return for_body


    def __generate_random_switch__(self, context):
        pass

    def __generate_code__(self, data):
        pass


    def __write_in_file__(self, data, fname):
        index = fname.find('.c')
        new_fname = fname[:index] + '_obf' + fname[index:]
        with open(new_fname, 'w') as fout:
            fout.write(data)


    def __strip_empty_strings__(self, data):
        res = []
        for line in data.splitlines():
            line = line.strip()
            if len(line) != 0 and line[0] == '#':
                line += '\n'
            res.append(line)

        return ' '.join(res) 

    def __calc_counts(self, N):
        number = random.uniform(0, 1)
        a = np.random.normal(number, 0.05)
        a = max(0.05, a)
        a = min(0.2, a)

        b = np.random.normal(1-number, 0.05)
        b = max(0.2, b)
        b = min(0.9, b)

        len_vars = N * a
        len_funcs = (N - len_vars) * b
        len_struct = N - len_funcs - len_vars

        count_vars = int(len_vars / cfg.SYM_ON_VAR)
        count_funcs = int(len_funcs / cfg.SYM_ON_FUNC)
        count_struct = int(len_struct / cfg.SYM_ON_STRUCT)

        count_vars = max(cfg.MIN_CONTEX_VARS, count_vars)
        count_funcs = max(cfg.MIN_CONTEX_FUNCS, count_funcs)
        count_struct = max(cfg.MIN_CONTEX_STRUCT, count_struct)

        return count_vars, int(len_vars), count_funcs, int(len_funcs), count_struct, int(len_struct)

    def __accumulate_float(self, arr):
        acc = 0
        for i in range(len(arr)):
            arr[i] += acc
            i_part = int(arr[i])
            acc = arr[i] - i_part
            arr[i] = i_part
        if acc > 0.001:
            arr[0] += 1
        return arr

    def __get_distribution(self, N, count):
        if N == 0:
            return []
        v = count / N
        dist_arr = [v for _ in range(N)]

        return self.__accumulate_float(dist_arr)

    def transform_code(self, source, output_path):
        self.__set_source_file__(source)
        data = self.__read_source_code__()
        print(f'Obfuscating {source:.<98}')
        # print(data)

        available_bytes = len(data) * cfg.SCALE_FACTOR

        # TODO: strip and remove spacing
        data = self.__remove_comments__(data)
        data = self.__strip_empty_strings__(data)

        available_bytes -= len(data)

        context = {
            'vars': [],
            'funcs': []
        }

        directives = self.__gen_useless_directives__()
        data = '\n'.join(directives) + '\n' + data
        print(f"Generating {'directives':.<99}[OK]")


        if cfg.ALLOW_USELESS_VARIABLES_IN_INPUT_CODE:
            data = self.__add_useless_variables__(data)  # TODO: старый подход, но пусть будет
            print(f"Generating {'useless variables':.<99}[OK]")

        print(f"Available symbols: {available_bytes}")
        count_vars, len_vars, count_funcs, len_funcs, count_struct, len_struct = self.__calc_counts(available_bytes)

        print(f"Will be generate: vars {count_vars}[{len_vars} sym], funcs {count_funcs}[{len_funcs} sym], struct {count_struct}[{len_struct}]")

        a = clang_ast.Ast(data, source)
        poss = a.get_top_level_pos()

        dist_vars = self.__get_distribution(len(poss), count_vars)
        dist_funcs = self.__get_distribution(len(poss), count_funcs)
        dist_struct = self.__get_distribution(len(poss), count_struct)


        variables = self.__gen_all_types_vars__(context)
        new_code = '\n'.join(variables) + '\n'
        data = new_code + data
        print(f"Generating {'init variables':.<99}[OK]")

        offset_accum = len(new_code)
        for p, count_vars, count_funcs, count_struct in zip(poss, dist_vars, dist_funcs, dist_struct):
            variables = self.__gen_context_variables__(count_vars, context)
            variables = '\n'.join(variables)

            functions = self.__gen_context_functions__(count_funcs, context)
            functions = '\n'.join(functions)

            structs = self.__gen_context_structs__(count_struct, context)
            structs = '\n'.join(structs)

            new_code = '\n' + variables + '\n' + functions + '\n' + structs + '\n'

            p = p[1] + offset_accum
            data = data[:p] + new_code + data[p:]
            offset_accum += len(new_code)

        print(f"Generating {f'variables and functions':.<99}[OK]")

        if cfg.ALLOW_COMMENTS:
            data = self.__add_useless_comments__(data)
            print(f"Adding {'comments':.<99}[OK]")

        
        data = self.__strip_empty_strings__(data)

        self.__write_in_file__(data, output_path)
        print(f"Writing in file{'':.<91}[OK]")

        return data


class Function:
    def __init__(self, context):
        self.type, self.name, self.params, self.body = Transformer().__generate_random_function__(context)

    def get_type(self):
        return self.type

    def get_name(self):
        return self.name

    def get_params(self):
        return self.params

    def get_body(self):
        return self.body

    def params_to_str(self):
        params = ''
        for var in self.params:
            params += f'{var.type} {var.name}'
            if var != self.params[-1]:
                params += ', '
        
        return params

    def func_call(self):
        call = f'{self.name}('
        for par in self.params:
            call += f'{par.name}'
            if par != self.params[-1]:
                call += ','

        call += ');'

        return call

class Variable:
    def __init__(self, type_var=None):
        self.type, self.name, self.value = Transformer().__generate_random_variable__(type_var)

    def get_type(self):
        return self.type

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

    @staticmethod
    def filter_by_type(seq, targer_type):
        res = [v for v in seq if v.type == targer_type]
        return res

class Operation:
    def __init__(self):
        pass

    @staticmethod
    def filter_by_type(ops, targer_type):
        # маленький костыль для фильтрации операций, которые не разрешены для float/double
        res = [v for v in ops if v != '%' or targer_type not in ('float', 'double')]
        return res

class Context:
    def __init__(self):
        pass

class Structure:
    def __init__(self):
        self.name = Transformer().__generate_random_string__()
        self.params = Transformer().__generate_random_variable_list__()

    def get_structure(self):
        struct = f'struct {self.name}\n{{\n'
        for par in self.params:
            struct += f'\t{par.type} {par.name};\n'
        struct += '\n};'

        return struct
