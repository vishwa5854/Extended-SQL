import subprocess
from sys import argv, stderr, stdout, exit
import re
from os.path import exists, basename, join
from os import makedirs

TAG: str = "GENERATOR"
emf: bool = True
spaces: str = "    "


def log(tag: str, message: str, error: bool = False) -> None:
    """
    A basic logger which would emit messages to either stdout or stderr based on the error flag
    :param tag: The tag to indicate where the message is coming from
    :param message: The actual message you want to write to the stream
    :param error: Flag to indicate if it is an error message or a normal output
    :return: None
    """
    if error:
        stderr.write(f"[{tag}] {message}\n")
        stderr.flush()
        return
    stdout.write(f"{tag}: {message}\n")
    stdout.flush()


def parse_input(file_name: str) -> dict:
    """
    This function parses the give input file which contains all 6 parameters of PHI into a dictionary
    :param file_name: The name of the input file to be parsed
    :return: dict(str, [str])
    """

    try:
        with open(file_name, 'r') as file:
            lines = file.readlines()
    except Exception as e:
        log(TAG, f"Error while reading given input file: {e}", True)
        exit(1)  # We cannot really move forward without inputs, so we exit with an exit code.

    input_params = {"s": [], "n": 0, "v": [], "f": [], "p": [], "g": ""}
    sections = ["s", "n", "v", "f", "p", "g"]
    section = None

    for line in lines:
        line = line.strip()
        if line[:-1] in sections:
            section = line[:-1]
            continue
        if section == "s":
            input_params[section] = [item.strip() for item in line.split(",")]
        elif section == "n":
            input_params[section] = int(line)
        elif section == "v":
            input_params[section] = [item.strip() for item in line.split(",")]
        elif section == "f":
            input_params[section] = [item.strip() for item in line.split(",")]
        elif section == "p":
            input_params[section].append(line)
        elif section == "g":
            input_params[section] = line
    return input_params


def initialise_predicate_for_default_grouping_variable(input_params: dict) -> [str]:
    """
    This function is responsible for initializing a predicate for default grouping variable (aka group by attributes)
    :param input_params - Dictionary of input parameters loaded from the input file
    :return - List of predicates
    """
    # We are going to add a predicate for the default grouping variable 0 based on the group by attributes
    predicates = input_params["p"]
    predicate_for_default_grouping_variable = ""

    for i in input_params["v"]:
        predicate_for_default_grouping_variable += f"0.{i}=={i} and "

    if predicate_for_default_grouping_variable != "":
        predicate_for_default_grouping_variable = predicate_for_default_grouping_variable[:-5]

    """
    Even though we don't have any aggregate functions for default grouping variable we are still inserting
    an empty string into the predicates at position 0, so that the existing logic for getting predicates
    would be simpler.    
    """
    predicates.insert(0, predicate_for_default_grouping_variable)
    return predicates


def phi(s: [str], n: int, v: [str], f: [str], p: [str], g: str) -> str:
    """
    This function is responsible for creating MF_STRUCT for the given 6 parameters of PHI operator
    :param s - List of projected attributes for the query output
    :param n - Number of grouping variables
    :param v - List of grouping attributes
    :param f - list of sets of aggregate functions. Fi represents a list of aggregate functions for each grouping var
                Eg: [count_1_quant, sum_2_quant, avg_2_quant, max_3_quant]
    :param p - list of predicates to define the ranges for the grouping variables
    :param g - Predicate for having clause
    :return - String containing the body of the _generated.py code with all the table scans and logic
    """
    class_variables = ""
    class_variable_names = "["

    # Init of f members to corresponding values like for max default should be -1, for min default should be MAX_NUM
    # for sum, it would be 0, count = 0, avg = 0
    for j in v:
        class_variables += f"""        {j} = ""\n"""
        class_variable_names += f"'{j}', "
    for j in f:
        aggregate_function = j.split('_')[0]
        class_variable_names += f"'{j}', "

        if aggregate_function == "sum":
            class_variables += f"""        {j} = 0\n"""
        elif aggregate_function == "count":
            class_variables += f"""        {j} = 0\n"""
        elif aggregate_function == "avg":
            sum_var = f"{j}_sum"
            count_var = f"{j}_count"
            class_variables += f"""        {sum_var} = 0\n        {count_var} = 0\n        {j} = 0\n"""
        elif aggregate_function == "max":
            class_variables += f"""        {j} = -1\n"""
        elif aggregate_function == "min":
            class_variables += f"""        {j} = float('inf')\n"""
        else:
            class_variables += f"""        {j} = ""\n"""
    class_variables = class_variables[4:]
    class_variable_names = class_variable_names[:-2] + "]"
    key = "("

    for i in v:
        key += f"row.get('{i}'), "
    key = key[:-2] + ")"
    group_by_values_insertion = ""

    for i in v:
        group_by_values_insertion += f"        data[pos].{i} = row.get('{i}')\n"

    aggregate_loops = ""

    local_variables_for_aggregate = ""

    # We need to insert local variables so that the predicates can use them
    for i in class_variable_names[1: -1].replace("'", '').split(", "):
        local_variables_for_aggregate += f"        {spaces}{i} = data[pos].{i}\n"

    # we are generating for loops for each aggregate function with their respective predicates
    # 1.state='NY'
    for i in f:
        aggregate_function, gv_num, aggregate_attribute = i.split("_")
        predicate = p[int(gv_num)]
        predicate = predicate.replace(f"{gv_num}.", "row.get('")
        predicate = predicate.replace("==", "')==")
        predicate = predicate.replace("!=", "')!=")
        predicate = predicate.replace(">", "')>")
        predicate = predicate.replace("<", "')<")
        aggregate_string = ""

        if aggregate_function == "sum":
            aggregate_string = f"data[pos].{i} += row.get('{aggregate_attribute}')"
        elif aggregate_function == "count":
            aggregate_string = f"data[pos].{i} += 1"
        elif aggregate_function == "min":
            aggregate_string = f"data[pos].{i} = min(data[pos].{i}, row.get('{aggregate_attribute}'))"
        elif aggregate_function == "max":
            aggregate_string = f"data[pos].{i} = max(data[pos].{i}, row.get('{aggregate_attribute}'))"
        elif aggregate_function == "avg":
            sum_var = f"data[pos].{i}_sum"
            count_var = f"data[pos].{i}_count"
            aggregate_string = (f"{sum_var} += row.get('{aggregate_attribute}')\n"
                                f"            {spaces}{count_var} += 1\n\n"
                                f"            {spaces}if {count_var} != 0:\n"
                                f"            {spaces}    data[pos].{i} = {sum_var} / {count_var}\n"
                                f"            {spaces}else:\n"
                                f"            {spaces}    data[pos].{i} = 'Infinity'")

        if emf:
            aggregate_loops += (f"    cur.scroll(0, mode='absolute')\n\n"
                                f"    for row in cur:\n"
                                f"        for pos in range(len(data)):\n"
                                f"{local_variables_for_aggregate}\n        "
                                f"    if {predicate}:\n"
                                f"                {aggregate_string}\n")
        else:
            aggregate_loops += (f"    cur.scroll(0, mode='absolute')\n\n"
                                f"    for row in cur:\n"
                                f"        key = {key}\n"
                                f"        pos = group_by_map.get(key)\n"
                                f"{local_variables_for_aggregate}\n        "
                                f"if {predicate}:\n"
                                f"            {aggregate_string}\n")

    # Prepare the HAVING clause logic
    having_clause = ""
    if g:
        # Replace aggregate function names in the HAVING clause with corresponding attributes
        for agg_func in f:
            g = g.replace(agg_func, f"obj.{agg_func}")
        having_clause = f"    data = [obj for obj in data if {g}]\n"

    def get_arithmetic_operation(attribute):
        # SELECT implementation
        pattern = re.compile(r'([+\-*/])')
        match = pattern.search(attribute)

        if match:
            operator = match.group(1)
            position = match.start()
            operand1 = attribute[:position].strip()
            operand2 = attribute[position + 1:].strip()
            return {"operator": operator, "operand1": operand1, "operand2": operand2, "found": True}
        else:
            return {"found": False}

    operations_dict = {}

    for attr in s:
        operation = get_arithmetic_operation(attr)
        operations_dict[attr] = operation

    select_columns = list(operations_dict.keys())
    # This is an expression of type e.g. avg_1_quant * avg_2_quant
    str_expr = "{getattr(obj, operations_dict[j]['operand1'])} {operations_dict[j]['operator']} {getattr(obj, operations_dict[j]['operand2'])}"
    # This is an expression of type e.g. 2 * avg_1_quant or avg_1_quant * 2
    int_expr = """f\"{operations_dict[j]['operand1']} {operations_dict[j]['operator']} {getattr(obj, operations_dict[j]['operand2'])}" if is_1_int else f"{getattr(obj, operations_dict[j]['operand1'])} {operations_dict[j]['operator']} {operations_dict[j]['operand2']}\""""

    return f"""
    class MFStruct:
    {class_variables}
    data = []
    
    # For all the grouping variables
    group_by_map = dict()
    
    for row in cur:
        key = {key}
        
        if (not group_by_map.get(key)) and (group_by_map.get(key) != 0):
            data.append(MFStruct())
            group_by_map[key] = len(data) - 1
        
        pos = group_by_map.get(key)
{group_by_values_insertion}
    # We need to compute values to the aggregate functions with their corresponding grouping variable predicate.
{aggregate_loops}
    # Apply HAVING clause if present
{having_clause}

    operations_dict = {operations_dict}
    table = PrettyTable()
    table.field_names = {select_columns}
    
    for obj in data:
        temp = []
        
        for j in table.field_names:
            if not operations_dict[j]['found']:
                temp.append(getattr(obj, j))
            else:
                if not (operations_dict[j]['operand1'].isnumeric() or operations_dict[j]['operand2'].isnumeric()):
                    value = eval(f"{str_expr}")
                    temp.append(value)
                else:
                    is_1_int = True if operations_dict[j]['operand1'].isnumeric() else False
                    is_2_int = True if operations_dict[j]['operand2'].isnumeric() else False
                    int_expr = {int_expr}
                    value = eval(int_expr)
                    temp.append(value)
        table.add_row(temp)

    # Printing the table
    return table
"""


def process(input_file: str, run: bool = True) -> None:
    """
    This is the generator code. It should take in the MF structure and generate the code
    needed to run the query. That generated code should be saved to a 
    file (e.g. _generated.py) and then run.
    """
    global spaces

    if not emf:
        spaces = ""

    # Parsing the input params from a file into proper data structures so that our PHI function can use them easily
    input_params = parse_input(f"{input_file}")

    predicates = initialise_predicate_for_default_grouping_variable(input_params)

    body = phi(input_params['s'], input_params['n'], input_params["v"], input_params["f"], predicates,
               input_params["g"])

    # A big string which contains the output python code to get the data for a given params of PHI
    tmp = f"""
import os
import psycopg2
import psycopg2.extras
from prettytable import PrettyTable
from dotenv import load_dotenv

# DO NOT EDIT THIS FILE, IT IS GENERATED BY generator.py


def query():
    load_dotenv()

    user = os.getenv('USERNAMEZ')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')

    conn = psycopg2.connect("dbname="+dbname+" user="+user+" password="+password,
                            cursor_factory=psycopg2.extras.DictCursor, host='127.0.0.1', port='5432')
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales")
    
    _global = []
    {body}
    
if "__main__" == __name__:
    print(query())
    """

    output_folder = "emf-outputs"

    if not emf:
        output_folder = "mf-outputs"
    output_file = f"{basename(input_file.split('.')[0])}_generated.py"
    output_file = join(output_folder, output_file)

    if not exists(output_folder):
        makedirs(output_folder)

    # Write the generated code to a file
    try:
        # With should automatically close the opened file once it is done
        with open(output_file, "w") as _generated_file:
            _generated_file.write(tmp)
    except Exception as e:
        log(TAG, f"Error while writing the generated python code to _generated.py: {e}", True)
        exit(1)  # Since we cannot really do anything at this point it is better to exit with an error

    if run:
        # Execute the generated code
        subprocess.run(["python", output_file])


if "__main__" == __name__:
    if len(argv) == 1:
        log(TAG, "Usage: python generator.py input_file_path run?", True)
        log(TAG, "Input path is required", True)
        exit(1)  # We cannot proceed without an input, so we exit with an error code.
    elif len(argv) == 2:
        process(argv[1])
        exit(0)
    elif len(argv) == 3:
        if argv[2] == "dont-run":
            process(argv[1], False)
            exit(0)
        elif argv[2] == "mf":
            emf = False
            process(argv[1])
            exit(0)
        log(TAG, f"Usage: python generator.py input_file [dont-run?]", True)
        exit(1)
    elif len(argv) == 4:
        if argv[3] == "mf" and argv[2] == "dont-run":
            emf = False
            process(argv[1], False)
            exit(0)
        log(TAG, f"Usage: python generator.py input_file [dont-run?] [mf?]", True)
        exit(1)
