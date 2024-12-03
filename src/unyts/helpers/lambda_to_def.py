def lambda_to_def(code_line:str) -> str:
    
    from_unit_i = code_line.index("network.get_node(") + len("network.get_node(")
    from_unit_f = code_line[from_unit_i:].index("),") + from_unit_i
    from_unit = code_line[from_unit_i: from_unit_f][1:-1].replace(' ', '_')
    
    to_unit_i = code_line[from_unit_f:].index("network.get_node(") + len("network.get_node(") + from_unit_f
    to_unit_f = code_line[to_unit_i:].index("),") + to_unit_i
    to_unit = code_line[to_unit_i: to_unit_f][1:-1].replace(' ', '_')
    
    lambda_i = code_line.index('lambda ') + len('lambda ')
    lambda_f = (code_line[lambda_i:].index('))') if '))' in code_line[lambda_i:] else code_line[lambda_i:].index('\n')) + lambda_i
    parenthesis = code_line[lambda_i: lambda_f].count('(') - code_line[lambda_i: lambda_f].count(')')
    lambda_code = code_line[lambda_i: lambda_f + parenthesis]
    
    variable = lambda_code[:lambda_code.index(':')].strip()
    return_code = lambda_code[lambda_code.index(':')+1:].strip()
    if return_code.endswith(','):
        comma = ','
        return_code = return_code[:-1]
    else:
        comma = ''
    
    if variable == return_code:
        def_name = f'equality{comma}'
        lambda_def = f"""def {def_name}(x):\n    return x\n"""
        
    else:
        def_name = f"{from_unit.replace('/', '_slash_').replace('*', '_star_')}__to__{to_unit.replace('/', '_slash_').replace('*', '_star_')}{comma}"
        lambda_def = f'''def {def_name}({from_unit.replace('/', '_slash_').replace('*', '_star_')}):\n    """"\n    conversion of lambda: \n      {lambda_code}\n    """\n    {variable} = {from_unit.replace('/', '_slash_').replace('*', '_star_')}\n    return {return_code}\n'''
    
    return lambda_def, lambda_i - len('lambda '), lambda_f, def_name
    

def read_database(file_path:str=None):
    if file_path is None:
        file_path = r"D:\git\unyts\src\unyts\database.py"
    with open(file_path, 'r') as f:
        file_code = f.readlines()
    return file_code


def convert_code():
    file_code = read_database()
    
    def_conversions = []
    
    new_code = [None] * len(file_code)
    
    for i, line in enumerate(file_code):
        if 'lambda ' in line:
            try:
                lambda_def, lambda_i, lambda_f, def_name = lambda_to_def(line)
            except ValueError:
                print("source line", i)
                raise ValueError
            if def_name != 'equality':
                def_conversions.append(lambda_def)
            line = f"{line[:lambda_i]}{def_name}{line[lambda_f:]}"
        
        new_code[i] = line
        
    with open(r"/unyts/units/def_conversions.py", 'w') as f:
        f.write("\n".join(def_conversions))
    
    with open(r"D:\git\unyts\src\unyts\database_def.py", 'w') as f:
        f.write("\n".join(new_code))
        
        
def convert_code_text():
    file_code = "".join(read_database())
    
    def_conversions = []

    new_code = ""
    
    remaining_code = file_code
    
    while "network.add_edge(" in remaining_code:
        i = remaining_code.index("network.add_edge(")
        new_code += remaining_code[:i]
        remaining_code = remaining_code[i:]
        
        f, count = len("network.add_edge("), 1
        while count > 0 and f < len(remaining_code):
            if remaining_code[f] == ')':
                count -= 1
            elif remaining_code[f] == '(':
                count += 1
            f += 1
        f += 1
        
        line = remaining_code[: f]
        remaining_code = remaining_code[f:]
        
        if 'lambda ' in line:
            try:
                lambda_def, lambda_i, lambda_f, def_name = lambda_to_def(line)
            except ValueError:
                print("source line", new_code.count('\n'))
                raise ValueError
            if def_name != 'equality':
                def_conversions.append(lambda_def)
            line = f"{line[:lambda_i]}{def_name}{line[lambda_f:]}"
        
        new_code += line
        
    new_code += remaining_code
        
        
    with open(r"D:/git/unyts/src/unyts/def_conversions.py", 'w') as f:
        f.write("\n".join(def_conversions))
    
    with open(r"D:\git\unyts\src\unyts\database_def.py", 'w') as f:
        f.write("".join(new_code))


convert_code_text()