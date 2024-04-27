from lark import Lark,Tree,Token
from lark.tree import pydot__tree_to_png
from lark.visitors import Interpreter

def comparatorIdentifier(dic):
    tipo = dic[0]
    temValue = dic[1]
    boolRedecl = dic[2]
    bool2 = dic[3]
    bool3 = dic[4]
    bool4 = dic[5]
    if(tipo != None): # Tem tipo
        dic = (tipo,temValue,boolRedecl,bool2,bool3,True)

    if(not(temValue)):
        dic = (tipo,temValue,boolRedecl,bool2,True,bool4)

def comparator(dic,tipoBOOL,tipoNOVO=None):
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

    else: #Está a ser usada!
        if(tipo != None): # Tem tipo
            dic = (tipo,temValue,boolRedecl,bool2,bool3,True)

        if(not(temValue)):
            dic = (tipo,temValue,boolRedecl,bool2,True,bool4)

class MyInterpreter(Interpreter):
    def __init__(self):
        self.dicVar = {} #key(nameVariavel-Scope|| tipo || temValue || Bool de nª de redlecarações, bool2,bool3, bool4(true=usada) )
        self.scope = "Global"
        self.declAuxValue = False #saber se vem do assign_statement
    
    def start(self,tree):
        print("Interpreter started")
        self.visit_children(tree)
        return self.dicVar

    def declaration(self,tree): #Define uma função, é preciso guardar a scope
        for elemento in tree.children:
            if (isinstance(elemento, Token) and elemento.data == 'IDENTIFIER'):
                self.scope = elemento
                print(f"Scope: {self.scope}")
        self.visit_children(tree)
        self.scope = "Global"

    def paramsfunc(self,tree):
        self.visit_children(tree)

    def declfunc(self,tree):
        tipo = tree.children[0]
        
        nomeVAR = tree.children[2]
        tipo = f"{tipo}-{tree.children[1]}"
        

        if f"{nomeVAR}-{self.scope}" in self.dicVar:
            keyObject = self.dicVar[f"{nomeVAR}-{self.scope}"]
            comparator(keyObject,True,tipo)    
        else:
            self.dicVar[f"{nomeVAR}-{self.scope}"] = (tipo,True,False,False,False,False)

    def decl(self,tree):
        nomeVAR = None
        tipo = tree.children[0]
        print("tipo",tree)
        
        if len(tree.children) == 3:
            nomeVAR = tree.children[2]
            tipo = f"{tipo}-{tree.children[1]}"
        else:
            nomeVAR = tree.children[1]
        print("nomevar",nomeVAR)

        if f"{nomeVAR}-{self.scope}" in self.dicVar:
            keyObject = self.dicVar[f"{nomeVAR}-{self.scope}"]
            comparator(keyObject,True,tipo)    
        else:
            if(self.declAuxValue):
                self.dicVar[f"{nomeVAR}-{self.scope}"] = (tipo,True,False,False,False,False)
            else:
                self.dicVar[f"{nomeVAR}-{self.scope}"] = (tipo,False,False,False,False,False)
        

        
        
    def declsemtipo(self,tree):
        nomeVAR = tree.children[0]

        if f"{nomeVAR}-{self.scope}" in self.dicVar:
            keyObject = self.dicVar[f"{nomeVAR}-{self.scope}"]
            comparator(keyObject,False)
        
        elif(self.declAuxValue): # Veio do assign_statement, ou seja, tem valor mas nao tem tipo
            self.dicVar[f"{nomeVAR}-{self.scope}"] = (None,True,False,True,False,False)
        else:                           
            self.dicVar[f"{nomeVAR}-{self.scope}"] = (None,False,False,True,True,False)

    def statement(self,tree):
        self.visit_children(tree)

    def body(self,tree):
        self.visit_children(tree)

    def statement(self,tree):
        self.visit_children(tree)
    
    def if_statement(self,tree):
        self.visit_children(tree)

    def while_statement(self,tree):
        self.visit_children(tree)

    def for_statement(self,tree):
        self.visit_children(tree)

    def assign_statement(self,tree):
        self.declAuxValue = True
        self.visit_children(tree)
        self.declAuxValue = False

    def print_statement(self,tree):
        self.visit_children(tree)

    def declare_statement(self,tree):
        self.visit_children(tree)

    def call_function(self,tree):
        self.scope = tree.children[0]
        self.visit_children(tree)
        self.scope = "Global"

    def return_statement(self,tree):
        self.visit_children(tree)

    def switch_case_statement(self,tree):
        self.visit_children(tree)

    def switch_case_branch(self,tree):
        self.visit_children(tree)

    def args(self,tree):
        self.visit_children(tree)

    def expr(self,tree): 
        self.visit_children(tree)

    def value(self,tree):
        if(isinstance(tree.children[0], Token)) and tree.children[0].type == 'IDENTIFIER':
            value = tree.children[0]
            if f"{value}-{self.scope}" in self.dicVar:
                dic = self.dicVar[f"{value}-{self.scope}"]
                comparatorIdentifier(dic)
            else:
                self.dicVar[f"{value}-{self.scope}"] = (None,False,False,True,True,False)
        else:   
            self.visit_children(tree)

    def array_access(self,tree):
        self.visit_children(tree)

    def set_access(self,tree):
        self.visit_children(tree)

    def binary_op(self,tree):
        pass

    def unary_op(self,tree):
        pass

    def binary_op_priority(self,tree): 
        pass

    def int(self,tree):
        return int(tree.children[0])
    
    def string(self,tree):
        return str(tree.children[0])    
    
    def tuple(self,tree):
        for elemento in tree.children:
            if (isinstance(elemento, Tree) and elemento.type == 'IDENTIFIER'):
                value = tree.children[0]
                if f"{value}-{self.scope}" in self.dicVar:
                    dic = self.dicVar[f"{value}-{self.scope}"]
                    comparatorIdentifier(dic)
                else:
                    self.dicVar[f"{value}-{self.scope}"] = (None,False,False,True,True,False)

    def bool(self,tree):
        return bool(tree.children[0])
    
    def array(self,tree):
        self.visit_children(tree)
    
    def set(self,tree):
        self.visit_children(tree)

    def comp_type(self,tree):
        return str(tree.children[0])

    def IDENTIFIER(self,tree):
        return str(tree.children[0])

    def type(self,tree):
        print("TreeType",tree.children[0])
        return str(tree.children[0])

grammar = '''
start: (declaration | statement)*

declaration: type comp_type? IDENTIFIER "(" paramsfunc? ")" "{" body* "}"

paramsfunc: declfunc ("," declfunc)*

comp_type: ("array" | "list" | "set")

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

if_statement: "if" "(" expr ")" "{" body* "}" ("else" "{" body* "}")?
while_statement: "while" "(" expr ")" "{" body* "}"
for_statement: "for" "(" assign_statement ";" expr ";" decl unary_op ")" "{" body* "}"
assign_statement: decl "=" (expr | call_function)
print_statement: "print" "(" expr ")"
declare_statement: decl
call_function: IDENTIFIER "(" args ")"
return_statement: "return" expr

switch_case_statement: "switch" "(" expr ")" "{" switch_case_branch* "}"

switch_case_branch: "case" value ":" body* "break" ";"
                  | "default" ":" body* "break" ";"

args: (expr  ("," expr)*)?

expr: value
    | "(" expr ")"
    | array_access
    | expr binary_op expr
    | unary_op expr

value: IDENTIFIER | tuple | bool | array | set | INTEGER | STRING

binary_op: "==" | "!=" | "<" | ">" | "<=" | ">=" | "+" | "-" | "or" | binary_op_priority
binary_op_priority:"*" | "/" | "%" | "^" | "and"
unary_op: "++" | "--"

array_access: IDENTIFIER "[" expr "]"
set_access: IDENTIFIER "{" expr "}"

type: "int"
    | "string"
    | "bool"
    | "boolean"
    | "tuple"
    | "void"

int: INTEGER 
string: STRING
tuple: "(" (STRING | INTEGER | IDENTIFIER) ("," (STRING | INTEGER | IDENTIFIER))* ")"
bool: "true" | "false"
array: "[" value ("," value)* "]"
set: "{" value ("," value)* "}"


STRING: /"[^"]*"|'[^']*'/
IDENTIFIER: /[a-zA-Z_]\w*/
INTEGER: /\d+/

%import common.WS
%ignore WS

'''

frase0 = '''

int s = a + b;

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
    boolean in = false;
    string value;
    if ( a * (a + b) ) {
        in = true;
        value = a;
    } else {
        value = "diff";
    }
    return value;
}

'''


frase6 = '''


void teste_somar_elementos() {
    int array = [1, 2, 3, 4, 5];
    somar_elementos(lista);
}

void teste_adicionar_elemento() {
    lista_original = [1, 2, 3];
    int elemento = 4;
    adicionar_elemento(original, elemento);
}

'''

frase7 = '''

void executar_acao(opcao) {
    switch (opcao) {
        case 1:
            print("Executando acao 1");
            break;
        case 2:
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
dic = MyInterpreter().visit(tree)

#exercicio 1
listaRedeclaracoes = []
listaNaoRedeclaracoes = []
listaNaoUsadas = []
listaNaoMencionadas = []

for key, value in dic.items():
    tipo = value[0]
    boolRedecl = value[2]
    bool2 = value[3]
    bool3 = value[4]
    bool4 = value[5]
    if(boolRedecl):
        listaRedeclaracoes.append(key)
    if(bool2):
        listaNaoRedeclaracoes.append(key)
    if(bool3):
        listaNaoUsadas.append(key)
    if not(bool4):

        listaNaoMencionadas.append(key)

print("Variaveis redeclaradas: ", listaRedeclaracoes)
print("Variaveis nao redeclaradas: ", listaNaoRedeclaracoes)
print("Variaveis nao usadas: ", listaNaoUsadas)
print("Variaveis nao mencionadas: ", listaNaoMencionadas)

#exericio 2
dicTipos = {}
for key, value in dic.items():
    print(f"{key} : {value}")
    tipo = value[0]
    dic[tipo] = key

print("Dicionario de tipos: {dicTipos}")


#exercicio 3



#exercicio 4


#exercicio 5