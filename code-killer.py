import transform
import renamer
import os
import sys
import argparse
import pathlib

def get_output_path(path: pathlib.Path, input_path, output_path):
    res = output_path / path.relative_to(input_path)
    res.parent.mkdir(parents=True, exist_ok=True)
    return str(res)

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument('-var', action='store_true', help="Добавлять неиспользуемые переменные")
    args.add_argument('-comm', action='store_true', help="Добавлять комментарии")
    args.add_argument('-rename_prefix', help="Если указан, то переименовывает символы в файле и добавляет префикс")
    args.add_argument('input', help="Входная директория")
    args.add_argument('output', help="Выходная директория")

    cmd = args.parse_args()
    if cmd.var:
        transform.cfg.ALLOW_USELESS_VARIABLES_IN_INPUT_CODE = True

    if cmd.comm:
        transform.cfg.ALLOW_COMMENTS = True

    tr = transform.Transformer()

    folder = pathlib.Path(cmd.input)

    for f in folder.glob("**/*.c"):
        output_path = get_output_path(f, cmd.input, cmd.output)
        print("\n\nNow proocessing", f, ", will be saved to", output_path)
        try:
            if type(cmd.rename_prefix) == str:
                file_to_obf = renamer.add_prefix_to_file(f, cmd.rename_prefix)
                renamer.rename(str(f), file_to_obf)

                tr.transform_code(file_to_obf, output_path)
                os.system(f'rm {file_to_obf}')
            else:
                tr.transform_code(str(f), output_path)
        except KeyboardInterrupt:
            print(f"User skip {f}")
        except Exception as e:
            print(f"On {f} exception {e}, skipped")
