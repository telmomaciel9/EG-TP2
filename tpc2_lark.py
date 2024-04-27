from lark import Lark,Tree
from lark.tree import pydot__tree_to_png
from lark.visitors import Interpreter

def comparator(dic,tipoBOOL,declAuxValue,tipoNOVO):
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
            dic = (tipoNOVO,temValue,boolRedecl,bool2,bool3,True)

        if(not(temValue)):
            dic = (tipoNOVO,temValue,boolRedecl,bool2,True,bool4)

class MyInterpreter(Interpreter):
    def __init__(self):
        self.dicVar = {} #key(nameVariavel-Scope|| tipo || temValue || Bool de nª de redlecarações, bool2,bool3, bool4(true=usada) )
        self.scope = "Global"
        self.declAuxValue = False
    
    def start(self,tree):
        self.visit_children(tree)
        return self.dicVar

    def declaration(self,tree): #Define uma função, é preciso guardar a scope
        for elemento in tree.children:
            if (isinstance(elemento, Tree) and elemento.data == 'IDENTIFIER'):
                self.scope = elemento
                print(f"Scope: {self.scope}")
        self.visit_children(tree)
        self.scope = "Global"
        
    def params(self,tree):
        self.declAuxValue = True
        self.visit_children(tree)
        self.declAuxValue = False

    def decl(self,tree):
        nomeVAR = None
        tipo = tree.children[0]
        
        if len(tree.children) == 3:
            nomeVAR = tree.children[2]
            tipo = f"{tipo}-{tree.children[1]}"
        else:
            nomeVAR = tree.children[1]
        

        if f"{nomeVAR}-{self.scope}" in self.dicVar:
            keyObject = self.dicVar[f"{nomeVAR}-{self.scope}"]
            comparator(keyObject,True,self.declAuxValue,tipo)    
        else:
            if(self.declAuxValue):
                self.dicVar[f"{nomeVAR}-{self.scope}"] = (tipo,True,False,False,False,False)
            else:
                self.dicVar[f"{nomeVAR}-{self.scope}"] = (tipo,False,False,False,False,False)
        

        
        
    def declSemTipo(self,tree):
        nomeVAR = tree.children[0]

        if f"{nomeVAR}-{self.scope}" in self.dicVar:
            keyObject = self.dicVar[f"{nomeVAR}-{self.scope}"]
            comparator(keyObject,False,self.declAuxValue)
        
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
        pass

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






    def comp_type(self,tree):
        return str(tree.children[0])

    def IDENTIFIER(self,tree):
        return str(tree.children[0])

    def type(self,tree):
        return str(tree.children[0])

grammar = '''
start: (declaration | statement)*

declaration: type comp_type? IDENTIFIER "(" params? ")" "{" body* "}"

params: decl ("," decl)*
comp_type: ("array" | "list" | "set")
decl: type comp_type? IDENTIFIER 
      | IDENTIFIER 


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

value: IDENTIFIER | attribute | INTEGER | STRING

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

attribute : int | string | tuple | bool | array | set

int: INTEGER 
string: STRING
tuple: "(" (STRING | INTEGER) ("," (STRING | INTEGER))* ")"
bool: "true" | "false"
array: "[" attribute ("," attribute)* "]"
set: "{" attribute ("," attribute)* "}"


STRING: /"[^"]*"|'[^']*'/
IDENTIFIER: /[a-zA-Z_]\w*/
INTEGER: /\d+/

%import common.WS
%ignore WS

'''

frase = '''

int s = a + b;

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

p = Lark(grammar)  # cria um objeto parser
tree = p.parse(frase)  # retorna uma tree
print(tree)
print(tree.pretty())
pydot__tree_to_png(tree, 'lark.png')  # corrigido o nome da função










# MyInterpreter().visit(tree)