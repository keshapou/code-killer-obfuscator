import clang.cindex

class Ast:
    def __init__(self, code, filename):
        index = clang.cindex.Index.create()
        self.filename = filename
        self.tu = index.parse(filename, unsaved_files=[(filename, code)], options=0)

    def get_top_level_pos(self, kind_filter=None):
        res = []
        for child in self.tu.cursor.get_children():
            if child.location.file.name != self.filename:
                continue
            if kind_filter is not None and child.kind not in kind_filter:
                continue
            ex = child.extent
            res.append((ex.start.offset, ex.end.offset))
        return res

if __name__ == "__main__":
    filename = "./test_data/simple/simple_func.cpp"
    code = open(filename).read()
    a = Ast(code, filename)
    print(a.get_top_level_pos())
