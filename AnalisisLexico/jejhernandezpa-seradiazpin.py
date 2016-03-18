import re

# Transformations

transformations = {">=": "? ", "<=": "@ ", "==": "$ ", "!=": "\\ ", "&&": "& ", "||": "| ", "//": '# ', "/*": '{ ', "*/": '{ '}

class Token:
    def __init__(self, token, line, column, lexer=""):
        self.token = token
        self.line = line + 1
        self.column = column + 1
        self.lexer = lexer

    def __str__(self):
        return "<" + self.token + "," + ("" if self.lexer == "" else self.lexer + ",") + str(self.line) + "," + str(self.column) + ">"

class Process_program:
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
        #print self.current_line, self.current_column
        char = self.current_char()
        if(char == "\n"):
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


    simple_token = {"+": "tk_mas", "-": "tk_menos", "*": "tk_mult", "/": "tk_div", "%": "tk_mod", "=": "tk_asig", "<" : "tk_menor", ">": "tk_mayor", "@": "tk_menor_igual",
                    "?": "tk_mayor_igual", "$": "tk_igual",  "|": "tk_o", "\\": "tk_diff", "!": "tk_neg", ":": "tk_dosp", ";": "tk_pyc", "(": "tk_par_izq", ")": "tk_par_der",
                    ".": "tk_punto", "&": "tk_y",",":"tk_coma"}
    compound_token = {"funcion_principal": "funcion_principal", "fin_principal": "fin_principal", "funcion": "funcion", "entero": "entero", "caracter": "caracter", "real": "real",
                      "booleano": "booleano", "cadena": "cadena", "imprimir" : "imprimir", "retornar": "retornar", "estructura": "estructura", "fin_estructura": "fin_estructura",
                      "leer": "leer", "si": "si", "entonces": "entonces", "fin_si": "fin_si", "si_no": "si_no", "mientras": "mientras", "hacer": "hacer", "fin_mientras": "fin_mientras",
                      "para": "para", "fin_para": "fin_para", "seleccionar": "seleccionar", "entre": "entre", "caso": "caso", "romper": "romper", "defecto": "defecto",
                      "fin_seleccionar": "fin_seleccionar", "verdadero":"verdadero", "falso":"falso", "fin_funcion":"fin_funcion"}
    lex_token = {"-?\d+":"tk_entero", "-?\d+\.\d+": "tk_real", "\".*\"": "tk_cadena", "\'.{0,1}\'": "tk_caracter", "[a-zA-Z][\w_-]*": "id"}
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


        #print "token", token
        return token if check else ""


    def get_tokens(self):
        tokens = []
        end_tokens = [" ", "\n", "\t"]
        special_case = ["\"", "\'"]
        while(not self.proc_prog.end()):
            char = self.proc_prog.forward()
            simple_token = ""

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

            #char mode
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

            if char in end_tokens or char in self.simple_token or char in special_case:

                if not self.COMMENT:
                    try:
                        result = self.process_current_lexer()
                    except LexicalError as e:
                        print ">>> " + str(e)
                        return

                if result == False:
                    self.start_line_lexer = self.proc_prog.current_line
                    self.start_column_lexer = self.proc_prog.current_column
                    continue # todo

                if not self.COMMENT:
                    print result[self.TOKEN]
                    self.tokens.append(str(result[self.TOKEN])+"\n")

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

    def process_current_lexer(self):
        if self.current_lexer == "":
            return False
        if self.current_lexer in self.simple_token.keys():
            return (Token(self.simple_token[self.current_lexer], self.start_line_lexer, self.start_column_lexer), False)
        if self.current_lexer in self.compound_token.keys():
            return (Token(self.compound_token[self.current_lexer], self.start_line_lexer, self.start_column_lexer), True)
        for regexp in self.lex_token.keys():
            pattern = re.compile(regexp)
            if pattern.match(self.current_lexer):
                return (Token(self.lex_token[regexp], self.start_line_lexer, self.start_column_lexer, self.current_lexer), True)

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


def read_file(file_name):
    lines = []
    file_data = open(file_name, "r")
    for line in file_data:
        lines.append(line)
    lines[len(lines)-1] += "\n"

    for i in range(len(lines)):
        lines[i] = lines[i].replace("\r","")
    return lines

n = 4
l = "A"
file_init = "./problemas_juez/L1"+l+"_2016_"+str(n)

program = []

program = read_file(file_init+".in")

transform(program)

proc_prog = Process_program(program)
a = DictionaryRegExp(proc_prog)
a.get_tokens()
tokens_list = a.tokens
print "----------------SOLUCION----------------------------"
out = read_file(file_init+".out")
out[len(out)-1] = out[len(out)-1].replace("\n\n","\n")
#print "".join(out)

print "----------------Assert----------------------------"

for i in range(len(tokens_list)):
    try:
        assert out[i] == tokens_list[i]
    except AssertionError:
        print ">>> Error " + tokens_list[i]+" != "+out[i]+" >>Linea "+str(i+1)




