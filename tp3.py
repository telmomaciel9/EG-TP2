from lark import Lark,Tree,Token
from lark.tree import pydot__tree_to_png
from lark.visitors import Interpreter
import html
import re

# def inicio_fim(string):
#     first_quote_index = string.find('"')
#     last_quote_index = string.rfind('"')
    
#     if first_quote_index != -1 and last_quote_index != -1:
#         first_quote = string[first_quote_index + 1: string.find('"', first_quote_index + 1)]
#         last_quote = string[string.rfind('"', 0, last_quote_index) + 1: last_quote_index]
#         return first_quote.strip(), last_quote.strip()
#     else:
#         return None, None

import re

def remove_whitespace(array):
    for i in range(len(array)):
        array[i] = array[i].strip()


def inicio_fim(string):
    quote_indices = [i for i, char in enumerate(string) if char == '"']
    
    if len(quote_indices) >= 2:
        first_quote = string[quote_indices[0] + 1: quote_indices[1]]
        last_quote = string[quote_indices[-2] + 1: quote_indices[-1]]
        
        if last_quote.strip() == "" and len(quote_indices) >= 4:
            last_quote = string[quote_indices[-4] + 1: quote_indices[-3]]
            
        return first_quote.strip(), last_quote.strip()
    else:
        return None, None

def extract_values_to_string(data):
    if isinstance(data, list):
        result = []
        for item in data:
            result.append(extract_values_to_string(item))
        return ' '.join(result)
    else:
        return str(data)

def comparatorIdentifier(dic):
    tipo = dic[0]
    temValue = dic[1]
    boolRedecl = dic[2]
    bool2 = dic[3]
    bool3 = dic[4]
    bool4 = dic[5]
    
    if(tipo != None): # Tem tipo
        bool4 = True
    
    if(not(temValue)):
        bool3 = True
    
    dic = (tipo,temValue,boolRedecl,bool2,bool3,bool4)
    return dic

def comparator(dic,tipoBOOL,tipoNOVO,declAuxValue):
    tipo = dic[0]
    temValue = dic[1]
    boolRedecl = dic[2]
    bool2 = dic[3]
    bool3 = dic[4]
    bool4 = dic[5]

    if(tipoBOOL): # Está a declarar com tipo
        if(tipo != None): # Já tem tipo então esta a redeclarar
            dic = (tipoNOVO,temValue,True,bool2,bool3,bool4)
        
        else: # Nao tem tipo e está a declarar com tipo, ou seja, foi usada sem tipo
            dic = (tipoNOVO,temValue,boolRedecl,True,bool3,bool4)

        return dic
    else: #Está a ser usada!


        if(tipo != None): # Tem tipo
            bool4 = True

        if(not(temValue)):
            if declAuxValue:
                temValue = True
            else:
                bool3 = True

        dic = (tipo,temValue,boolRedecl,bool2,bool3,bool4)

        return dic

class MyInterpreter(Interpreter):
    def __init__(self):
        self.dicVar = {} #key(nameVariavel-Scope|| tipo || temValue || Bool de nª de redlecarações, bool2,bool3, bool4(true=usada) )
        self.estrutura = []
        self.estruturasControlo = 0
        self.declAuxValue = False #saber se vem do assign_statement
        self.boolIF = False
        self.ifsMerge = 0
        self.dicInstrucoes = {
            'atribuicoes': 0, 
            'leitura': 0,
            'condicionais': 0,
            'ciclicas': 0
        }
        self.scope = "Global"
        self.arrayString = []

    def start(self, tree):
        print("Interpreter started")
        self.visit_children(tree)
        #self.stringGrafo = f"digraph Programa{{\n{self.stringGrafo}}}" #FALTA O INICIO E FIM
        print("Start", self.arrayString)
        arrayDasStrings = self.arrayString[::-1]
        stringGrafoFinal = ""
        if arrayDasStrings:
            print("Array das strings", arrayDasStrings)
            if re.search(r'"if .*" -> ""', arrayDasStrings[-1]):
                arrayDasStrings[-1] = re.sub(r'\n\s*"if .*" -> ""\n\s*', '\n', arrayDasStrings[-1])
            print("Array das strings", arrayDasStrings)
            
            stringGrafoFinal = "\n".join(arrayDasStrings)

        primeiro, ultimo = inicio_fim(stringGrafoFinal)

        stringGrafoFinal = f"""inicio -> "{primeiro}"{stringGrafoFinal}"{ultimo}" -> fim"""

        return self.dicVar, self.dicInstrucoes, self.ifsMerge, self.estruturasControlo, stringGrafoFinal

    def declaration(self, tree): #Define uma função, é preciso guardar a scope
        for elemento in tree.children:
            if (isinstance(elemento, Token) and elemento.type == 'IDENTIFIER'):
                self.scope = elemento
        self.visit_children(tree)
        self.scope = "Global"

    def paramsfunc(self, tree):
        self.visit_children(tree)

    def declfunc(self, tree):
        tipo = self.visit(tree.children[0]) or ""
        
        if len(tree.children) == 3:
            nomeVAR = str(tree.children[2])
            compTIPO = self.visit(tree.children[1]) or ""
            tipo = f"{tipo}-{compTIPO}"
        else:
            nomeVAR = str(tree.children[1])
        
        key = f"{nomeVAR}-{self.scope}"
        if key in self.dicVar:
            keyObject = self.dicVar[key]
            v = comparator(keyObject, True, tipo)   
            self.dicVar[key] = v 
        else:
            self.dicVar[key] = (tipo, True, False, False, False, False)

    def decl(self, tree):
        nomeVAR = None
        tipo = self.visit(tree.children[0]) or ""
        
        if len(tree.children) == 3:
            nomeVAR = str(tree.children[2])
            compTIPO = self.visit(tree.children[1]) or ""
            tipo = f"{tipo}-{compTIPO}"
        else:
            nomeVAR = tree.children[1]

        key = f"{nomeVAR}-{self.scope}"
        if key in self.dicVar:
            keyObject = self.dicVar[key]
            v = comparator(keyObject, True, tipo, self.declAuxValue)  
            self.dicVar[key] = v
        else:
            if self.declAuxValue:
                self.dicVar[key] = (tipo, True, False, False, False, False)
            else:
                self.dicVar[key] = (tipo, False, False, False, False, False)


        expressao = f"{tipo} {nomeVAR}" 
        
        return expressao
    
    def declsemtipo(self, tree):
        nomeVAR = str(tree.children[0])
        key = f"{nomeVAR}-{self.scope}"

        if key in self.dicVar:
            keyObject = self.dicVar[key]
            v = comparator(keyObject, False, None, self.declAuxValue)
            self.dicVar[key] = v
        elif self.declAuxValue: # Veio do assign_statement, ou seja, tem valor mas nao tem tipo
            self.dicVar[key] = (None, True, False, True, False, False)
        else:                           
            self.dicVar[key] = (None, False, False, True, True, False)

        return nomeVAR
    
    def statement(self, tree):
        return self.visit_children(tree)

    def body(self, tree):
        return self.visit_children(tree)

    def if_statement(self, tree): # exp body body?
        stringElse = ""
        if self.estrutura:
            self.estruturasControlo += 1

        self.dicInstrucoes['condicionais'] += 1

        if self.boolIF:
            self.ifsMerge += 1

        n = self.visit(tree.children[0]) or ""

        self.estrutura.append(True)
        self.boolIF = True

        exp = self.visit(tree.children[1]) or ""

        self.boolIF = False
        self.estrutura.pop()

        print("EXP", exp)   
        conteudo =  exp[0] if exp else ""
        stringG = f"""
        "if {extract_values_to_string(n)}" [shape=diamond];
        "if {extract_values_to_string(n)}" -> "{extract_values_to_string(conteudo)}"
        """

        if len(exp) > 1:
            pattern = r'"([^"]*)"'
            for element in exp[1:]:
                match = re.search(pattern, extract_values_to_string(element))
                if match:
                    print("Match", match.group(1))
                    stringG += f"""
                "{extract_values_to_string(exp[0])}" -> "{match.group(1)}"
                    """

        numeroFilhos = len(tree.children)
        if numeroFilhos == 3:
            expElse = self.visit(tree.children[2]) or ""
            stringElse = f"""
            "if {extract_values_to_string(n)}" -> "{extract_values_to_string(expElse)}"
            """

        stringG += stringElse
        self.arrayString.append(stringG)
        return stringG

    def while_statement(self, tree):
        self.boolIF = False

        if self.estrutura:
            self.estruturasControlo += 1
        
        self.dicInstrucoes['ciclicas'] += 1
    
        self.estrutura.append(True)
        exp = self.visit(tree.children[0]) or ""
        body = self.visit(tree.children[1]) or ""
        self.estrutura.pop()

        string = f"""
        "while {exp}" [shape=diamond];
        "while {exp}" -> "{body}"[label="true"];
        "{body}" -> "while {exp}"
        "while {exp}" -> ""[label="false"]; 
        """
        self.arrayString.append(string)
        return string

    def for_statement(self, tree):
        self.boolIF = False

        if self.estrutura:
            self.estruturasControlo += 1
        
        self.dicInstrucoes['ciclicas'] += 1
        self.dicInstrucoes['atribuicoes'] += 1
        self.dicInstrucoes['leitura'] += 1

        self.estrutura.append(True)
        exp = self.visit_children(tree) or ""
        self.estrutura.pop()
        return exp

    def assign_statement(self, tree):
        self.boolIF = False

        self.dicInstrucoes['atribuicoes'] += 1
        self.declAuxValue = True
        exp = self.visit_children(tree) or ""
        self.declAuxValue = False
        string = f"""
        "{tree.children[0]}" -> "{exp}"
        """
        self.arrayString.append(string)
        return string

    def print_statement(self, tree):
        self.boolIF = False

        exp = self.visit_children(tree) or ""
        string = f"""
        "print" -> "{exp}"
        """
        self.arrayString.append(string)
        return string

    def declare_statement(self, tree):
        self.boolIF = False
        exp = self.visit_children(tree) or ""
        

        return extract_values_to_string(exp)
    
    def call_function(self, tree):
        self.boolIF = False

        exp = self.visit_children(tree) or ""
        string = f"""
        "call" -> "{exp}"
        """
        self.arrayString.append(string)
        return string

    def return_statement(self, tree):

        self.boolIF = False

        exp = self.visit_children(tree) or ""
        string = f"""
        "return" -> "{exp}"
        """
        self.arrayString.append(string)
        return string

    def switch_case_statement(self, tree):
        self.boolIF = False

        if self.estrutura:
            self.estruturasControlo += 1
        
        self.dicInstrucoes['condicionais'] += 1
        self.visit_children(tree)

        self.estrutura.append(True)
        exp = self.visit(tree.children[1]) or ""  # Visita novamente o corpo do switch_case para verificar aninhamentos
        self.estrutura.pop()
        return exp

    def switch_case_branch(self, tree):
        return self.visit_children(tree) or ""

    def args(self, tree):
        return self.visit_children(tree) or ""

    def expr(self, tree): 
        return self.visit_children(tree) or ""

    def value(self, tree):
        if isinstance(tree.children[0], Token) and tree.children[0].type == 'IDENTIFIER':
            self.dicInstrucoes['leitura'] += 1
            value = str(tree.children[0])
            key = f"{value}-{self.scope}"
            if key in self.dicVar:
                dic = self.dicVar[key]
                v = comparatorIdentifier(dic)
                self.dicVar[key] = v
            else:
                self.dicVar[key] = (None, False, False, True, True, False) 
            
            return value
        else:   
            return self.visit_children(tree) or ""

    def array_access(self, tree):
        self.boolIF = False

        value = str(tree.children[0])
        key = f"{value}-{self.scope}"
        if key in self.dicVar:
            dic = self.dicVar[key]
            v = comparatorIdentifier(dic)
            self.dicVar[key] = v
        else:
            self.dicVar[key] = (None, True, False, True, False, False)
        self.visit_children(tree)

    def set_access(self, tree):
        self.boolIF = False

        value = str(tree.children[0])
        key = f"{value}-{self.scope}"
        if key in self.dicVar:
            dic = self.dicVar[key]
            v = comparatorIdentifier(dic)
            self.dicVar[key] = v
        else:
            self.dicVar[key] = (None, True, False, True, False, False)
        self.visit_children(tree)

    def binary_op(self, tree):
        arrayAux = []

        for elemento in tree.children:
            if (isinstance(elemento, Tree) and elemento.data == 'binary_op_priority'):
                arrayAux.append(self.visit(elemento))
            else:
                arrayAux.append((elemento))
    
        return ' '.join(arrayAux)


    def unary_op(self, tree):
        return ' '.join([str(child) for child in tree.children])

    def binary_op_priority(self, tree): 
        return ' '.join([str(child) for child in tree.children])

    def int(self, tree):
        return str(tree.children[0])
    
    def string(self, tree):
        return str(tree.children[0])
    
    def tuple(self, tree):
        return ', '.join([str(child) for child in tree.children])

    def bool(self, tree):
        return str(tree.children[0])
    
    def array(self, tree):
        return ', '.join([self.visit(child) for child in tree.children])
    
    def set(self, tree):
        return ', '.join([self.visit(child) for child in tree.children])

    def comp_type(self, tree):
        return str(tree.children[0])

    def IDENTIFIER(self, tree):
        return str(tree.children[0])

    def type(self, tree):
        return str(tree.children[0])
    
    def INTEGER(self, tree):
        return str(tree.children[0])
    
    def BOOL(self, tree):
        return str(tree.children[0])
    
    def access(self, tree):
        return self.visit_children(tree) or ""




grammar = '''
start: (declaration | statement)*

declaration: type comp_type? IDENTIFIER "(" paramsfunc? ")" "{" body* "}"

paramsfunc: declfunc ("," declfunc)*

comp_type: (ARRAY | LIST | SET)

declfunc: type comp_type? IDENTIFIER 
decl: type comp_type? IDENTIFIER 
      | IDENTIFIER  -> declsemtipo

body: statement*

statement: if_statement
    | while_statement
    | for_statement
    | assign_statement ";"
    | print_statement ";"
    | declare_statement ";"
    | call_function ";"
    | return_statement ";"
    | switch_case_statement 
    | access ";"

if_statement: "if" "(" expr ")" "{" body "}" ("else" "{" body "}")?
while_statement: "while" "(" expr ")" "{" body "}"
for_statement: "for" "(" assign_statement ";" expr ";" decl unary_op ")" "{" body "}"
assign_statement: decl "=" (expr | call_function)
print_statement: "print" "(" expr ")"
declare_statement: decl
call_function: IDENTIFIER "(" args ")"
return_statement: "return" expr
access: array_access | set_access

switch_case_statement: "switch" "(" expr ")" "{" switch_case_branch* "}"

switch_case_branch: "case" value ":" body* "break" ";"
                  | "default" ":" body* "break" ";"

args: (expr  ("," expr)*)?

expr: value
    | "(" expr ")"
    | access 
    | expr binary_op expr
    | unary_op expr

value: BOOOL | IDENTIFIER | tuple | array | set | INTEGER | STRING 

binary_op: BINARY_OP | binary_op_priority
binary_op_priority: BINARY_OP_PRIORITY
unary_op: UNARY_OP

BINARY_OP: "==" | "!=" | "<=" | ">=" | "<" | ">" | "+" | "-" | "or"
BINARY_OP_PRIORITY: "*" | "/" | "%" | "^" | "and"
UNARY_OP: "++" | "--"


array_access: IDENTIFIER "[" value "]"
set_access: IDENTIFIER "{" value   "}"

type: INT
    | STRINGG
    | BOOL
    | BOOLEAN
    | TUPLE
    | VOID
    | FLOAT

INT: "int"
STRINGG: "string"
BOOL: "bool"
BOOLEAN: "boolean"
TUPLE: "tuple"
VOID: "void"
ARRAY: "array"
LIST: "list"
SET: "set"
FLOAT: "float"

int: INTEGER 
string: STRING
tuple: "(" (IDENTIFIER | STRING | INTEGER) ("," (IDENTIFIER | INTEGER | STRING))* ")"
bool: "true" | "false"
array: "[" value? ("," value)* "]"
set: "{" value? ("," value)* "}"

BOOOL: /(TRUE|FALSE)/
STRING: /"[^"]*"|'[^']*'/
IDENTIFIER: /[a-zA-Z_]\w*/
INTEGER: /\d+/

%import common.WS
%ignore WS

'''

frase0 = '''

if ( a * (a + b) ) {     
    int a; 
    int b;
    if (in) {
        if(aboboras) {
            int al;
        }
    } else {
        int ah;
    }
}else {
int c;
}

'''

frase = '''
s;

int s = a + b;

int s;

int sum(int a, int b) {
    int s = a + b;
    return s;
}

'''

frase2 = '''

void list_sum(int array a) {
    int inc = 0;
    int counter = 0;
    while (inc < 10) {
        inc = inc + 1;
    }
    print(counter);
}

'''

frase3 = '''

void list_sum2(int array a) {
    int inc;
    int counter = 0;
    for (inc = 0; inc < 10; inc++) {
        counter = counter + a[inc];
        for (inc = 0; inc < 10; inc++) {
            while (inc < 10) {
       while (inc < 10) {
        inc = inc + 1;
    }
    }
        counter = counter + a[inc];
    }
    }
    print(counter);
}

'''

frase4 = '''

void last(int list a, int b) {
    int list result;
    result = cons(b, a);
    print('nice!');
}

'''

frase5 = '''

string word(string a, string b) {
    boolean in = FALSE;
    int inc = 0;
    int inc = 1;
    string value;
    if ( a * (a + b) ) {
        if (a == b) {

        }

        if (in) {
             if (in) {
            }
        }
        
        in = TRUE;
        value = a;
    } else {
        value = "diff";
    }
    return value;
}

'''


frase6 = '''


void teste_somar_elementos() {
    int array lista = [1, c, 3, 4, 5];
    somar_elementos(lista);
}

void teste_adicionar_elemento() {
    lista_original = [1, 2, 3];
    int elemento = 4;
    adicionar_elemento(lista_original, elemento);
}

'''

frase7 = '''

void executar_acao(int opcao) {
    switch (opcao) {
        case 1:
            for (int i = 0; i < 10; i++) {
                for (int i = 0; i < 10; i++) {
                }
            }
            print("Executando acao 1");
            break;
        case 2:
            for (int i = 0; i < 10; i++) {
            }
            print("Executando acao 2");
            break;
        case 3:
            print("Executando acao 3");
            break;
        default:
            print("opcao invalida");
            break;
    }
}
'''

frase8 = '''

void teste_somar_elementos() {
    int set = { 1, 2, 3, 4, 5 } ;
    somar_elementos(lista);
}

void teste_adicionar_elemento() {
    set_original = { 1, 2, 3 };
    int elemento = 4;
    adicionar_elemento(original, elemento);
}

'''





#Lançamento do desafio de especificar uma LPI, contendo:
#		Int, Set, Array, Tuplo, String, Lista
#		Decls + Insts
#		Insts : Atrib, Leitura, Escrita, 
 #                    	          Seleção (SE, CASO), 
  #                   	          Repetição (ENQ-FAZER, REPETIR-ATE, PARA-interv-FAZER
	#	Opers: +-*/%^    ;  []  ; . (seleção de 1campo) ; cons, snoc, in, head/tail ->>>
     #       	Funções com retorno e parametros 

print("INICIO")
p = Lark(grammar)  # cria um objeto parser
print("Passou")
tree = p.parse(frase0)  # retorna uma tree
print(tree)
print(tree.pretty())
pydot__tree_to_png(tree, 'lark.png')  # corrigido o nome da função









print("interpreter")
dic,dicCenas, ifs, estruturasControlo,  array = MyInterpreter().visit(tree)


 
print("Estruturas de controlo:", estruturasControlo)
print(dicCenas)
print("ifs",ifs)
#exercicio 1
listaRedeclaracoes = []
listaNaoRedeclaracoes = []
listaNaoInicializadas = []
listaNaoMencionadas = []

for key, value in dic.items():
    tipo = value[0]
    boolRedecl = value[2]
    bool2 = value[3]
    bool3 = value[4]
    bool4 = value[5]
    if (boolRedecl):
        listaRedeclaracoes.append(key)
    if (bool2):
        listaNaoRedeclaracoes.append(key)
    if (bool3):
        listaNaoInicializadas.append(key)
    if tipo != None and not (bool4):
        listaNaoMencionadas.append(key)

print("Variaveis redeclaradas: ", listaRedeclaracoes)
print("Variaveis não declaradas: ", listaNaoRedeclaracoes)
print("Variaveis usadas mas não inicializadas(sem valor): ", listaNaoInicializadas)
print("Variaveis nao mencionadas mas declaradas: ", listaNaoMencionadas)

#exericio 2
dicTipos = {}
for key, value in dic.items():
    print(f"{key} : {value}")
    tipo = value[0]
    if tipo not in dicTipos:
        dicTipos[tipo] = [key]
    else:
        dicTipos[tipo].append(key)

print(f"Dicionario de tipos: {dicTipos}")


#exercicio 3



#exercicio 4


#HTML



# Assuming the data is as follows:


struturasControlo = dicCenas

section4 = estruturasControlo
section5 = ifs

# Create the HTML file
with open('output.html', 'w') as f:
    f.write("<html><body>")

    # Section 1
    f.write("<h1>Section 1</h1>")
    for lista, name in zip([listaRedeclaracoes, listaNaoRedeclaracoes, listaNaoInicializadas, listaNaoMencionadas],
                        ['listaRedeclaracoes', 'listaNaoRedeclaracoes', 'listaNaoInicializadas', 'listaNaoMencionadas']):
        f.write(f"<h2>{name}</h2>")
        f.write("<table>")
        for item in lista:
            f.write(f"<tr><td>{item}</td></tr>")
        f.write("</table>")

    # Section 2
    f.write("<h1>Section 2</h1>")
    f.write("<table>")
    for key, values in dicTipos.items():
        f.write(f"<tr><th>{key}</th>")
        for value in values:
            f.write(f"<td>{value}</td>")
        f.write("</tr>")
    f.write("</table>")

    # Section 3
    f.write("<h1>Section 3</h1>")
    f.write("<table>")
    for key, value in struturasControlo.items():
        f.write(f"<tr><td>{key}</td><td>{value}</td></tr>")
    f.write("</table>")

    # Section 4
    f.write("<h1>Section 4</h1>")
    f.write(f"<p>{section4}</p>")

    # Section 5
    f.write("<h1>Section 5</h1>")
    f.write(f"<p>{section5}</p>")

    f.write("</body></html>")


print("Array->",array)