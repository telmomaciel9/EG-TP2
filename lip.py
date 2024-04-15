from lark import Lark,Tree
from lark.tree import pydot__tree_to_png
from lark.visitors import Interpreter


grammar = '''
start: program

program: statement+

statement: assign_statement
         | if_statement
         | while_statement
         | print_statement
         | function_declaration

assign_statement: expression
                | NAME "=" expression -> assign_statementname
                | NAME "=" call_function -> assign_statementname
                | type NAME "=" expression -> assign_statementtype
                | type NAME -> assign_statementtype

if_statement: "if" expression ":" program "else" ":" program

while_statement: "while" expression ":" program

print_statement: "print" "(" expression ")"

function_declaration: type NAME "(" expression ")" ":" program
                    | type NAME "(" assign_statement ")" ":" program
                    | type NAME "(" ")" ":" program

call_function: NAME "(" expression ")"

expression: NUMBER -> expressionnumber
          | STRING -> expressionstring
          | NAME -> expressionname
          | expression "+" expression
          | expression "+=" expression
          | expression "-=" expression
          | expression "-" expression
          | expression ">" expression
          | expression "<" expression
          | expression ">=" expression
          | expression "<=" expression
          | expression "==" expression
          | expression "!=" expression
          | "not" expression
          | expression "or" expression
          | expression_priority

expression_priority: expression "*" expression | expression "/" expression | expression "and" expression | expression_par
expression_par : "(" expression ")"

type: "int"
    | "string"
    | "bool"
    | "set"
    | "list"
    | "array"
    | "tuple"
    | "void"

NUMBER: /-?\d+(\.\d+)?/
STRING: /".*?"/
NAME: /[a-zA-Z_][a-zA-Z0-9_]*/

%import common.WS
%ignore WS

'''

frase = '''
int a = 1 + 1
int b = 2


int soma( int a):
    pass

int c = 3
d = c * (a + b)

'''

p = Lark(grammar)  # cria um objeto parser
tree = p.parse(frase)  # retorna uma tree
print(tree)
print(tree.pretty())

pydot__tree_to_png(tree,'lark_test.png')

#############################################

class MyInterpreter(Interpreter):
    def __init__(self):
        self.dicVar = {} #key(nameVariavel-Scope| Value e tipo e Scope???)
        self.scope = "Global"

    def start(self,tree):
        self.visit_children(tree)

    def program(self,tree):
        for child in tree.children:
            self.visit(child)

    def statement(self,tree):
        self.visit_children(tree)

    def assign_statementname(self,tree):
        nomeVAR = tree.children[0]


    def assign_statementtype(self,tree):
        typeVAR = tree.children[0]
        nomeVAR = tree.children[1]

        if len(tree.children) == 2:
            self.dicVar[f"{nomeVAR}-{self.scope}"] = (None,typeVAR,self.scope)
        else:
            value = self.visit(tree.children[2])
            print("value",value)
            self.dicVar[f"{nomeVAR}-{self.scope}"] = (value,typeVAR,self.scope)

    def assign_statement(self,tree):
        self.visit_children(tree)

    def if_statement(self,tree):    
        self.visit_children(tree)
 

    def while_statement(self,tree):
        self.visit_children(tree)

    def print_statement(self,tree):
        self.visit_children(tree)

    def function_declaration(self,tree): #GUARDAR O NAME E SE QUE O TYPE
        self.scope = tree.children[1]
        self.visit_children(tree)
        self.scope = "Global"


    def call_function(self,tree): #Guardar o NAME 
        self.visit_children(tree)


    def expression(self,tree): #Retornar a expressao toda e meter dentro do value???????
        print("treeEXPRESSION",tree)
        self.visit_children(tree)
            
    def expressionnumber(self,tree):
        return (tree.children[0],'NUMBER')

    def expressionstring(self,tree):
        return (tree.children[0],'STRING')

    def expressionname(self,tree):
        return (tree.children[0],'NAME')

    def expression_priority(self,tree):
        self.visit_children(tree)

    def expression_par(self,tree):
        self.visit_children(tree)

    def type(self,tree):
        pass

    def NUMBER(self,tree):
        pass

    def STRING(self,tree):
        pass

    def NAME(self,tree):
        pass


MyInterpreter().visit(tree)
