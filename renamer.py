import sys
import clang.cindex
import os
import random
import string
import re
import pathlib

process_file_name = ""
keyword_datatypes = ['int', 'double', 'float', 'char']

def filter_name(name):
    d = ''
    if '(' in name:
        d = '('
    elif ' ' in name:
        d = ' '
    elif '[' in name:
        d = '['
    else:
        return name

    i = name.index(d)
    return name[:i].replace(d, '')


def get_qualifier_name(typnode):
    parts_name = []
    typnode = typnode.get_declaration()
    parts_name.append(typnode.spelling)

    tp = typnode.semantic_parent
    while tp is not None:
        if tp.kind == clang.cindex.CursorKind.NAMESPACE:
            parts_name.append(tp.spelling)


        tp = tp.semantic_parent
    parts_name.reverse()
    return '::'.join(parts_name)


def get_filename(filepath):
    if type(filepath) != str:
        filepath = str(filepath)
    return filepath.split('/')[-1]


def traverse(node, deep, name_offset, datatypes, literals):
    off = node.location.offset
    match_decl_kind = set([clang.cindex.CursorKind.FUNCTION_DECL, 
                            clang.cindex.CursorKind.PARM_DECL, 
                            clang.cindex.CursorKind.VAR_DECL,
                            ])

    nodefile = get_filename(node.location.file)

    if nodefile == process_file_name:
        if node.kind == clang.cindex.CursorKind.STRING_LITERAL or node.kind == clang.cindex.CursorKind.CHARACTER_LITERAL:
            # print(f"{node.displayname}\t\t\t\t{node.kind}")
            literals.append(node.displayname)

    if node.kind in match_decl_kind:
        if nodefile == process_file_name:
            tokens = node.get_tokens()
            first_token = next(tokens)
            # print('{}Found {} {} in {} => {} kind={} {} LOCATION {}'.format('  ' * deep, node.type.spelling, node.displayname, f"{node.location.line}:{node.location.column}", off, node.kind, first_token.kind, node.location.file))
            
            name_offset[off] = filter_name(node.displayname)
            datatypes.add(filter_name(get_qualifier_name(node.type)))

    for child in node.get_children():
        traverse(child, deep + 1, name_offset, datatypes, literals)

    return name_offset, datatypes, literals

def gen_new_names(off_name):
    off_new_names = {}
    letters = string.ascii_letters + '_'

    for key in off_name:
        if off_name[key] == 'main':
            off_new_names == off_name[key]
            continue
        off_new_names[key] = ''.join(random.choice(letters) for i in range(random.randrange(10, 15)))

    return off_new_names

def gen_new_datatypes(datatypes):
    new_datatypes = {}
    letters = string.ascii_letters + '_'

    for dt in datatypes:
        if dt == "":
            continue
        new_datatypes[dt] = ''.join(random.choice(letters) for i in range(random.randrange(10, 15)))

    return new_datatypes

def remove_comments(source_code):
    with open(source_code) as fin:
        data = fin.read()
        data = re.sub(re.compile(r"([\n\s]*\/\/.*)|(\/\*.*\*\/)"), "" , data)

    with open(source_code, 'w') as fout:
        fout.seek(0)
        fout.write(data)

    return data

def include_defines(source_code, datatypes):
    with open(source_code, 'r') as fin:
        data = fin.read()    

    with open(source_code, 'w') as fout:
        for key in datatypes:
            data = f'#define {datatypes[key]}\t{key}\n' + data
        fout.write(data)


def add_prefix_to_file(filepath, prefix):
    path = pathlib.Path(filepath)
    parts = list(path.parts[:-1])
    parts.append(f"{prefix}{path.parts[-1]}")
    return '/'.join(parts)


def rename(filepath_in, filepath_out):
    global process_file_name
    try:
        filepath_tmp = add_prefix_to_file(filepath_in, "rentmp_")

        index = clang.cindex.Index.create()
        tu = index.parse(filepath_in)

        process_file_name = get_filename(filepath_in)

        name_offset, datatypes, literals = traverse(tu.cursor, 0, {}, set(), [])

        # [ print(x) for x in literals ]

        new_datatypes = gen_new_datatypes(datatypes)

        new_names_offset = gen_new_names(name_offset)

        # print(datatypes)
        # sys.exit(0)

        cmd = 'clang-rename-6.0 '
        for key in new_names_offset:
            cmd += f'-offset={key} -new-name=\"{new_names_offset[key]}\" '

        cmd += f'{filepath_in} > {filepath_tmp} 2>>rename1.log'
        # print("\t\t\t", cmd)

        os.system(cmd)

        cmd = 'clang-rename-6.0 '
        # print(new_datatypes)
        # print(keyword_datatypes)
        names = 0
        for key in new_datatypes:
            if key in keyword_datatypes:
                continue
            cmd += f'-qualified-name=\"{key}\" -new-name=\"{new_datatypes[key]}\" '
            names += 1

        cmd += f'{filepath_tmp} > {filepath_out} 2>>rename2.log'
        cmd += f' && rm {filepath_tmp}'
        # print("\t\t\t", cmd)

        if names != 0:
            os.system(cmd)
        else:
            os.system(f"mv {filepath_tmp} {filepath_out}")

        include_defines(filepath_out, new_datatypes)
    except Exception as e:
        print("Exception", e)
        print("Renaming skipped")
        os.system(f"cp {filepath_in} {filepath_out}")

if __name__ == "__main__":
    rename(sys.argv[1], add_prefix_to_file(sys.argv[1], "rename_"))
