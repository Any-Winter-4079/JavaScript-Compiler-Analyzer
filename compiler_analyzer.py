import sys
import re


###############
#   Helpers   #
###############


# ok
def error_handler(code, string_chars=0, value=None, token=None, options=None, lexeme=None, description=None):
    """Writes error to standard output stream, deletes all symbol tables and terminates compilation"""
    global c
    global next_token
    global st_list
    # Lexical error
    if code == 1:
        print("Lexical error: line {}\nValue {} out of range.".format(current_line, value))
    elif code == 2:
        print("Lexical error: line {}\nYour string contains {} characters.\n"
              "String max length of 64 exceeded.".format(current_line, string_chars))
    elif code == 3:
        if not c:
            print("Lexical error: line {}\nString must be closed by '\n"
                  "End of file found, ' expected.".format(current_line, value))
        else:
            print("Lexical error: lines {}-{}\nMultiline strings are not allowed.\n"
                  "End of line found, ' expected.".format(current_line-1, current_line, value))
    elif code == 4:
        print("Lexical error: line {}\nIncorrect modulus assignment.\n"
              "{} found but = expected".format(current_line, c))
    elif code == 5:
        c = "End of File" if not c else c
        c = "End of Line" if c == "\n" else c
        print("Lexical error: line {}\nIncorrect logical operator ||\n"
              "{} found but | expected".format(current_line, c))
    elif code == 6:
        print("Lexical error: line {}\nInvalid character \"{}\".".format(current_line, c))
    elif code == -6:
        print("Semantic error: line {}\nRe-declared variable \"{}\".".format(current_line, lexeme))
    else:
        # Syntax error
        tokens_representation = {
            "<PalRes, 1>": "alert",
            "<PalRes, 2>": "boolean",
            "<PalRes, 3>": "for",
            "<PalRes, 4>": "function",
            "<PalRes, 5>": "if",
            "<PalRes, 6>": "input",
            "<PalRes, 7>": "let",
            "<PalRes, 8>": "number",
            "<PalRes, 9>": "return",
            "<PalRes, 10>": "string",
            "<Ent": "Integer Value",
            "<Cad": "String",
            "<Id": "Variable",
            "<Igual, >": "=",
            "<ModIgual, >": "%=",
            "<Coma, >": ",",
            "<PtComa, >": ";",
            "<ParAper, >": "(",
            "<ParCier, >": ")",
            "<CorcAper, >": "{",
            "<CorcCier, >": "}",
            "<Mult, >": "*",
            "<Or, >": "||",
            "<Mayor, >": ">",
            "<EOF, >": "End of File"
        }
        # The received token
        if 6 < code < 25:
            next_token_code = next_token.split(",")[0]
            if next_token_code == "<Id":
                next_token = find_lexeme_in_symbol_table(int(next_token.split(",")[1][1]))
            elif next_token_code == "<Ent":
                next_token = next_token.split(",")[1][1:-1]
            elif next_token_code == "<Cad":
                next_token = next_token.split(",")[1][2:-2]
            else:
                next_token = tokens_representation[next_token]
            # The token that should have occurred
            if token is not None:
                token_code = token.split(",")[0]
                if token_code == "<Ent" or token_code == "<Cad" or token_code == "<Id":
                    token = find_lexeme_in_symbol_table(int(token.split(",")[1][1]))
                else:
                    token = tokens_representation[token]
        if code == 7:
            print("Syntax error: line {}\n\"{}\" expected, but \"{}\" was found".format(current_line, token, next_token))
        elif code == 8:
            print("Syntax error: line {}\nUnexpected start of Program Block: \"{}\"".format(current_line, next_token))
            print("Program Blocks must start with any of the following:")
            for i in options:
                print("\"{}\"".format(i))
        elif code == 9:
            print("Syntax error: line {}\nUnexpected start of Compound Sentence: \"{}\"".format(current_line, next_token))
            print("Compound Sentences must start with any of the following:")
            for i in options:
                print("\"{}\"".format(i))
        elif code == 10:
            print("Syntax error: line {}\nUnexpected start of Then Block after If statement: \"{}\"".format(current_line, next_token))
            print("Then Blocks must start with any of the following:")
            for i in options:
                print("\"{}\"".format(i))
        elif code == 11:
            print("Syntax error: line {}\nUnexpected start of Initialization after Variable declaration: \"{}\"".format(current_line, next_token))
            print("Initializations after Variable declaration must be empty or start with the symbol \"=\"")
        elif code == 12:
            print("Syntax error: line {}\nUnexpected Type: \"{}\"".format(current_line, next_token))
            print("Variable and Function Types must start with any of the following:")
            for i in options:
                print("\"{}\"".format(i))
        elif code == 13:
            print("Syntax error: line {}\nUnexpected Assignment symbol: \"{}\"".format(current_line, next_token))
            print("Assignments must include any of the following:")
            for i in options:
                print("\"{}\"".format(i))
        elif code == 14:
            print("Syntax error: line {}\nUnexpected symbol found in Expression: \"{}\"".format(current_line, next_token))
            print("Any of the following symbols was expected:")
            for i in options:
                print("\"{}\"".format(i))
        elif code == 15:
            print("Syntax error: line {}\nUnexpected start of Simple Sentence: \"{}\"".format(current_line, next_token))
            print("Simple Sentences must start with any of the following:")
            for i in options:
                print("\"{}\"".format(i))
        elif code == 16:
            print("Syntax error: line {}\nUnexpected symbol after Variable: \"{}\"".format(current_line, next_token))
            print("Any of the following symbols was expected:")
            for i in options:
                print("\"{}\"".format(i))
        elif code == 17:
            print("Syntax error: line {}\nUnexpected symbol in Function Call Parameters: \"{}\"".format(current_line, next_token))
            print("Any of the following was expected:")
            for i in options:
                print("\"{}\"".format(i))
        elif code == 18:
            print("Syntax error: line {}\nUnexpected symbol in Return Statement Expression: \"{}\"".format(current_line, next_token))
            print("Any of the following was expected:")
            for i in options:
                print("\"{}\"".format(i))
        elif code == 19:
            print("Syntax error: line {}\nUnexpected symbol upon Function Declaration: \"{}\"".format(current_line, next_token))
            print("Function Declarations must start with the keyword \"function\"")
        elif code == 20:
            print("Syntax error: line {}\nUnexpected symbol in Function Declaration: \"{}\"".format(current_line, next_token))
            print("Upon Function Declaration, the \"function\" keyword must be followed by the function return type, or the function identifier if no return statement is to be used")
            print("Any of the following was expected:")
            for i in options:
                print("\"{}\"".format(i))
        elif code == 21:
            print("Syntax error: line {}\nUnexpected symbol in Function Declaration Argument: \"{}\"".format(current_line, next_token))
            print("Function Arguments must be typed and be enclosed by parenthesis. Any of the following was expected:")
            for i in options:
                print("\"{}\"".format(i))
        elif code == 22:
            print("Syntax error: line {}\nUnexpected symbol in Function Declaration Arguments: \"{}\"".format(current_line, next_token))
            print("Function Arguments must be enclosed by parenthesis, and be separated by commas. Any of the following was expected:")
            for i in options:
                print("\"{}\"".format(i))
        elif code == 23:
            print("Syntax error: line {}\nUnexpected symbol in Body Block: \"{}\"".format(current_line, next_token))
            print("Body Blocks may appear after \"for\", \"if\", and \"function\" Blocks, and must start with any of the following:")
            for i in options:
                print("\"{}\"".format(i))
        elif code == 24:
            print("Syntax error: line {}\n\"EOF\" expected, but \"{}\" was found".format(current_line, next_token))
        else:
            # Semantic error
            if code >= 25:
                print("Semantic error: line {}\n{}".format(current_line, description))
    # print("Before destruction, Symbol Table list was: {}".format(st_list))
    del st_list
    sys.exit()


# ok
def search_keyword(lexeme, keyword_table):
    """Returns the lexeme's position in the Keyword Table, or None if it does not occur"""
    try:
        return keyword_table.index(lexeme) + 1  # Python: 0-based, KT: 1-based indexing
    except ValueError:
        return None


# ok
def character_to_value():
    """Returns the integer value of the base 10 string literal of length one "c" -no char type in Python"""
    return int(c)


# ok
def find_type_width(id_type):
    """Returns the width in bytes of the specified variable type"""
    return type_widths[id_type]


# ok
def add_st_to_st_list():
    """Add a symbol table to the collection of symbol tables, and return its position in the collection"""
    st_list.append([])
    return len(st_list) - 1


# ok
def find_lexeme_in_symbol_table(id_pos):
    """Returns lexeme of variable at position "id_pos"
       in the currently-in-use symbol Table.
     """
    # Python: 0-based, ST: 1-based indexing
    lexeme = st_list[current_st_index][id_pos - 1]["Lexema"]
    return lexeme


# ok
def find_pos_in_symbol_table(lexeme):
    """Returns the lexeme's position in
       the currently-in-use symbol table.
       If not found, None is returned
     """
    # Python: 0-based, ST: 1-based indexing
    id_pos = next((index + 1 for (index, dct) in enumerate(st_list[current_st_index]) if dct["Lexema"] == lexeme), None)
    return id_pos


# ok
def find_id_type_in_st(id_pos):
    """Returns the variable's type which is at position "id_pos"
       in the currently-in-use symbol table.
       If no type is found, None is returned
    """
    # Python: 0-based, ST: 1-based indexing
    if "Tipo" in st_list[current_st_index][id_pos - 1]:
        id_type = st_list[current_st_index][id_pos - 1]["Tipo"]
        return id_type
    return None


# ok
def find_offset_in_st():
    """Returns the offset for the next variable to be
       inserted into the currently-in-use symbol table.
       Checks the last element in the ST which
       has an offset (functions do not), and retrieves
       its offset and its type. Next offset will be:
       offset + size_of(type).
       If no element with offset is present in the ST,
       zero is returned
    """
    for i in range(len(st_list[current_st_index])):
        if "Despl" in st_list[current_st_index][-i - 1]:
            current_offset = st_list[current_st_index][-i - 1]["Despl"]
            return current_offset + find_type_width(st_list[current_st_index][-i - 1]["Tipo"])
    return 0


# ok
def find_params_types(id_pos):
    """Returns a list containing the types of every parameter
       defined in the declaration of the function at
       position "id_pos" in the currently-in-use symbol table.
    """
    # Python: 0-based, ST: 1-based indexing
    attributes = st_list[current_st_index][id_pos - 1]
    params_types = []
    for attribute in attributes:
        if attribute[:9] == "TipoParam":
            params_types.append(attributes[attribute])
    return params_types


# ok
def find_return_type(id_pos):
    """Returns the returning data type of the function
       at position "id_pos" in the currently-in-use symbol table.
    """
    # Python: 0-based, ST: 1-based indexing
    attributes = st_list[current_st_index][id_pos - 1]
    return attributes["TipoRetorno"]


# ok
def insert_into_symbol_table(lexeme):
    """Inserts "lexeme" into the currently-in-use symbol table
      at the next position available, and returns its position
    """
    st_list[current_st_index].append({"Lexema": lexeme})
    # Python: 0-based, ST: 1-based indexing
    return len(st_list[current_st_index])


# ok
def insert_type_into_st(id_pos, id_type):
    """Inserts the given "type" into the currently-in-use
       symbol table at position "id_pos"
    """
    # Python: 0-based, ST: 1-based indexing
    st_list[current_st_index][id_pos - 1]["Tipo"] = id_type


# ok
def insert_offset_into_st(id_pos, offset):
    """Inserts the given "offset" into the currently-in-use
       symbol table at position "id_pos"
    """
    # Python: 0-based, ST: 1-based indexing
    st_list[current_st_index][id_pos - 1]["Despl"] = offset


# ok
def insert_label_into_st(id_pos, fun_label):
    """Inserts the given "function label" into the currently-in-use
       symbol table at position "id_pos"
    """
    # Python: 0-based, ST: 1-based indexing
    st_list[current_st_index][id_pos - 1]["EtiqFuncion"] = fun_label


# ok
def insert_param_count(id_pos, param_count):
    """Inserts the given number of arguments into the currently-in-use
       symbol table at position "id_pos"
    """
    # Python: 0-based, ST: 1-based indexing
    st_list[current_st_index][id_pos - 1]["NumParam"] = param_count


# ok
def insert_param_type(id_pos, i, fun_arg_type):
    """Inserts the given argument type into the currently-in-use
       symbol table at position "id_pos"
    """
    # Python: 0-based, ST: 1-based indexing
    label = "TipoParam" + str(i)
    st_list[current_st_index][id_pos - 1][label] = fun_arg_type


# ok
def insert_param_mode(id_pos, i, arg_mode):
    """Inserts the given argument mode (by value or by reference)
       into the currently-in-use symbol table at position "id_pos"
    """
    # Python: 0-based, ST: 1-based indexing
    label = "ModoParam" + str(i)
    st_list[current_st_index][id_pos - 1][label] = arg_mode


# ok
def insert_return_type(id_pos, return_type):
    """Inserts the given return data type (integer, string, boolean or no return)
       into the currently-in-use symbol table at position "id_pos"
    """
    # Python: 0-based, ST: 1-based indexing
    st_list[current_st_index][id_pos - 1]["TipoRetorno"] = return_type


###############
#    Lexer    #
###############


# ok
def lexer():
    """Reads one character at a time, detects lexical errors, updates Symbol Table.
       Returns token: <code, attribute>, or calls error_handler upon lexical error
    """
    global c
    global current_line
    global non_current_ts
    global current_st_index
    current_token = None
    state = 0  # initial FSA state
    keyword_table = ["alert", "boolean", "for", "function", "if", "input", "let", "number", "return", "string"]
    transition, value, lexeme, counter = None, None, None, None  # fixes warnings, but you can delete this line
    final_states = [1, 3, 4, 5, 6, 7, 9, 11, 13, 14, 15, 16, 17, 19, 22]
    fsa_transitions = {
        0: {
            "[ \t\n]": {  # matches a delimiter (space, tab, newline).
                "action": "A",
                "next_state": 0
            },
            "[>]": {  # matches a >.
                "action": "B",
                "next_state": 1
            },
            "[0-9]": {  # matches a digit (0 to 9).
                "action": "C",
                "next_state": 2
            },
            "[=]": {  # matches a =.
                "action": "F",
                "next_state": 4
            },
            "[{]": {  # matches a {.
                "action": "G",
                "next_state": 5
            },
            "[}]": {  # matches a }.
                "action": "H",
                "next_state": 6
            },
            "[,]": {  # matches a ,.
                "action": "I",
                "next_state": 7
            },
            "[']": {  # matches a '.
                "action": "J",
                "next_state": 8
            },
            "[%]": {  # matches a %.
                "action": "M",
                "next_state": 10
            },
            "[|]": {  # matches a |.
                "action": "O",
                "next_state": 12
            },
            "[(]": {  # matches a (.
                "action": "Q",
                "next_state": 14
            },
            "[)]": {  # matches a ).
                "action": "R",
                "next_state": 15
            },
            "[*]": {  # matches a *.
                "action": "S",
                "next_state": 16
            },
            "[;]": {  # matches a ;.
                "action": "T",
                "next_state": 17
            },
            "[a-zA-Z]": {  # matches a letter (a to z or A to Z).
                "action": "U",
                "next_state": 18
            },
            "[/]": {  # matches a /.
                "action": "X",
                "next_state": 20
            },
            None: {  # represents End of File, which is not a character, but a state of the file handle.
                # allows final transition to state 22.
                "action": "Z4",
                "next_state": 22
            }
        },
        2: {
            "[0-9]": {  # matches a digit (0 to 9).
                "action": "D",
                "next_state": 2
            },
            "[^0-9]": {  # matches everything but a digit.
                "action": "E",
                "next_state": 3
            },
            None: {  # represents End of File, which is not a character, but a state of the file handle.
                # allows transition to state 3.
                "action": "E",
                "next_state": 3
            }
        },
        8: {
            "[^'\n]": {  # matches everything but a single quotation mark, or a newline.
                "action": "K",
                "next_state": 8
            },
            "[']": {  # matches a single quotation mark.
                "action": "L",
                "next_state": 9
            }
        },
        10: {  # matches a =.
            "[=]": {
                "action": "N",
                "next_state": 11
            }
        },
        12: {  # matches a |.
            "[|]": {
                "action": "P",
                "next_state": 13
            }
        },
        18: {  # matches a letter (a to z or A to Z).
            "[a-zA-Z]": {
                "action": "V",
                "next_state": 18
            },
            "[0-9]": {  # matches a digit (0 to 9).
                "action": "V",
                "next_state": 18
            },
            "[_]": {  # matches a _.
                "action": "V",
                "next_state": 18
            },
            "[^a-zA-Z0-9_]": {  # matches everything but a letter (a to z or A to Z), a digit (0 to 9), and a _.
                "action": "W",
                "next_state": 19
            },
            None: {  # represents End of File, which is not a character, but a state of the file handle.
                # allows transition to state 19.
                "action": "W",
                "next_state": 19
            }
        },
        20: {
            "[/]": {  # matches a /.
                "action": "Y",
                "next_state": 21
            }
        },
        21: {  # matches everything but a newline.
            "[^\n]": {
                "action": "Z",
                "next_state": 21
            },
            "[\n]": {  # matches a newline.
                "action": "Z2",
                "next_state": 0
            },
            None: {  # represents End of File, which is not a character, but a state of the file handle.
                # allows final transition to state 22.
                "action": "Z3",
                "next_state": 22
            }
        }
    }
    while state not in final_states:
        allowed_state_transitions = fsa_transitions[state]
        valid_transition = False
        if state not in [2, 18] and c == "\n":  # in States 2, 18, we do not read on "\n", thus increment counter
            current_line = current_line + 1     # next time, when we return to State 0 and read same character
        for transition in allowed_state_transitions:
            if not c:  # eof
                if transition is None:  # eof
                    valid_transition = True  # eof valid in Transitions 0-22, 2-3, 18-19, 21-0
                    break
            else:  # character
                if transition is not None:  # Cannot use re.match with None
                    if re.match(transition, c):  # compare transition pattern Vs. character
                        valid_transition = True
                        break
        if valid_transition:
            action = fsa_transitions[state][transition]["action"]
            state = fsa_transitions[state][transition]["next_state"]
            if action == "A":
                c = f.read(1)
            elif action == "B":
                current_token = "<Mayor, >"
                c = f.read(1)
            elif action == "C":
                value = character_to_value()
                c = f.read(1)
            elif action == "D":
                value = value * 10 + character_to_value()
                c = f.read(1)
            elif action == "E":
                if value < 32768:
                    current_token = "<Ent, {}>".format(value)
                else:
                    error_handler(1, value=value)
                    break
            elif action == "F":
                current_token = "<Igual, >"
                c = f.read(1)
            elif action == "G":
                current_token = "<CorcAper, >"
                c = f.read(1)
            elif action == "H":
                current_token = "<CorcCier, >"
                c = f.read(1)
            elif action == "I":
                current_token = "<Coma, >"
                c = f.read(1)
            elif action == "J":
                counter = 0
                lexeme = "\""
                c = f.read(1)
            elif action == "K":
                lexeme = lexeme + c
                counter = counter + 1
                c = f.read(1)
            elif action == "L":
                if counter < 65:
                    lexeme = lexeme + "\""
                    current_token = "<Cad, {}>".format(lexeme)
                    c = f.read(1)
                else:
                    error_handler(2, string_chars=counter)
                    break
            elif action == "M":
                c = f.read(1)
            elif action == "N":
                current_token = "<ModIgual, >"
                c = f.read(1)
            elif action == "O":
                c = f.read(1)
            elif action == "P":
                current_token = "<Or, >"
                c = f.read(1)
            elif action == "Q":
                current_token = "<ParAper, >"
                c = f.read(1)
            elif action == "R":
                current_token = "<ParCier, >"
                c = f.read(1)
            elif action == "S":
                current_token = "<Mult, >"
                c = f.read(1)
            elif action == "T":
                current_token = "<PtComa, >"
                c = f.read(1)
            elif action == "U":
                lexeme = c
                c = f.read(1)
            elif action == "V":
                lexeme = lexeme + c
                c = f.read(1)
            elif action == "W":
                pos = search_keyword(lexeme, keyword_table)
                if pos is not None:
                    current_token = "<PalRes, {}>".format(pos)
                else:
                    pos = find_pos_in_symbol_table(lexeme)
                    if decl_zone:
                        if pos is None:
                            pos = insert_into_symbol_table(lexeme)
                        else:
                            error_handler(-6, lexeme=lexeme)
                    else:
                        if pos is None:
                            current_st_index2 = current_st_index
                            if current_st_index != global_st_index:
                                current_st_index = global_st_index
                                pos = find_pos_in_symbol_table(lexeme)
                                non_current_ts = True
                            if pos is None:
                                pos = insert_into_symbol_table(lexeme)
                            current_st_index = current_st_index2
                    current_token = "<Id, {}>".format(pos)
            elif action == "X":
                c = f.read(1)
            elif action == "Y":
                c = f.read(1)
            elif action == "Z":
                c = f.read(1)
            elif action == "Z2":
                c = f.read(1)
            else:  # Z3 | Z4
                current_token = "<EOF, >"
        else:
            if state == 8:
                error_handler(3)
            elif state == 10:
                error_handler(4)
            elif state == 12:
                error_handler(5)
            else:
                error_handler(6)
            break
    return current_token


###############
#    Parser   #
###############


# ok
def p():
    """Handles syntax validation for Program Blocks:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions at the Program level for semantic validation.
    """
    global parse
    global st_list
    global current_st_index
    global global_st_index
    global non_current_ts
    if len(st_list) == 0:
        global_st_index = add_st_to_st_list()
    current_st_index = global_st_index
    non_current_ts = False
    if next_token in ["<PalRes, 3>", "<PalRes, 5>", "<PalRes, 7>", "<PalRes, 1>", "<PalRes, 6>", "<PalRes, 9>"] or next_token.split(",")[0] == "<Id":
        parse += " 1"
        return_type = None
        comp_sent(return_type)
        p()
    elif next_token in ["<PalRes, 4>"]:
        parse += " 2"
        fun()
        p()
    elif next_token == "<EOF, >":
        parse += " 3"
        # print(st_list)
        for i in range(len(st_list)):
            f3.write("TABLA DE SIMBOLOS #{}:\n".format(i+1))
            for entry in st_list[i]:
                f3.write("* Lexema: '{}'\n".format(entry["Lexema"]))
                f3.write("\t+ Tipo: '{}'\n".format(entry["Tipo"]))
                if entry["Tipo"] == "Fun":
                    f3.write("\t\t+ NumParam: {}\n".format(entry["NumParam"]))
                    for tag in entry:
                        if tag[:9] == "TipoParam":
                            f3.write("\t\t+ {}: '{}'\n".format(tag, entry[tag]))
                        if tag[:9] == "ModoParam":
                            f3.write("\t\t+ {}: '{}'\n".format(tag, entry[tag]))
                    f3.write("\t\t+ TipoRetorno: '{}'\n".format(entry["TipoRetorno"]))
                    f3.write("\t\t+ EtiqFuncion: '{}'\n".format(entry["EtiqFuncion"]))
                else:
                    f3.write("\t+ Despl: {}\n".format(entry["Despl"]))
        del st_list
    else:
        error_handler(8, options=["for", "if", "let", "alert", "input", "return", "Variable", "function", "End of File"])


# ok
def comp_sent(return_type):
    """Handles syntax validation for Compound Statements:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for Compound Statements for semantic validation.
    """
    global parse
    global decl_zone
    if next_token == "<PalRes, 3>":
        parse += " 4"
        compare("<PalRes, 3>")
        compare("<ParAper, >")
        assign1_lexeme = assign()
        compare("<PtComa, >")
        exp_type = exp()
        if exp_type != "Log":
            if exp_type == "Ent":
                exp_type = "an integer"
            elif exp_type == "Cad":
                exp_type = "a string"
            else:
                exp_type = "nothing"
            error_handler(25, description="\"for\" loops need a logical stop condition, but {} was found".format(exp_type))
        compare("<PtComa, >")
        assign2_lexeme = assign()
        if assign1_lexeme != assign2_lexeme:
            error_handler(26, description=" \"{}\" is initialized, but \"{}\" is updated in \"for\" loop. This may lead to an infinite loop".format(assign1_lexeme, assign2_lexeme))
        compare("<ParCier, >")
        compare("<CorcAper, >")
        body(return_type)
        compare("<CorcCier, >")
    elif next_token == "<PalRes, 5>":
        parse += " 5"
        compare("<PalRes, 5>")
        compare("<ParAper, >")
        exp_type = exp()
        if exp_type != "Log":
            if exp_type == "Ent":
                exp_type = "an integer"
            elif exp_type == "Cad":
                exp_type = "a string"
            else:
                exp_type = "nothing"
            error_handler(27, description="\"if\" statements need a logical entry condition, but {} was found".format(exp_type))
        compare("<ParCier, >")
        then(return_type)
    elif next_token == "<PalRes, 7>":
        parse += " 6"
        decl_zone = True
        compare("<PalRes, 7>")
        type_f_type = type_f()
        id_pos = int(next_token.split(", ")[1][:-1])
        compare("<Id, any>")
        insert_type_into_st(id_pos, type_f_type)
        offset = find_offset_in_st()
        insert_offset_into_st(id_pos, offset)
        decl_zone = False
        init(type_f_type)
        compare("<PtComa, >")
    elif next_token in ["<PalRes, 1>", "<PalRes, 6>", "<PalRes, 9>"] or next_token.split(",")[0] == "<Id":
        parse += " 7"
        simple_sent(return_type)
    else:
        error_handler(9, options=["for", "if", "let", "alert", "input", "return", "Variable"])


# ok
def then(return_type):
    """Handles syntax validation for Then Blocks after If statements:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for Then Blocks for semantic validation.
    """
    global parse
    if next_token in ["<PalRes, 1>", "<PalRes, 6>", "<PalRes, 9>"] or next_token.split(",")[0] == "<Id":
        parse += " 8"
        simple_sent(return_type)
    elif next_token == "<CorcAper, >":
        parse += " 9"
        compare("<CorcAper, >")
        body(return_type)
        compare("<CorcCier, >")
    else:
        error_handler(10, options=["alert", "input", "return", "Variable", "{"])


# ok
def init(type_f_type):
    """Handles syntax validation for Initializations after a Variable declaration:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for Initializations for semantic validation.
    """
    global parse
    if next_token == "<Igual, >":
        parse += " 10"
        compare("<Igual, >")
        exp_type = exp()
        if exp_type != type_f_type:
            if exp_type == "Ent":
                exp_type = "an integer value"
            elif exp_type == "Cad":
                exp_type = "a string value"
            elif exp_type == "Log":
                exp_type = "a logical value"
            else:
                exp_type = "null"
            if type_f_type == "Ent":
                type_f_type = "an integer"
            elif type_f_type == "Cad":
                type_f_type = "a string"
            else:
                type_f_type = "a logical"
            error_handler(28, description="Initialization after a Variable declaration must match the variable's type.\nCannot initialize {} variable to {}".format(type_f_type, exp_type))
    elif next_token in ["<PtComa, >"]:
        parse += " 11"
    else:
        error_handler(11)


# ok
def type_f():
    """Handles syntax validation for a variable's Type declaration:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for Type declarations for semantic validation.
    """
    global parse
    type_f_type = ""
    if next_token == "<PalRes, 8>":
        parse += " 12"
        compare("<PalRes, 8>")
        type_f_type = "Ent"
    elif next_token == "<PalRes, 2>":
        parse += " 13"
        compare("<PalRes, 2>")
        type_f_type = "Log"
    elif next_token == "<PalRes, 10>":
        parse += " 14"
        compare("<PalRes, 10>")
        type_f_type = "Cad"
    else:
        error_handler(12, options=["number", "boolean", "string"])
    return type_f_type


# ok
def assign():
    """Handles syntax validation for Variable Assignments:
       Updates Parse Tree.
       Calls the appropriate function.
       compare will fail and error_handler will be called if an unexpected token is sent.
       Performs Semantic actions for Variable Assignments for semantic validation.
    """
    global parse
    global current_st_index
    global non_current_ts
    parse += " 15"
    id_pos = int(next_token.split(", ")[1][:-1])
    compare("<Id, any>")
    if non_current_ts:
        current_st_index2 = current_st_index
        current_st_index = global_st_index
        id_type = find_id_type_in_st(id_pos)
        if id_type is None:
            id_type = "Ent"
            insert_type_into_st(id_pos, id_type)
            offset = find_offset_in_st()
            insert_offset_into_st(id_pos, offset)
        id_lexeme = find_lexeme_in_symbol_table(id_pos)
        current_st_index = current_st_index2
        non_current_ts = False
    else:
        id_type = find_id_type_in_st(id_pos)
        if id_type is None:
            insert_type_into_st(id_pos, id_type)
            offset = find_offset_in_st()
            insert_offset_into_st(id_pos, offset)
            id_type = "Ent"
        id_lexeme = find_lexeme_in_symbol_table(id_pos)
    assign1(id_type)
    return id_lexeme


# ok
def assign1(id_type):
    """Handles syntax validation for Assignment Operations:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for Assignment Operations for semantic validation.
    """
    global parse
    if next_token == "<Igual, >":
        parse += " 16"
        compare("<Igual, >")
        exp_type = exp()
        if exp_type != id_type:
            if exp_type == "Ent":
                exp_type = "an integer value"
            elif exp_type == "Cad":
                exp_type = "a string value"
            elif exp_type == "Log":
                exp_type = "a logical value"
            else:
                exp_type = "null"
            if id_type == "Ent":
                id_type = "an integer"
            elif id_type == "Cad":
                id_type = "a string"
            elif id_type == "Log":
                id_type = "a logical"
            else:
                id_type = "a function"
            error_handler(29, description="A Variable assignment (=) expression must match the Variable's type.\nCannot assign {} variable to {}".format(id_type, exp_type))
    elif next_token == "<ModIgual, >":
        parse += " 17"
        compare("<ModIgual, >")
        exp_type = exp()
        if exp_type != id_type:
            if exp_type == "Ent":
                exp_type = "an integer value"
            elif exp_type == "Cad":
                exp_type = "a string value"
            elif exp_type == "Log":
                exp_type = "a logical value"
            else:
                exp_type = "null"
            if id_type == "Ent":
                id_type = "an integer"
            elif id_type == "Cad":
                id_type = "a string"
            elif id_type == "Log":
                id_type = "a logical"
            else:
                id_type = "a function"
            error_handler(30, description="A Variable assignment (%=) expression must match the Variable's type.\nCannot assign {} variable to {}".format(id_type, exp_type))
    else:
        error_handler(13, options=["=", "%="])


# ok
def exp():
    """Handles syntax validation for Expressions (1/4):
       Updates Parse Tree.
       Calls the appropriate function.
       Performs Semantic actions for Expressions for semantic validation.
    """
    global parse
    exp_type = ""
    parse += " 18"
    exp2_type = exp2()
    exp_p_type = exp_p()
    if exp_p_type != "Vacio":
        if exp2_type != "Log":
            if exp2_type == "Ent":
                exp2_type = "an integer operand"
            elif exp2_type == "Cad":
                exp2_type = "a string operand"
            else:
                exp2_type = "null"
            error_handler(31, description="An || (OR) operator requires two logical operands, but {} was found.".format(exp2_type))
        else:
            exp_type = "Log"
    else:
        exp_type = exp2_type
    return exp_type


# ok
def exp_p():
    """Handles syntax validation for Logical Expressions:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for Logical Expressions for semantic validation.
    """
    global parse
    exp_p_type = ""
    if next_token == "<Or, >":
        parse += " 19"
        compare("<Or, >")
        exp2_type = exp2()
        if exp2_type != "Log":
            if exp2_type == "Ent":
                exp2_type = "an integer operand"
            elif exp2_type == "Cad":
                exp2_type = "a string operand"
            else:
                exp2_type = "null"
            error_handler(32, description="An || (OR) operator requires two logical operands, but {} was found.".format(exp2_type))
        else:
            exp_p_type = "Log"
        exp_p_type2 = exp_p()
        if exp_p_type2 != "Vacio":
            if exp_p_type2 != "Log":
                if exp_p_type2 == "Ent":
                    exp_p_type2 = "an integer operand"
                elif exp_p_type2 == "Cad":
                    exp_p_type2 = "a string operand"
                else:
                    exp_p_type2 = "null"
                error_handler(33, description="|| (OR) operators can be chained, but all operands must be logical.\nFor example, true || false || true is allowed.\n.However, {} was found.".format(exp_p_type2))
    elif next_token in ["<Coma, >", "<PtComa, >", "<ParCier, >"]:
        parse += " 20"
        exp_p_type = "Vacio"
    else:
        error_handler(14, options=["||", ",", ";", ")"])
    return exp_p_type


# ok
def exp2():
    """Handles syntax validation for Expressions (2/4):
       Updates Parse Tree.
       Calls the appropriate function.
       Performs Semantic actions for Expressions for semantic validation.
    """
    global parse
    exp2_type = ""
    parse += " 21"
    exp3_type = exp3()
    exp2_p_type = exp2_p()
    if exp2_p_type != "Vacio":
        if exp3_type != "Ent":
            if exp3_type == "Log":
                exp3_type = "a logical operand"
            elif exp3_type == "Cad":
                exp3_type = "a string operand"
            else:
                exp3_type = "null"
            error_handler(34, description="A > (GREATER THAN) operator requires two integer operands, but {} was found.".format(exp3_type))
        else:
            exp2_type = "Log"
    else:
        exp2_type = exp3_type
    return exp2_type


# ok
def exp2_p():
    """Handles syntax validation for Relational Expressions:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for Relational Expressions for semantic validation.
    """
    global parse
    exp2_p_type = ""
    if next_token == "<Mayor, >":
        parse += " 22"
        compare("<Mayor, >")
        exp3_type = exp3()
        if exp3_type != "Ent":
            if exp3_type == "Log":
                exp3_type = "a logical operand"
            elif exp3_type == "Cad":
                exp3_type = "a string operand"
            else:
                exp3_type = "null"
            error_handler(35, description="A > (GREATER THAN) operator requires two integer operands, but {} was found.".format(exp3_type))
        else:
            exp2_p_type = "Log"
        exp2_p_type2 = exp2_p()
        if exp2_p_type2 != "Vacio":
            error_handler(36, description="> (GREATER THAN) operators cannot be chained, as all operands must be integers.\nFor example, 3 > 5 > 2 evaluates to false > 2, which is invalid.")
    elif next_token in ["<Or, >", "<Coma, >", "<PtComa, >", "<ParCier, >"]:
        parse += " 23"
        exp2_p_type = "Vacio"
    else:
        error_handler(14, options=[">", "||", ",", ";", ")"])
    return exp2_p_type


# ok
def exp3():
    """Handles syntax validation for Expressions (3/4):
       Updates Parse Tree.
       Calls the appropriate function.
       Performs Semantic actions for Expressions for semantic validation.
    """
    global parse
    exp3_type = ""
    parse += " 24"
    exp4_type = exp4()
    exp3_p_type = exp3_p()
    if exp3_p_type != "Vacio":
        if exp4_type != "Ent":
            if exp4_type == "Log":
                exp4_type = "a logical operand"
            elif exp4_type == "Cad":
                exp4_type = "a string operand"
            else:
                exp4_type = "null"
            error_handler(37, description="A * (MULTIPLICATION) operator requires two integer operands, but {} was found.".format(exp4_type))
        else:
            exp3_type = "Ent"
    else:
        exp3_type = exp4_type
    return exp3_type


# ok
def exp3_p():
    """Handles syntax validation for Arithmetic Expressions:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for Arithmetic Expressions for semantic validation.
    """
    global parse
    exp3_p_type = ""
    if next_token == "<Mult, >":
        parse += " 25"
        compare("<Mult, >")
        exp4_type = exp4()
        if exp4_type != "Ent":
            if exp4_type == "Log":
                exp4_type = "a logical operand"
            elif exp4_type == "Cad":
                exp4_type = "a string operand"
            else:
                exp4_type = "null"
            error_handler(38, description="A * (MULTIPLICATION) operator requires two integer operands, but {} was found.".format(exp4_type))
        else:
            exp3_p_type = "Ent"
        exp3_p_type2 = exp3_p()
        if exp3_p_type2 != "Vacio":
            if exp3_p_type2 != "Ent":
                if exp3_p_type2 == "Log":
                    exp3_p_type2 = "a logical operand"
                elif exp3_p_type2 == "Cad":
                    exp3_p_type2 = "a string operand"
                else:
                    exp3_p_type2 = "null"
                error_handler(39, description="* (MULTIPLICATION) operators can be chained, but all operands must be integer.\nFor example, 3 * 4 * 12 is allowed.\n.However, {} was found.".format(exp3_p_type2))
    elif next_token in ["<Mayor, >", "<Or, >", "<Coma, >", "<PtComa, >", "<ParCier, >"]:
        parse += " 26"
        exp3_p_type = "Vacio"
    else:
        error_handler(14, options=["*", ">", "||", ",", ";", ")"])
    return exp3_p_type


# ok
def exp4():
    """Handles syntax validation for Expressions (4/4):
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for Expressions for semantic validation.
    """
    global parse
    global current_st_index
    global non_current_ts
    exp4_type = ""
    if next_token.split(",")[0] == "<Id":
        parse += " 27"
        id_pos = int(next_token.split(", ")[1][:-1])
        compare("<Id, any>")
        current_st_index2 = current_st_index
        if non_current_ts:
            current_st_index = global_st_index
            id_type = find_id_type_in_st(id_pos)
            if id_type is None:
                id_type = "Ent"
                insert_type_into_st(id_pos, id_type)
                offset = find_offset_in_st()
                insert_offset_into_st(id_pos, offset)
            exp4_type = id_type
        else:
            id_type = find_id_type_in_st(id_pos)
            if id_type is None:
                id_type = "Ent"
                insert_type_into_st(id_pos, id_type)
                offset = find_offset_in_st()
                insert_offset_into_st(id_pos, offset)
            exp4_type = id_type
        pos_call_type = pos_call(id_pos, id_type, current_st_index2)
        if pos_call_type is not None:
            exp4_type = pos_call_type
        current_st_index = current_st_index2
        non_current_ts = False
    elif next_token.split(",")[0] == "<Ent":
        parse += " 28"
        compare("<Ent, any>")
        exp4_type = "Ent"
    elif next_token.split(",")[0] == "<Cad":
        parse += " 29"
        compare("<Cad, any>")
        exp4_type = "Cad"
    elif next_token == "<ParAper, >":
        parse += " 30"
        compare("<ParAper, >")
        exp4_type = exp()
        compare("<ParCier, >")
    else:
        error_handler(14, options=["Variable", "Integer Value", "String", "("])
    return exp4_type


# ok
def pos_call(id_pos, id_type, current_st_index2):
    """Handles syntax validation for Possible Function Calls following a Variable:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for Possible Function Calls for semantic validation.
    """
    global parse
    global current_st_index
    global non_current_ts
    pos_call_type = ""
    if next_token == "<ParAper, >":
        parse += " 31"
        if id_type != "Fun":
            if id_type == "Log":
                id_type = "A logical variable"
            elif id_type == "Cad":
                id_type = "A string variable"
            elif id_type == "Ent":
                id_type = "An integer variable"
            else:
                id_type = "null"
            error_handler(40, description="{} was attempted to be called as a function, but only function variables can be invoked.".format(id_type))
        fun_params_types = find_params_types(id_pos)
        current_st_index = current_st_index2
        non_current_ts = False
        compare("<ParAper, >")
        call_params_types = call_params()
        if len(call_params_types) != len(fun_params_types):
            error_handler(41, description="Function was invoked with {} arguments, but it was declared as requiring {} arguments.".format(len(call_params_types), len(fun_params_types)))
        for i in range(len(call_params_types)):
            if call_params_types[i] != fun_params_types[i]:
                if i == 0:
                    ith = str(i+1) + "st"
                elif i == 1:
                    ith = str(i+1) + "nd"
                elif i == 2:
                    ith = str(i+1) + "rd"
                else:
                    ith = str(i+1) + "th"
                if call_params_types[i] == "Log":
                    call_ith_type = "a boolean"
                elif call_params_types[i] == "Cad":
                    call_ith_type = "a string"
                elif call_params_types[i] == "Ent":
                    call_ith_type = "an integer"
                elif call_params_types[i] == "Fun":
                    call_ith_type = "a function variable"
                else:
                    call_ith_type = "null"
                if fun_params_types[i] == "Log":
                    fun_ith_type = "logical"
                elif fun_params_types[i] == "Cad":
                    fun_ith_type = "a string"
                else:
                    fun_ith_type = "an integer"
                error_handler(42, description="{} argument in function call was expected to be {} but {} was found.".format(ith, fun_ith_type, call_ith_type))
        compare("<ParCier, >")
        current_st_index = global_st_index
        pos_call_type = find_return_type(id_pos)
        current_st_index = current_st_index2
    elif next_token in ["<Mult, >", "<Mayor, >", "<Or, >", "<Coma, >", "<PtComa, >", "<ParCier, >"]:
        parse += " 32"
        pos_call_type = None
    else:
        error_handler(16, options=["(", "*", ">", "||", ",", ";", ")"])
    return pos_call_type


# ok
def simple_sent(return_type):
    """Handles syntax validation for Simple Statements:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for Simple Statements for semantic validation.
    """
    global parse
    global current_st_index
    global non_current_ts
    global ret_to_find
    if next_token.split(",")[0] == "<Id":
        parse += " 33"
        id_pos = int(next_token.split(", ")[1][:-1])
        compare("<Id, any>")
        current_st_index2 = current_st_index
        if non_current_ts:
            current_st_index = global_st_index
            id_type = find_id_type_in_st(id_pos)
            if id_type is None:
                id_type = "Ent"
                insert_type_into_st(id_pos, id_type)
                offset = find_offset_in_st()
                insert_offset_into_st(id_pos, offset)
        else:
            id_type = find_id_type_in_st(id_pos)
            if id_type is None:
                id_type = "Ent"
                insert_type_into_st(id_pos, id_type)
                offset = find_offset_in_st()
                insert_offset_into_st(id_pos, offset)
        assign_or_call(id_pos, id_type, current_st_index2)
        current_st_index = current_st_index2
        non_current_ts = False
        compare("<PtComa, >")
    elif next_token == "<PalRes, 1>":
        parse += " 34"
        compare("<PalRes, 1>")
        compare("<ParAper, >")
        exp_type = exp()
        if exp_type != "Ent" and exp_type != "Cad":
            if exp_type == "Log":
                exp_type = "a boolean"
            elif exp_type == "Fun":
                exp_type = "a function variable"
            else:
                exp_type = "null"
            error_handler(43, description="\"alert\" statements can display an integer or a string to the user, but {} was found.".format(exp_type))
        compare("<ParCier, >")
        compare("<PtComa, >")
    elif next_token == "<PalRes, 6>":
        parse += " 35"
        compare("<PalRes, 6>")
        compare("<ParAper, >")
        id_pos = int(next_token.split(", ")[1][:-1])
        compare("<Id, any>")
        if non_current_ts:
            current_st_index2 = current_st_index
            current_st_index = global_st_index
            id_type = find_id_type_in_st(id_pos)
            if id_type is None:
                id_type = "Ent"
                insert_type_into_st(id_pos, id_type)
                offset = find_offset_in_st()
                insert_offset_into_st(id_pos, offset)
            current_st_index = current_st_index2
            non_current_ts = False
        else:
            id_type = find_id_type_in_st(id_pos)
            if id_type is None:
                id_type = "Ent"
                insert_type_into_st(id_pos, id_type)
                offset = find_offset_in_st()
                insert_offset_into_st(id_pos, offset)
        if id_type != "Ent" and id_type != "Cad":
            if id_type == "Log":
                id_type = "a boolean variable"
            elif id_type == "Fun":
                id_type = "a function variable"
            else:
                id_type = "no variable"
            error_handler(44, description="\"input\" statements can assign an integer or a string (from the user) to an integer or string variable, but {} was found.".format(id_type))
        compare("<ParCier, >")
        compare("<PtComa, >")
    elif next_token == "<PalRes, 9>":
        parse += " 36"
        compare("<PalRes, 9>")
        if return_type is None:
            error_handler(45, description="A \"return statement\" was found outside a function body. Only a function can use a return statement.")
        if return_type == "Vacio":
            error_handler(46, description="A \"return statement\" was found on a function that was declared as not returning any data.")
        ret_to_find = False
        ret_res_type = ret_res()
        if return_type != ret_res_type:
            if return_type == "Ent":
                return_type = "an integer"
            elif return_type == "Cad":
                return_type = "a string"
            else:
                return_type = "a boolean"
            if ret_res_type == "Ent":
                ret_res_type = "An integer-valued"
            elif ret_res_type == "Cad":
                ret_res_type = "A string-valued"
            elif ret_res_type == "Log":
                ret_res_type = "A boolean"
            elif ret_res_type == "Fun":
                ret_res_type = "A function-handler"
            else:
                ret_res_type = "No valid"
            error_handler(47, description="\"{} return statement\" was found on a function that was declared as returning {}.".format(ret_res_type, return_type))
        compare("<PtComa, >")
    else:
        error_handler(15, options=["Variable", "alert", "input", "return"])


# ok
def assign_or_call(id_pos, id_type, current_st_index2):
    """Handles syntax validation for Assignments / Function Calls following a Variable:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for Assignments / Function Calls for semantic validation.
    """
    global parse
    global current_st_index
    global non_current_ts
    if next_token in ["<Igual, >", "<ModIgual, >"]:
        parse += " 37"
        current_st_index = current_st_index2
        non_current_ts = False
        assign1(id_type)
    elif next_token == "<ParAper, >":
        parse += " 38"
        if id_type != "Fun":
            if id_type == "Log":
                id_type = "A logical variable"
            elif id_type == "Cad":
                id_type = "A string variable"
            elif id_type == "Ent":
                id_type = "An integer variable"
            else:
                id_type = "null"
            error_handler(48, description="{} was attempted to be called as a function, but only function variables can be invoked.".format(id_type))
        fun_params_types = find_params_types(id_pos)
        current_st_index = current_st_index2
        non_current_ts = False
        compare("<ParAper, >")
        call_params_types = call_params()
        if len(call_params_types) != len(fun_params_types):
            error_handler(49, description="Function was invoked with {} arguments, but it was declared as requiring {} arguments.".format(len(call_params_types), len(fun_params_types)))
        for i in range(len(call_params_types)):
            if call_params_types[i] != fun_params_types[i]:
                if i == 0:
                    ith = str(i + 1) + "st"
                elif i == 1:
                    ith = str(i + 1) + "nd"
                elif i == 2:
                    ith = str(i + 1) + "rd"
                else:
                    ith = str(i + 1) + "th"
                if call_params_types[i] == "Log":
                    call_ith_type = "a boolean"
                elif call_params_types[i] == "Cad":
                    call_ith_type = "a string"
                elif call_params_types[i] == "Ent":
                    call_ith_type = "an integer"
                elif call_params_types[i] == "Fun":
                    call_ith_type = "a function variable"
                else:
                    call_ith_type = "null"
                if fun_params_types[i] == "Log":
                    fun_ith_type = "logical"
                elif fun_params_types[i] == "Cad":
                    fun_ith_type = "a string"
                else:
                    fun_ith_type = "an integer"
                error_handler(50, description="{} argument in function call was expected to be {} but {} was found.".format(ith, fun_ith_type, call_ith_type))
        compare("<ParCier, >")
    else:
        error_handler(16, options=["=", "%=", "("])


# ok
def call_params():
    """Handles syntax validation for Function Call Parameters:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for Function Call Parameters for semantic validation.
    """
    global parse
    call_params_types = []
    if next_token.split(",")[0] == "<Id" or next_token.split(",")[0] == "<Ent" or next_token.split(",")[0] == "<Cad" or next_token in ["<ParAper, >"]:
        parse += " 39"
        exp_type = exp()
        if exp_type == "Vacio":
            error_handler(51, description="Function arguments must have a basic data type (boolean, integer, string) but a function call without any return data type was passed as argument.")
        call_params_types.append(exp_type)
        call_params_types = more_call_params(call_params_types)
    elif next_token in ["<ParCier, >"]:
        parse += " 40"
    else:
        error_handler(17, options=["Variable", "Integer Value", "String", "(", ")"])
    return call_params_types


# ok
def more_call_params(call_params_types):
    """Handles syntax validation for Function Call Parameters, after the First Parameter:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for Function Call Parameters for semantic validation.
    """
    global parse
    if next_token == "<Coma, >":
        parse += " 41"
        compare("<Coma, >")
        exp_type = exp()
        if exp_type == "Vacio":
            error_handler(52, description="Function arguments must have a basic data type (boolean, integer, string) but a function call without any return data type was passed as argument.")
        call_params_types.append(exp_type)
        call_params_types = more_call_params(call_params_types)
    elif next_token in ["<ParCier, >"]:
        parse += " 42"
    else:
        error_handler(17, options=[",", ")"])
    return call_params_types


# ok
def ret_res():
    """Handles syntax validation for Return Statement Expressions:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for Return Statement Expressions for semantic validation.
    """
    global parse
    ret_res_type = ""
    if next_token.split(",")[0] == "<Id" or next_token.split(",")[0] == "<Ent" or next_token.split(",")[0] == "<Cad" or next_token in ["<ParAper, >"]:
        parse += " 43"
        ret_res_type = exp()
    elif next_token in ["<PtComa, >"]:
        parse += " 44"
        ret_res_type = "Vacio"
    else:
        error_handler(18, options=["Variable", "Integer Value", "String", "(", ";"])
    return ret_res_type


# ok
def fun():
    """Handles syntax validation for Function Declarations:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for Function Declarations for semantic validation.
    """
    global parse
    global decl_zone
    global ret_to_find
    global current_st_index
    if next_token == "<PalRes, 4>":
        parse += " 45"
        if current_st_index != global_st_index:
            error_handler(53, description="Nested functions (declaring a function inside another function) are not allowed.")
        decl_zone = True
        compare("<PalRes, 4>")
        ret_type_type = ret_type()
        id_pos = int(next_token.split(", ")[1][:-1])
        decl_zone = False
        compare("<Id, any>")
        id_lexeme = find_lexeme_in_symbol_table(id_pos)
        fun_label = "Et" + id_lexeme + str(1)
        insert_type_into_st(id_pos, "Fun")
        insert_label_into_st(id_pos, fun_label)
        compare("<ParAper, >")
        local_st_index = add_st_to_st_list()
        current_st_index = local_st_index
        fun_args_types = fun_args()
        current_st_index = global_st_index
        param_count = len(fun_args_types)
        insert_param_count(id_pos, param_count)
        for i in range(1, param_count + 1):
            insert_param_type(id_pos, i, fun_args_types[i-1])
            insert_param_mode(id_pos, i, "Valor")
        insert_return_type(id_pos, ret_type_type)
        current_st_index = local_st_index
        compare("<ParCier, >")
        compare("<CorcAper, >")
        if ret_type_type == "Vacio":
            ret_to_find = False
        else:
            ret_to_find = True
        body(ret_type_type)
        if ret_to_find:
            if ret_type_type == "Ent":
                ret_type_type = "an integer"
            elif ret_type_type == "Cad":
                ret_type_type = "a string"
            else:
                ret_type_type = "a boolean"
            error_handler(54, description="Function must have {} return statement. However, none was found.".format(ret_type_type))
        current_st_index = global_st_index
        compare("<CorcCier, >")
    else:
        error_handler(19)


# ok
def ret_type():
    """Handles syntax validation for returning data Types on Function Declarations:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for returning data Types for semantic validation.
    """
    global parse
    ret_type_type = ""
    if next_token in ["<PalRes, 8>", "<PalRes, 2>", "<PalRes, 10>"]:
        parse += " 46"
        ret_type_type = type_f()
    elif next_token.split(",")[0] in ["<Id"]:
        parse += " 47"
        ret_type_type = "Vacio"
    else:
        error_handler(20, options=["number", "boolean", "string", "Variable"])
    return ret_type_type


# ok
def fun_args():
    """Handles syntax validation for function Arguments on Function Declarations:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for function Arguments for semantic validation.
    """
    global parse
    global decl_zone
    fun_args_types = []
    if next_token in ["<PalRes, 8>", "<PalRes, 2>", "<PalRes, 10>"]:
        parse += " 48"
        decl_zone = True
        type_f_type = type_f()
        fun_args_types = [type_f_type]
        id_pos = int(next_token.split(", ")[1][:-1])
        compare("<Id, any>")
        insert_type_into_st(id_pos, type_f_type)
        offset = find_offset_in_st()
        insert_offset_into_st(id_pos, offset)
        fun_args_types = more_fun_args(fun_args_types)
        decl_zone = False
    elif next_token in ["<ParCier, >"]:
        parse += " 49"
    else:
        error_handler(21, options=["number", "boolean", "string", ")"])
    return fun_args_types


# ok
def more_fun_args(fun_args_types):
    """Handles syntax validation for Function Arguments on Function Declarations, after the First Argument:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for function Arguments for semantic validation.
    """
    global parse
    if next_token == "<Coma, >":
        parse += " 50"
        compare("<Coma, >")
        type_f_type = type_f()
        fun_args_types.append(type_f_type)
        id_pos = int(next_token.split(", ")[1][:-1])
        compare("<Id, any>")
        insert_type_into_st(id_pos, type_f_type)
        offset = find_offset_in_st()
        insert_offset_into_st(id_pos, offset)
        fun_args_types = more_fun_args(fun_args_types)
    elif next_token in ["<ParCier, >"]:
        parse += " 51"
    else:
        error_handler(22, options=[",", ")"])
    return fun_args_types


# ok
def body(return_type):
    """Handles syntax validation for the Body of a Function:
       Updates Parse Tree.
       Calls the appropriate function if the token received from the Lexer is expected.
       Calls error_handler if an unexpected token is sent.
       Performs Semantic actions for the Body of a Function for semantic validation.
    """
    global parse
    if next_token in ["<PalRes, 3>", "<PalRes, 5>", "<PalRes, 7>", "<PalRes, 1>", "<PalRes, 6>", "<PalRes, 9>"] or next_token.split(",")[0] == "<Id":
        parse += " 52"
        comp_sent(return_type)
        body(return_type)
    elif next_token in ["<CorcCier, >"]:
        parse += " 53"
    else:
        error_handler(23, options=["for", "if", "let", "alert", "input", "return", "Variable", "}"])


def parser():
    """Processes one token at a time, detects syntax errors.
       Generates Parse Tree, or calls error_handler upon syntax error
    """
    global next_token
    next_token = lexer()
    f2.write("{}\n".format(next_token))
    p()
    if next_token != "<EOF, >":
        error_handler(24)


def compare(t):
    """Compares the expected token, with the received token from the Lexer.
       If both match, it asks the Lexer for the next token, and writes the current token to tokens file.
       Calls error_handler if an unexpected token is sent.
    """
    global next_token
    if next_token == t or next_token.split(",")[0] == t.split(",")[0]:
        next_token = lexer()
        f2.write("{}\n".format(next_token))
    else:
        error_handler(7, token=t)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Use: python3 compiler_analyzer.py file")
    else:
        parse = "D"  # descending
        next_token = ""
        current_line = 1
        decl_zone = False  # whether code will be able to declare local variables
        st_list = []  # list of symbol tables
        current_st_index = 0  # index of currently-in-use symbol table
        global_st_index = 0  # what index global st occurs in st_list
        non_current_ts = False
        ret_to_find = False
        type_widths = {
            "Ent": 2,
            "Log": 2,
            "Cad": 128
        }
        with open(sys.argv[1], "r") as f, open("tokens.txt", "w+") as f2, open("symbol_table.txt", "w+") as f3, open(
                "parse.txt", "w+") as f4:
            c = f.read(1)  # read first character
            parser()  # parser with semantic actions
            parse += "\n"
            f4.write(parse)

