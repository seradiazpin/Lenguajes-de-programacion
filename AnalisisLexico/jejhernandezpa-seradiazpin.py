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
                    ".": "tk_punto", "&": "tk_y"}
    compound_token = {"funcion_principal": "funcion_principal", "fin_principal": "fin_principal", "funcion": "funcion", "entero": "entero", "caracter": "caracter", "real": "real",
                      "booleano": "booleano", "cadena": "cadena", "imprimir" : "imprimir", "retornar": "retornar", "estructura": "estructura", "fin_estructura": "fin_estructura",
                      "leer": "leer", "si": "si", "entonces": "entonces", "fin_si": "fin_si", "si_no": "si_no", "mientras": "mientras", "hacer": "hacer", "fin_mientras": "fin_mientras",
                      "para": "para", "fin_para": "fin_para", "seleccionar": "seleccionar", "entre": "entre", "caso": "caso", "romper": "romper", "defecto": "defecto",
                      "fin_seleccionar": "fin_seleccionar"}
    lex_token = {"-?\d+":"tk_entero", "-?\d+\.\d+": "tk_real", "\".*\"": "tk_cadena", "\'(.| )\'": "tk_caracter", "verdadero|falso": "tk_booleano", "[a-zA-Z][\w_-]*": "tk_id"}
    TOKEN = 0
    LEX_TOKEN = 1
    MAX_SIZE_SIMPLE_TOKEN = 2

    def __init__(self, process_program):
        self.proc_prog = process_program
        self.current_lexer = ""
        self.start_line_lexer = 0
        self.start_column_lexer = 0
        self.STRING = False;
        self.COMMENT = False;

    def preprocess_token(self, token):
        tok = token[self.TOKEN]
        if(tok == "tk_caracter"):
            tok.lexer = tok.lexer.replace("'", "")
        if(tok.token == "tk_cadena"):
            tok.lexer = tok.lexer.replace("\"", "")
        return (tok, token[self.LEX_TOKEN])

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
                    self.STRING = not self.STRING
                self.current_lexer += char
                continue

            # comment mode
            if char == '{':
                self.COMMENT = not self.COMMENT
                self.current_lexer = ""
                continue

            if(char in end_tokens or char in self.simple_token):

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

                result1 = self.preprocess_token(result)

                if not self.COMMENT:
                    print result1[self.TOKEN]

                if(result[self.LEX_TOKEN]):
                    proc_prog.backward()
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

program = []
file = open("program.txt", "r")
for line in file:
    program.append(line)

program[len(program)-1] += "\n"

#program = ["funcion_principal\n", "imprimir(3<=5)\n", "fin_principal \n", "+\n"]
transform(program)
#print "\n".join(program)

proc_prog = Process_program(program)
DictionaryRegExp(proc_prog).get_tokens()


