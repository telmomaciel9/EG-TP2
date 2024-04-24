from lark import Lark
from lark.tree import pydot__tree_to_png

grammar = '''
start: (declaration | statement)*

declaration: type comp_type? IDENTIFIER "(" params? ")" "{" body* "}"

params: decl ("," decl)*
comp_type: ("array" | "list" | "set")
decl: type comp_type? IDENTIFIER | IDENTIFIER


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

args: (expr ("," expr)*)?

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

frase8 = ''''



'''


#Falta fazer
#Set
#Seleção????


#Lançamento do desafio de especificar uma LPI, contendo:
#		Int, Set, Array, Tuplo, String, Lista
#		Decls + Insts
#		Insts : Atrib, Leitura, Escrita, 
 #                    	          Seleção (SE, CASO), 
  #                   	          Repetição (ENQ-FAZER, REPETIR-ATE, PARA-interv-FAZER
	#	Opers: +-*/%^    ;  []  ; . (seleção de 1campo) ; cons, snoc, in, head/tail ->>>
     #       	Funções com retorno e parametros 

p = Lark(grammar)  # cria um objeto parser
tree = p.parse(frase7)  # retorna uma tree
print(tree)
print(tree.pretty())
pydot__tree_to_png(tree, 'lark.png')  # corrigido o nome da função
