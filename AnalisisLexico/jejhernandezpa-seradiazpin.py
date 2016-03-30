import re

# Transformations

transformations = {">=": "? ", "<=": "@ ", "==": "$ ", "!=": "\\ ", "&&": "& ", "||": "| ",
                   "//": '# ', "/*": '{ ', "*/": '{ '}


class Token:
    def __init__(self, token, line, column, lexer=""):
        self.token = token
        self.line = line + 1
        self.column = column + 1
        self.lexer = lexer

    def __str__(self):
        return "<" + self.token + "," + ("" if self.lexer == "" else self.lexer + ",") + str(self.line) + "," + str(self.column) + ">"


class ProcessProgram:
    def __init__(self, program):
        self.current_line = 0
        self.current_column = 0
        self.program = program

    def current_char(self):
        return self.program[self.current_line][self.current_column]

    def change_line(self):
        self.current_line += 1
        self.current_column = 0

    def forward(self):
        # print self.current_line, self.current_column
        char = self.current_char()
        if char == "\n":
            self.current_line += 1
            self.current_column = 0
        else:
            self.current_column += 1
        return char

    def backward(self):
        if self.current_column > 0:
            self.current_column -= 1

    def end(self):
        return self.current_line >= len(self.program)


class DictionaryRegExp:

    simple_token = {"+": "tk_mas", "-": "tk_menos", "*": "tk_mult", "/": "tk_div", "%": "tk_mod", "=": "tk_asig",
                    "<": "tk_menor", ">": "tk_mayor", "@": "tk_menor_igual", "?": "tk_mayor_igual", "$": "tk_igual",
                    "|": "tk_o", "\\": "tk_dif", "!": "tk_neg", ":": "tk_dosp", ";": "tk_pyc", "(": "tk_par_izq",
                    ")": "tk_par_der", ".": "tk_punto", "&": "tk_y", ",": "tk_coma"}
    compound_token = {"funcion_principal": "funcion_principal", "fin_principal": "fin_principal", "funcion": "funcion",
                      "entero": "entero", "caracter": "caracter", "real": "real", "booleano": "booleano",
                      "cadena": "cadena", "imprimir": "imprimir", "retornar": "retornar", "estructura": "estructura",
                      "fin_estructura": "fin_estructura", "leer": "leer", "si": "si", "entonces": "entonces",
                      "fin_si": "fin_si", "si_no": "si_no", "mientras": "mientras", "hacer": "hacer",
                      "fin_mientras": "fin_mientras", "para": "para", "fin_para": "fin_para",
                      "seleccionar": "seleccionar", "entre": "entre", "caso": "caso", "romper": "romper",
                      "defecto": "defecto", "fin_seleccionar": "fin_seleccionar", "verdadero": "verdadero",
                      "falso": "falso", "fin_funcion": "fin_funcion"}

    lex_token = {"-?\d+": "tk_entero", "-?\d+\.\d+": "tk_real", "\".*\"": "tk_cadena", "\'.{0,1}\'": "tk_caracter",
                 "[a-zA-Z][\w_-]*": "id"}
    TOKEN = 0
    LEX_TOKEN = 1
    MAX_SIZE_SIMPLE_TOKEN = 2

    def __init__(self, process_program):
        self.proc_prog = process_program
        self.current_lexer = ""
        self.start_line_lexer = 0
        self.start_column_lexer = 0
        self.STRING = False
        self.COMMENT = False
        self.CHAR = False
        self.STREND = False
        self.CHREND = False
        self.tokens_val = []
        self.tokens = []

    def get_simple_token(self):
        backwards = 2
        check = False

        token = ""
        for i in range(1, self.MAX_SIZE_SIMPLE_TOKEN + 1):
            token += self.proc_prog.current_char()
            self.proc_prog.forward()
            if token in self.simple_token.keys():
                check = True
                backwards = i
                break

        for i in range(backwards):
            self.proc_prog.backward()

        # print "token", token
        return token if check else ""

    def get_tokens(self):
        end_tokens = [" ", "\n", "\t"]
        special_case = ["\"", "\'"]

        while not self.proc_prog.end():
            char = self.proc_prog.forward()
            if self.current_lexer == "" and char in self.simple_token:
                self.current_lexer = char

            # line comment
            if char == '#':
                self.proc_prog.change_line()
                self.start_line_lexer = self.proc_prog.current_line
                self.start_column_lexer = self.proc_prog.current_column
                self.current_lexer = ""
                continue

            # string mode
            if char == '\"' or self.STRING:
                if char == '\"':
                    if self.STRING:
                        self.STREND = True
                    self.STRING = not self.STRING
                if not self.STREND:
                    self.current_lexer += char
                    continue
                else:
                    self.current_lexer += char

            # char mode
            if char == '\'' or self.CHAR:
                if char == '\'':
                    if self.CHAR:
                        self.CHREND = True
                    self.CHAR = not self.CHAR
                if not self.CHREND:
                    self.current_lexer += char
                    continue
                else:
                    self.current_lexer += char

            # comment mode
            if char == '{':
                self.COMMENT = not self.COMMENT
                self.current_lexer = ""
                continue

            try:
                if (type(int(self.current_lexer)) is int) and char == '.':
                    self.current_lexer += char
                    continue
            except ValueError:
                # print ">>> Not number"
                None

            if char in end_tokens or char in self.simple_token or char in special_case:

                if not self.COMMENT:
                    try:
                        result = self.process_current_lexer()
                    except LexicalError as e:
                        print ">>> " + str(e)
                        return

                if not self.COMMENT:
                    if not result:
                        self.start_line_lexer = self.proc_prog.current_line
                        self.start_column_lexer = self.proc_prog.current_column
                        continue

                if not self.COMMENT:
                    #print result[self.TOKEN]
                    self.tokens_val.append(str(result[self.TOKEN])+"\n")
                    self.tokens.append(result[self.TOKEN])

                if not self.COMMENT:
                    if result[self.LEX_TOKEN] and not self.STREND and not self.CHREND:
                        proc_prog.backward()
                    else:
                        self.STREND = False
                        self.CHREND = False

                self.start_line_lexer = self.proc_prog.current_line
                self.start_column_lexer = self.proc_prog.current_column
                self.current_lexer = ""
            else:
                self.current_lexer += char
        end = Token("EOF", self.start_line_lexer, self.start_column_lexer)
        self.tokens.append(end)

    def process_current_lexer(self):
        if self.current_lexer == "":
            return False
        if self.current_lexer in self.simple_token.keys():
            return Token(self.simple_token[self.current_lexer], self.start_line_lexer, self.start_column_lexer), False
        if self.current_lexer in self.compound_token.keys():
            return Token(self.compound_token[self.current_lexer], self.start_line_lexer, self.start_column_lexer), True
        for regexp in self.lex_token.keys():
            pattern = re.compile(regexp)
            if pattern.match(self.current_lexer):
                return Token(self.lex_token[regexp], self.start_line_lexer, self.start_column_lexer, self.current_lexer), True

        raise LexicalError(self.start_line_lexer, self.start_column_lexer)


def transform(program):

    for i in range(len(program)):
        keys = transformations.keys()
        # special cases
        for key in keys:
            program[i] = program[i].replace(key, transformations[key])


class LexicalError:
    def __init__(self, line, column):
        self.line = line + 1
        self.column = column + 1

    def __str__(self):
        return "Error lexico (linea: " + str(self.line) + ", posicion: " + str(self.column) + ")"

simbols = {"tk_mas":"+","tk_menos":"-","tk_mult":"*","tk_div":"=","tk_mod":"%","tk_asig":"=","tk_menor":"<","tk_mayor":"+>",
           "tk_menor_igual":"<=","tk_mayor_igual":">=","tk_igual":"==","tk_y":"&&","tk_o":"||","tk_dif":"!=","tk_neg":"!",
           "tk_dosp":":", "tk_pyc":";", "tk_coma":",", "tk_punto":".", "tk_par_izq":"(", "tk_par_der":")", "id":"identificador",
           "tk_entero":"valor_entero", "tk_real":"valor_real", "tk_caracter":"valor_caracter", "tk_cadena":"valor_cadena"}

order = {"tk_mas": 1,"tk_menos": 2, "tk_mult": 3,"tk_div":4, "tk_mod":5, "tk_asig":6, "tk_menor":7, "tk_mayor":8,
         "tk_menor_igual":9,"tk_mayor_igual":10,"tk_igual":11,"tk_y":12,"tk_o":13,"tk_dif":14,"tk_neg":15,
         "tk_dosp":16, "tk_pyc":17, "tk_coma":18, "tk_punto":19, "tk_par_izq":20, "tk_par_der":21, "id":22,
         "tk_entero":23, "tk_real":24, "tk_caracter":25, "tk_cadena":26, "funcion_principal": 27, "fin_principal": 28,
         "funcion": 53,
         "leer": 29, "imprimir": 30, "booleano": 31, "caracter":32, "entero":33,  "real": 34, "cadena": 35, "si": 36,
         "entonces": 37, "fin_si": 38, "si_no": 39, "mientras": 40, "hacer": 41, "fin_mientras": 41, "para": 42,
         "fin_para": 43, "retornar": 55, "estructura": 50,"fin_estructura": 52,
         "seleccionar": 44, "entre": 45, "caso": 46, "romper": 47,"defecto": 48,
         "fin_seleccionar": 49, "verdadero": 57, "falso": 56, "fin_funcion": 54, "EOF":58}


class SyntacticalError:
    def __init__(self, token, expected_tokens):
        self.line = token.line
        self.column = token.column
        self.token = token.token
        self.lexer = token.lexer
        self.expected_tokens = sorted(expected_tokens, key = lambda tk: order[tk],reverse = False)
        for i in range(len(expected_tokens)):
            if self.expected_tokens[i] in simbols.keys():
                self.expected_tokens[i] = "\"" + simbols[self.expected_tokens[i]] + "\""
            else:
                self.expected_tokens[i] = "\"" + self.expected_tokens[i] + "\""

        if self.token in simbols.keys():
            self.token = "\""+simbols[self.token]+"\""
        else:
            self.token = "\""+self.token+"\""

    def __str__(self):

        return "<"+ str(self.line)+","+str(self.column)+"> Error Sintactico: se encontro "+ (self.lexer if self.lexer != "" else self.token)+\
                " se esperaba: "+ ','.join(self.expected_tokens)


class SyntacticalAnalyser:

    def __init__(self, lexical):
        self.tokens = lexical.tokens
        self.index = 0
        self.current_token = self.tokens[self.index]
        self.funcion_principal = False

    def next_token(self):
        self.index += 1
        self.current_token = self.tokens[self.index]
        return self.current_token

    def match(self, token):
        if not token == self.current_token.token:
            raise SyntacticalError(self.current_token, [token])
        else:
            self.next_token()

    def program(self):
        if self.current_token.token in ["estructura", "funcion", "funcion_principal"]:
            self.element()
            self.program()
        elif self.current_token.token in ["EOF"]:
            if not self.funcion_principal:
                print "Error sintactico: falta funcion_principal"
            else:
                print "El analisis sintactico ha finalizado exitosamente."
        else:
            raise SyntacticalError(self.current_token, ["estructura", "funcion", "funcion_principal"])

    def element(self):
        err_token = ["fin_principal","id", "entero","real","booleano", "caracter", "cadena","si","leer","imprimir",
                                        "para", "hacer", "mientras", "seleccionar", "romper","retornar"]
        if self.current_token.token in ["funcion"]:
            self.match("funcion")
            self.element_pri(err_token)
        elif self.current_token.token in ["funcion_principal"]:
            self.funcion_principal = True
            self.match("funcion_principal")
            self.cmp_declaration()
            try:
                self.match("fin_principal")
            except SyntacticalError:
                err_token.append("fin_principal")
                raise SyntacticalError(self.current_token, err_token)
        elif self.current_token.token in ["estructura"]:
            self.match("estructura")
            self.match("id")
            self.cmp_declaration()
            try:
                self.match("fin_estructura")
            except SyntacticalError:
                err_token.append("fin_estructura")
                raise SyntacticalError(self.current_token, err_token)
        else:
            raise SyntacticalError(self.current_token, ["funcion", "funcion_principal", "estructura"])

    def element_pri(self, err_token):
        if self.current_token.token in ["entero","real","booleano", "caracter", "cadena"]:
            self.type_var()
            self.match("id")
            self.match("tk_par_izq")
            self.params()
            self.match("tk_par_der")
            self.match("hacer")
            self.cmp_declaration()
            try:
                self.match("fin_funcion")
            except SyntacticalError:
                err_token.append("fin_funcion")
                raise SyntacticalError(self.current_token, err_token)
        elif self.current_token.token in ["id"]:
            self.match("id")
            self.match("id")
            self.match("tk_par_izq")
            self.params()
            self.match("tk_par_der")
            self.match("hacer")
            self.cmp_declaration()
            try:
                self.match("fin_funcion")
            except SyntacticalError:
                err_token.append("fin_funcion")
                raise SyntacticalError(self.current_token, err_token)
        else:
            raise SyntacticalError(self.current_token, ["entero","real","booleano", "caracter", "cadena", "id"])


    def params(self):
        if self.current_token.token in ["entero","real","booleano", "caracter", "cadena","id"]:
            self.mandatory_params()
        #else:
            #raise SyntacticalError(self.current_token, ["entero","real","booleano", "caracter", "cadena"])


    def mandatory_params(self):
        if self.current_token.token in ["entero","real","booleano", "caracter", "cadena"]:
            self.type_var()
            self.match("id")
            self.mandatory_params_pri()
        elif self.current_token.token in ["id"]:
            self.match("id")
            self.match("id")
            self.mandatory_params_pri()
        else:
            raise SyntacticalError(self.current_token, ["entero","real","booleano", "caracter", "cadena","id"])

    def mandatory_params_pri(self):
        if self.current_token.token in ["tk_coma"]:
            self.match("tk_coma")
            self.mandatory_params()

    def dSyn(self):
        if self.current_token.token in ["id"]:
            self.identifier_id()
            self.dSyn_fun()
        elif self.current_token.token in ["entero","real","booleano", "caracter", "cadena"]:
            self.type_var()
            self.match("id")
            self.dSyn_pri()
        else:
            raise SyntacticalError(self.current_token, ["id","entero","real","booleano", "caracter", "cadena"])

    def dSyn_fun(self):
        if self.current_token.token in ["id","tk_asig"]:
            self.dSyn_special()
        elif self.current_token.token in ["tk_par_izq"]:
            self.match("tk_par_izq")
            self.args_fun()
            self.match("tk_par_der")
        else:
            raise SyntacticalError(self.current_token, ["id","entero","real","booleano", "caracter", "cadena"])


    def dSyn_special(self):
        if self.current_token.token in ["id"]:
            self.match("id")
            self.dSyn_pri()
        elif self.current_token.token in ["tk_asig"]:
            self.match("tk_asig")
            self.exp()
        else:
            raise SyntacticalError(self.current_token, ["id","tk_asig"])


    def dSyn_pri(self):
        if self.current_token.token in ["tk_asig"]:
            self.match("tk_asig")
            self.exp()
            self.dSyn_pri_pri()
        if self.current_token.token in ["tk_coma"]:
            self.dSyn_pri_pri()
        #else:
            #raise SyntacticalError(self.current_token, ["tk_asig"])

    def dSyn_pri_pri(self):
        if self.current_token.token in ["tk_coma"]:
            self.match("tk_coma")
            self.match("id")
            self.dSyn_id()


    def dSyn_id(self):
        if self.current_token.token in ["tk_asig"]:
            self.match("tk_asig")
            self.exp()
            self.dSyn_pri_pri()
        if self.current_token.token in ["tk_coma"]:
            self.dSyn_pri_pri()


    def args_fun(self):
        if self.current_token.token in ["id", "tk_par_izq" ,"tk_entero" ,"tk_real" ,"tk_caracter" ,"tk_cadena",
                                        "verdadero", "falso"]:
            self.exp()
            self.args_fun_pri()

    def args_fun_pri(self):
        if self.current_token.token in ["tk_coma"]:
            self.match("tk_coma")
            self.exp()
            self.args_fun_pri()

    def type_var(self):
        if self.current_token.token in ["entero"]:
            self.match("entero")
        elif self.current_token.token in ["real"]:
            self.match("real")
        elif self.current_token.token in ["booleano"]:
            self.match("booleano")
        elif self.current_token.token in ["caracter"]:
            self.match("caracter")
        elif self.current_token.token in ["cadena"]:
            self.match("cadena")
        else:
            raise SyntacticalError(self.current_token, ["entero","real","booleano", "caracter", "cadena"])

    def declaration(self):
        if self.current_token.token in ["id", "entero","real","booleano", "caracter", "cadena"]:
            self.dSyn()
            self.match("tk_pyc")
        elif self.current_token.token in ["si"]:
            self.match("si")
            self.match("tk_par_izq")
            self.exp()
            self.match("tk_par_der")
            self.match("entonces")
            self.cmp_declaration()
            self.declaration_if_pri()
        elif self.current_token.token in ["leer"]:
            self.match("leer")
            self.match("tk_par_izq")
            self.identifier_id()
            self.match("tk_par_der")
            self.match("tk_pyc")
        elif self.current_token.token in ["imprimir"]:
            self.match("imprimir")
            self.match("tk_par_izq")
            self.str_struct()
            self.match("tk_par_der")
            self.match("tk_pyc")
        elif self.current_token.token in ["mientras"]:
            self.match("mientras")
            self.match("tk_par_izq")
            self.exp()
            self.match("tk_par_der")
            self.match("hacer")
            self.cmp_declaration()
            self.match("fin_mientras")
        elif self.current_token.token in ["para"]:
            self.match("para")
            self.match("tk_par_izq")
            self.dSyn()
            self.match("tk_pyc")
            self.exp()
            self.match("tk_pyc")
            self.end_loop()
            self.match("tk_par_der")
            self.match("hacer")
            self.cmp_declaration()
            self.match("fin_para")
        elif self.current_token.token in ["hacer"]:
            self.match("hacer")
            self.cmp_declaration(True)
            self.match("mientras")
            self.match("tk_par_izq")
            self.exp()
            self.match("tk_par_der")
            self.match("tk_pyc")
        elif self.current_token.token in ["seleccionar"]:
            self.match("seleccionar")
            self.match("tk_par_izq")
            self.identifier()
            self.match("tk_par_der")
            self.match("entre")
            self.case()
            self.match("fin_seleccionar")
        elif self.current_token.token in ["romper"]:
            self.match("romper")
            self.match("tk_pyc")
        elif self.current_token.token in ["retornar"]:
            self.match("retornar")
            self.exp()
            self.match("tk_pyc")
        else:
            raise SyntacticalError(self.current_token, ["romper", "seleccionar", "hacer", "para", "mientras", "imprimir",
                                                        "leer", "si", "id", "entero","real","booleano", "caracter", "cadena","retornar"])

    def declaration_if_pri(self):
        if self.current_token.token in ["fin_si"]:
            self.match("fin_si")
        elif self.current_token.token in ["si_no"]:
            self.match("si_no")
            self.cmp_declaration()
            self.match("fin_si")
        else:
            raise SyntacticalError(self.current_token, ["fin_si","si_no"])

    def end_loop(self):
        if self.current_token.token in ["id"]:
            self.match("id")
        elif self.current_token.token in ["tk_entero"]:
            self.match("tk_entero")
        elif self.current_token.token in ["tk_real"]:
            self.match("tk_real")
        else:
            raise SyntacticalError(self.current_token, ["id","tk_entero","tk_real"])

    def str_struct(self):
        if self.current_token.token in ["id", "tk_par_izq" ,"tk_entero" ,"tk_real" ,"tk_caracter" ,"tk_cadena",
                                        "verdadero", "falso"]:
            self.exp()
            self.str_struct_pri()
        else:
            raise SyntacticalError(self.current_token, ["id", "tk_par_izq" ,"tk_entero" ,"tk_real" ,"tk_caracter" ,
                                                        "tk_cadena", "verdadero", "falso"])

    def str_struct_pri(self):
        if self.current_token.token in ["tk_coma"]:
            self.match("tk_coma")
            self.str_struct()
        #elif self.current_token.token in ["tk_par_der"]:
           #self.match("tk_par_der")


    def case(self):
        if self.current_token.token in ["caso"]:
            self.match("caso")
            self.terminal()
            self.match("tk_dosp")
            self.cmp_declaration()
            self.case()
        elif self.current_token.token in ["defecto"]:
            self.match("defecto")
            self.match("tk_dosp")
            self.cmp_declaration()
        else:
            raise SyntacticalError(self.current_token, ["caso", "defecto"])

    def cmp_declaration(self,dowhile = False):
        if self.current_token.token in ["id", "entero","real","booleano", "caracter", "cadena","si","leer","imprimir",
                                        "para", "hacer", "mientras", "seleccionar", "romper","retornar"]:
            if dowhile and self.current_token.token == "mientras":
                return
            self.declaration()
            self.cmp_declaration(dowhile)
        if self.current_token.token in ["fin_principal"]:
            return

        #elif self.current_token.token in ["fin_si","si_no","fin_mientras", "fin_para", "mientras", "caso", "defecto",
         #                                 "fin_seleccionar","fin_funcion","fin_principal","fin_estructura"]:
            #self.match(self.current_token.token)

    def exp(self):
        if self.current_token.token in ["id","tk_entero" ,"tk_real" ,"tk_caracter" ,"tk_cadena", "verdadero", "falso"]:
            self.terminal()
            self.exp_pri()
        elif self.current_token.token in ["tk_par_izq"]:
            self.match("tk_par_izq")
            self.exp()
            self.match("tk_par_der")
            self.exp_pri()
        else:
            raise SyntacticalError(self.current_token, ["id","tk_par_izq","tk_entero" ,"tk_real" ,"tk_caracter" ,
                                                        "tk_cadena", "verdadero", "falso"])

    def exp_pri(self):
        if self.current_token.token in ["tk_mas", "tk_menos","tk_mult", "tk_div", "tk_mod", "tk_menor", "tk_mayor",
                                        "tk_menor_igual", "tk_mayor_igual","tk_igual","tk_o","tk_dif", "tk_neg",
                                        "tk_y"]:
            self.match(self.current_token.token)
            self.exp()
            self.exp_pri()

    def identifier(self):
        if self.current_token.token in ["id"]:
            self.match("id")
            self.identifier_fun()
        else:
            raise SyntacticalError(self.current_token, ["id"])

    def identifier_id(self):
        if self.current_token.token in ["id"]:
            self.match("id")
            self.identifier_id_pri()
        else:
            raise SyntacticalError(self.current_token, ["id"])

    def identifier_fun(self):
        if self.current_token.token in ["tk_mas", "tk_menos","tk_mult", "tk_div", "tk_mod", "tk_menor", "tk_mayor",
                                        "tk_menor_igual", "tk_mayor_igual","tk_igual","tk_o","tk_dif", "tk_neg",
                                        "tk_y","tk_punto","tk_par_der","tk_pyc"]:
            self.identifier_pri()
        elif self.current_token.token in ["tk_par_izq"]:
            self.match("tk_par_izq")
            self.args_fun()
            self.match("tk_par_der")
        else:
            raise SyntacticalError(self.current_token, ["tk_mas", "tk_menos","tk_mult", "tk_div", "tk_mod", "tk_menor", "tk_mayor",
                                        "tk_menor_igual", "tk_mayor_igual","tk_igual","tk_o","tk_dif", "tk_neg",
                                        "tk_y","tk_punto","tk_par_izq","tk_par_der"])

    def identifier_pri(self):
        if self.current_token.token in ["tk_punto"]:
            self.match("tk_punto")
            self.identifier()

    def identifier_id_pri(self):
        if self.current_token.token in ["tk_punto"]:
            self.match("tk_punto")
            self.identifier_id()

    def terminal(self):
        if self.current_token.token in ["id"]:
            self.identifier()
        elif self.current_token.token in ["id","tk_entero" ,"tk_real" ,"tk_caracter" ,"tk_cadena", "verdadero", "falso"]:
            self.match(self.current_token.token)




def read_file(file_name):
    lines = []
    file_data = open(file_name, "r")
    for line in file_data:
        lines.append(line)
    lines[len(lines)-1] += "\n"

    for i in range(len(lines)):
        lines[i] = lines[i].replace("\r", "")
    return lines

# Cambiar n para el numero y l para la letra de los casos de prueba
n = 5
l = "D"
file_init = "./problemas_juez/L1"+l+"_2016_"+str(n)

program = []

program = read_file(file_init+".in")

transform(program)
proc_prog = ProcessProgram(program)
a = DictionaryRegExp(proc_prog)
a.get_tokens()
tokens_list = a.tokens
"""
print "----------------SOLUCION----------------------------"
out = read_file(file_init+".out")
out[len(out)-1] = out[len(out)-1].replace("\n\n", "\n")
# print "".join(out)

print "----------------Assert----------------------------"

for i in range(len(tokens_list)):
    try:
        assert out[i] == tokens_list[i]
    except AssertionError:
        print ">>> Error " + tokens_list[i]+" != "+out[i]+" >>Linea "+str(i+1)

"""
print "------------------Sintactico----------------------------"

sintactical = SyntacticalAnalyser(a)

sintactical.program()

