# write your code here
import sys
import os
import re
import ast

def check_s002(string):
    ident_counter = 0
    if string[0] != ' ':
        return False
    for i in string:
        if i == ' ':
            ident_counter += 1
        else:
            break
    if (ident_counter % 4) == 0:
        return False
    else:
        return True


def check_s003(string):
    if ';' not in string or not string:
        return False
    else:
        no_comment = string[:string.find('#')].strip()
        if no_comment and no_comment[-1] == r';':
            return True
        else:
            return False


def check_s004(string):
    if '#' not in string:
        return False
    else:
        strings = string.split('#')
        if not strings[0].strip():
            return False
        else:
            if strings[0][-2] != ' ':
                return True


def check_s005(string):
    if 'todo' not in string.lower() or '#' not in string:
        return False
    elif string.find('#') > string.lower().find('todo'):
        return False
    else:
        return True


def check_s007(string):
    if re.match(r'class|def', string) is None:
        return False
    elif re.match(r'(class|def)\s\s+', string):
        return f"S007 Too many spaces after '{re.match(r'(class|def)', string).group(0)}'"


def check_s008(string):
    if re.match(r'class\s', string) is None:
        return False
    elif re.match(r'class\s+(\w+)', string):
        match_008 = re.match(r'[A-Z][A-Za-z0-9]+', re.match(r'class\s+(\w+)', string).group(1))
        name = re.match(r'class\s+(\w+)', string).group(1)
        if match_008 is None:
            return f"S008 Class name '{name}' should be written in CamelCase"
        else:
            return False


def check_s009(string):
    if re.match(r'def\s', string) is None:
        return False
    elif re.match(r'def\s+(\w+)', string):
        match_009 = re.match(r'([a-z]|_)\w+', re.match(r'def\s+(\w+)', string).group(1))
        name = re.match(r'def\s+(\w+)', string).group(1)
        if match_009 is None:
            return f"S009 Function name '{name}' should be written in snake_case"
        else:
            return False


def check_file(f_name):
    with open(f_name, 'r', encoding='utf-8') as file:
        total_errs.setdefault(f_name, [])
        empty_lines = 0
        errors = {}
        code = file.read()
        file.seek(0)
        for n, line in enumerate(file):
            errors.setdefault(n + 1, [])
            if line.strip('\n'):
                if len(line) > 79:
                    errors[n + 1].append('S001 Too long')
                if check_s002(line):
                    errors[n + 1].append('S002 Indentation is not a multiple of four')
                if check_s003(line):
                    errors[n + 1].append('S003 Unnecessary semicolon')
                if check_s004(line):
                    errors[n + 1].append('S004 At least two spaces required before inline comments')
                if check_s005(line):
                    errors[n + 1].append('S005 TODO found')
                if empty_lines > 2:
                    errors[n + 1].append('S006 More than two blank lines used before this line')
                if re.match(r'class|def', line.lstrip()):
                    if check_s007(line.lstrip()):
                        errors[n + 1].append(check_s007(line.lstrip()))
                    if check_s008(line.lstrip()):
                        errors[n + 1].append(check_s008(line.lstrip()))
                    if check_s009(line.lstrip()):
                        errors[n + 1].append(check_s009(line.lstrip()))
                empty_lines = 0
            else:
                empty_lines += 1

        for k, v in errors.items():
            if v:
                for e in v:
                    total_errs[f_name].append(f'Line {k}: {e}')

        tree = ast.parse(code)
        # print(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # if re.match(r'([a-z]|_)\w+', node.name) is None:
                #     print(node.name, node.lineno, 'issues - 1')
                for arg in ast.walk(node):
                    if isinstance(arg, ast.Assign):
                        for name in arg.targets:
                            if isinstance(name, ast.Attribute) and re.match(r'([a-z]|_)\w+', name.attr) is None:
                                print(name.attr, arg.lineno, 'issues - 2')
                            if isinstance(name, ast.Name) and re.match(r'([a-z]|_)\w+', name.id) is None:
                                # print(name.id, arg.lineno, 'issues - 21')
                                total_errs[f_name].append(
                                    f'Line {arg.lineno}: S011 Variable {name.id} should be written in snake_case')
                    if isinstance(arg, ast.arg):
                        if re.match(r'([a-z]|_)\w*', arg.arg) is None:
                            # print(arg.arg, arg.lineno, 'issues  - 3')
                            total_errs[f_name].append(f'Line {arg.lineno}: S010 Argument name {arg.arg} should be '
                                                      f'written in snake_case')
                    if isinstance(arg, ast.List) or isinstance(arg, ast.Set) or isinstance(arg, ast.Dict):
                        # print('mutable on line', arg.lineno, arg)
                        total_errs[f_name].append(f'Line {arg.lineno}: S012 The default argument value is mutable.')




filepath = sys.argv[1]
total_errs = {}
if filepath.endswith('.py'):
    check_file(filepath)
else:
    for dirpath, dirnames, files in os.walk(filepath):
        # print(f'Found directory: {dirpath}')
        for file_name in files:
            # print(dirnames)
            # print(file_name)

            if file_name.endswith('.py'):
                check_file(filepath + r'/' + file_name)


for i in sorted(total_errs):
    for a in total_errs[i]:
        print(f'{i}: {a}')

