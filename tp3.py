from lark import Lark,Tree,Token
from lark.tree import pydot__tree_to_png
from lark.visitors import Interpreter
import html
import re
import graphviz

def remove_duplicate_lines(string): 
    lines = string.strip().split('\n')
    seen = set()
    unique_lines = []

    # Itera sobre as linhas de trás para frente
    for line in reversed(lines):
        stripped_line = line.strip()  # Remove espaços em branco das extremidades
        if stripped_line and stripped_line not in seen:  # Verifica se a linha não é vazia e não é duplicada
            seen.add(stripped_line)
            unique_lines.append(line)  # Adiciona a linha original (preserva os espaços em branco internos)

    # Reverte as linhas para manter a ordem original
    unique_lines.reverse()
    return '\n'.join(unique_lines)

def add_shapes(string):
    shapes = set()
    pattern = r'"(if\s(?:[^"]|\\"|\\\\)*?)"'  # Expressão regular para encontrar "if" dentro de aspas
    matches = re.findall(pattern, string)
    for match in matches:
        shapes.add(f'\n"{match}" [shape=diamond];')
    return ''.join(shapes)

def conect_express(graph_str):
    # Separar a string por linhas
    linhas = graph_str.strip().split('\n')

    # Função para verificar se a linha contém uma ligação
    def tem_ligacao(linha):
        return '->' in linha
    
    # Função para extrair os elementos da ligação
    def extrair_elementos(linha):
        return [parte.strip().strip('"') for parte in linha.split('->')]

    # Inicializar a lista de conexões
    conexoes = []

    # Remover espaços em branco das extremidades de cada linha e armazenar no array
    array_de_linhas = [linha.strip() for linha in linhas]

    # Processar cada linha
    i = 0
    while i < len(linhas):
        # Ignorar linhas vazias
        if not array_de_linhas[i]:
            i += 1
            continue
        
        if tem_ligacao(array_de_linhas[i]):
            elementos = extrair_elementos(array_de_linhas[i])
            if i + 1 < len(linhas) and tem_ligacao(linhas[i + 1].strip()):
                # Se a próxima linha também tiver uma ligação, apenas prosseguir
                conexoes.append(array_de_linhas[i])
                i += 1
                continue
            elif i + 1 < len(linhas):
                # Se a próxima linha não tiver uma ligação, conectar o segundo elemento à próxima linha
                prox_linha = linhas[i + 1].strip().strip('"') 
                conexoes.append(array_de_linhas[i])
                conexoes.append(f'"{elementos[1]}" -> "{prox_linha}"') 
                i += 1
            else:
                i += 1
        else:
            # Verificar se a próxima linha é um único elemento
            if i + 1 < len(linhas) and not tem_ligacao(linhas[i + 1].strip()):
                prox_linha = linhas[i + 1].strip().strip('"')
                conexoes.append(f'{array_de_linhas[i]} -> "{prox_linha}"')
                i += 1
            elif i + 1 < len(linhas):
                # Conectar à primeira parte do próximo elemento com ligação
                prox_elemento = extrair_elementos(linhas[i + 1].strip())[0]
                conexoes.append(f'{array_de_linhas[i]} -> "{prox_elemento}"')
                i += 1
            else:
                i += 1
    
    return '\n'.join(conexoes)


def conectar_fim(string):
    linhas = string.strip().split('\n')
    apontados = set()
    apontadores = set()
    novas_linhas = []

    # Iterar pelas linhas para coletar todos os apontadores e apontados
    for linha in linhas:
        if '->' in linha:
            esquerda, direita = [parte.strip().strip('"') for parte in linha.split('->')]
            apontadores.add(esquerda)
            apontados.add(direita)
            novas_linhas.append(f'"{esquerda}" -> "{direita}"')

    # Encontrar elementos apontados que não são apontadores
    finais = apontados - apontadores

    # Adicionar as conexões para "fim" para os elementos que não apontam para nada
    for final in finais:
        novas_linhas.append(f'"{final}" -> "fim"')

    return '\n'.join(novas_linhas)

def processar_grafo(stringGrafoFinal):
    stringGrafoFinal = f'"inicio"\n{stringGrafoFinal}\n'
    stringGrafoFinal = remove_duplicate_lines(stringGrafoFinal)
    stringGrafoFinal = conect_express(stringGrafoFinal)
    stringGrafoFinal = conectar_fim(stringGrafoFinal)
    stringGrafoFinal += add_shapes(stringGrafoFinal)
    return stringGrafoFinal

def extract_values_to_string(data):
    if isinstance(data, list):
        result = []
        for item in data:
            result.append(extract_values_to_string(item))
        return ' '.join(result)
    else:
        return str(data)
    
def extract_before_second_if(expr):
    matches = re.findall(r'"if[^"]*"', expr)
    if len(matches) >= 2:

        target = matches[1]  # The string with "if" that appears second

        parts = expr.split(target)
        # print("PARTS", parts)
        if len(parts) >= 2:
            prev_matches = re.findall(r'"([^"]*)"', parts[1])
            # print("PREV", prev_matches)
            if prev_matches:
                return prev_matches[-1]
    return None

def extract_first(expr):
    match = re.search(r'"([^"]*)"', expr)
    if match:
        return match.group(1)
    return None

def extract_last(expr):
    matches = re.findall(r'"([^"]*)"', expr)
    if matches:
        return matches[-1]
    return None

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
        self.ativoIF = []
        self.ativoWHILE = []
        self.assign = False
        self.declare = False
        self.ifAuxArray = []
        self.elseBool = False
        self.funcion = None
        self.isfuncion = False

    def start(self, tree):
        #print("Interpreter started")
        self.visit_children(tree)
        #print("Start", self.arrayString)
        arrayDasStrings=self.arrayString
        stringGrafoFinal = ""
        if arrayDasStrings:
            for i in range(len(arrayDasStrings)):
                if re.search(r'"if .*" -> ""', arrayDasStrings[i]):
                    arrayDasStrings[i] = re.sub(r'"if .*" -> ""', '\n', arrayDasStrings[i])


            stringGrafoFinal = "\n".join(arrayDasStrings)

        #print("GRAFO FINAL\n", stringGrafoFinal)
        grafo_processado = processar_grafo(stringGrafoFinal)        

        return self.dicVar, self.dicInstrucoes, self.ifsMerge, self.estruturasControlo, grafo_processado

    def declaration(self, tree): #Define uma função, é preciso guardar a scope
        for elemento in tree.children:
            if (isinstance(elemento, Token) and elemento.type == 'IDENTIFIER'):
                self.scope = elemento 
        
        self.isfuncion = True
        self.funcion = ""
        
        self.visit_children(tree)

        #self.arrayString.append(self.funcion)
        self.isfuncion = False
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

        if self.assign:
            expressao = f'{tipo} {nomeVAR}'
        else:
            expressao = f'"{tipo} {nomeVAR}"'
        if not self.ativoIF and not self.ativoWHILE and not self.assign: 
            self.arrayString.append(expressao)
            
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


        if not self.ativoIF and not self.ativoWHILE: 
            self.arrayString.append(f'"{nomeVAR}"')

        return nomeVAR
    
    def statement(self, tree):
        return self.visit_children(tree)

    def body(self, tree):
        return self.visit_children(tree)

    def if_statement(self, tree):

        self.ativoIF.append( True)


        numeroFilhos = len(tree.children)

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

        stringG = ""
        conteudo = ""

        if exp:
            print("EXP", exp)   
            if len(exp) > 1:
                stringG += f'"if {extract_values_to_string(n)}" -> {extract_values_to_string(exp[0])}\n'
                for i in range(0, len(exp) - 1):                    
                    current_value = extract_values_to_string(exp[i])
                    next_value = extract_values_to_string(exp[i + 1])
                    
                    if extract_first(current_value): 
                        #stringG += f'{current_value}\n'
                        if extract_first(next_value):
                            stringG += f'"{extract_last(current_value)}" -> "{extract_first(next_value)}"\n'
                        else:
                            stringG += f'"{extract_last(current_value)}" -> "{next_value}"\n'

                    else: 
                        if extract_first(next_value):
                            stringG += f'"{current_value}" -> "{extract_first(next_value)}"\n'
                        else:
                            stringG += f'"{current_value}" -> "{next_value}"\n'
                    if "if" in current_value and self.elseBool:
                        then = extract_before_second_if(current_value)
                        ult = extract_last(current_value)
                        stringG += f'"{then}" -> "{next_value}"\n'
                        stringG += f'"{ult}" -> "{next_value}"\n'
                    elif "if" in current_value and not self.elseBool:
                        pIf = extract_first(current_value)
                        stringG += f'"{pIf}" -> "{next_value}"\n'
            else:
                print("OIII")
                match = re.search(r'"([^"]*)"', exp[0][0])
                if match:
                    conteudo = match.group(1)
                else:
                    conteudo = exp[0][0]

        if extract_values_to_string(conteudo) != '':
            stringG += f'"if {extract_values_to_string(n)}" -> "{extract_values_to_string(conteudo)}"\n'
        else:
            print("AQUIII", f'"if {extract_values_to_string(n)}"\n')
            #stringG += f'"if {extract_values_to_string(n)}"\n'

        self.elseBool = False
        if numeroFilhos == 3:
            self.elseBool = True
            expElse = self.visit(tree.children[2]) or ""
            conteudoElse = ""
            if expElse:
                match = re.search(r'"([^"]*)"', expElse[0][0])
                if match:
                    conteudoElse = match.group(1)
                else:
                    conteudoElse = expElse[0][0]

            
            stringElse = f'"if {extract_values_to_string(n)}" -> "{extract_values_to_string(conteudoElse)}"\n'
            
            if len(expElse) > 1:
                for i in range(len(expElse)-2):
                    stringElse += f'{extract_values_to_string(expElse[i])} -> {extract_values_to_string(expElse[i+1])}\n'
                if extract_first(extract_values_to_string(expElse[len(expElse)-1])):
                    stringElse += f'{extract_values_to_string(expElse[len(expElse)-2])} -> "{extract_first(extract_values_to_string(expElse[len(expElse)-1]))}"\n'
                else:
                    stringElse += f'"{extract_values_to_string(expElse[len(expElse)-2])}" -> "{extract_values_to_string(expElse[len(expElse)-1])}"\n'


        stringG += stringElse
        self.ifAuxArray.append(stringG)
        self.ativoIF.pop()
        if not self.ativoIF:
            self.arrayString += self.ifAuxArray[::-1]
        return stringG


    def while_statement(self, tree):
        self.boolIF = False
        self.ativoWHILE.append(True)

        if self.estrutura:
            self.estruturasControlo += 1
        
        self.dicInstrucoes['ciclicas'] += 1
    
        self.estrutura.append(True)
        n = self.visit(tree.children[0]) or ""
        exp = self.visit(tree.children[1]) or ""
        self.estrutura.pop()
        string = ""
        if exp:
            string += f'"if {extract_values_to_string(n)}" -> "{extract_values_to_string(exp[0])}"\n'
            if len(exp) > 1:
                for i in range(0, len(exp) - 1):

                    current_value = extract_values_to_string(exp[i])
                    next_value = extract_values_to_string(exp[i + 1])

                    if extract_first(current_value): 
                        string += f'{current_value}\n'
                        if extract_first(next_value):
                            string += f'"{extract_last(current_value)}" -> "{extract_first(next_value)}"\n'
                        else:
                            string += f'"{extract_last(current_value)}" -> "{next_value}"\n'

                    else: 
                        if extract_first(next_value):
                            string += f'"{current_value}" -> "{extract_first(next_value)}"\n'
                        else:
                            string += f'"{current_value}" -> "{next_value}"\n'

                string += f'"{next_value}" -> "if {extract_values_to_string(n)}" \n'
            else:
                string += f'"{extract_values_to_string(exp[0])}" -> "if {extract_values_to_string(n)}" \n'
        else:
            string += f'"if {extract_values_to_string(n)}"\n'

        self.arrayString.append(string)
        self.ativoWHILE.pop()
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
        self.assign = True

        self.dicInstrucoes['atribuicoes'] += 1
        self.declAuxValue = True
        exp = self.visit_children(tree) or ""
        self.declAuxValue = False

        string = ""

        if not self.ativoIF and not self.ativoWHILE: 
            string = f'"{extract_values_to_string(exp)}"'
            self.arrayString.append(string)
        else:
            string = f'{extract_values_to_string(exp)}'

        self.assign = False
        return string

    def print_statement(self, tree):
        self.boolIF = False

        exp = self.visit_children(tree) or ""
        string = f'"print({extract_values_to_string(exp)})"'
        self.arrayString.append(string)
        return string

    def declare_statement(self, tree):
        self.boolIF = False
        self.declare = True
        exp = self.visit_children(tree) or ""
        
        self.declare = False
        return extract_values_to_string(exp)
    
    def call_function(self, tree):
        self.boolIF = False

        exp = self.visit_children(tree) or ""
        if self.assign:
            string = f'{extract_values_to_string(exp)}'
        else:
            string = f'"{extract_values_to_string(exp)}"'
            self.arrayString.append(string)
        return string

    def return_statement(self, tree):

        self.boolIF = False

        exp = self.visit_children(tree) or ""
        string = f'"return {extract_values_to_string(exp)}"'
        self.arrayString.append(string)
        return string

    def switch_case_statement(self, tree):
        self.boolIF = False

        if self.estrutura:
            self.estruturasControlo += 1
        
        self.dicInstrucoes['condicionais'] += 1
        self.visit_children(tree)

        self.estrutura.append(True)
        exp = self.visit(tree.children[1]) or ""  
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
            return str(tree.children[0]) or ""

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
assign_statement: decl IGUAL (expr | call_function)
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

    
IGUAL: "="  
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

frase1 = '''
if ( a * (a + b) ) {     
    int a; 
    int b;
    if (in) {
        int debug;
        if(aboboras) {
            int al;
            int al2;
        }
    } else {
        if(coae){
            c = 2;
        }
        else{
            int h;
            int i;
        }
    }
}



'''

frase2= '''
a;
b;
if(aboboras) {
    al;
    al2;
    if(eu){
        al3;
        if(eu2){
            al4;
        }
        else{
            al5;
        }
        boneco;
    }
    alssss;
}
else{
    eueueue;
}
lapala;
'''

frase3 = '''
int c;
int d;
while (inc2 < 10) {
    inc = inc + 1;
    inc2 = inc + 1;
}
int a;
int b;
'''

frase4 = '''

void sum(int array a) {
    int inc = 0;
    int counter = 0;
    int c;
    while (inc < 10) {
        inc = inc + 1;
        counter = counter + 2;
    }
    print(counter);
}

'''

frase5 = '''

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

frase6 = '''

void last(int list a, int b) {
    int list result;
    result = cons(b, a);
    print('nice!');
}

'''

frase7 = '''

string word(string a, string b) {
    boolean in = FALSE;
    int inc = 0;
    int inc = 1;
    string value;
    if ( a * (a + b) ) {
        ola;
        if (a == b) {
            skj;
        }

        if (in) {
            if (in2) {
                sss;
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


frase8 = '''


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

frase9 = '''

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

frase10 = '''

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
tree = p.parse(frase1)  # retorna uma tree
print(tree)
print(tree.pretty())
pydot__tree_to_png(tree, 'lark.png')  # corrigido o nome da função









#print("interpreter")
dic,dicCenas, ifs, estruturasControlo,  array = MyInterpreter().visit(tree)


 
#print("Estruturas de controlo:", estruturasControlo)
#print(dicCenas)
#print("ifs",ifs)
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

#print("Variaveis redeclaradas: ", listaRedeclaracoes)
#print("Variaveis não declaradas: ", listaNaoRedeclaracoes)
#print("Variaveis usadas mas não inicializadas(sem valor): ", listaNaoInicializadas)
#print("Variaveis nao mencionadas mas declaradas: ", listaNaoMencionadas)

#exericio 2
dicTipos = {}
for key, value in dic.items():
    #print(f"{key} : {value}")
    tipo = value[0]
    if tipo not in dicTipos:
        dicTipos[tipo] = [key]
    else:
        dicTipos[tipo].append(key)

#print(f"Dicionario de tipos: {dicTipos}")


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


print("digraph G{\n",array, "\n}")

def gerar_html_com_imagem(grafo_dot, nome_arquivo_html):
    dot = graphviz.Digraph()
    for line in grafo_dot.strip().split('\n'):
        if '->' in line:
            source, target = re.findall(r'"(.*?)"', line)
            dot.edge(source, target)
        else:
            match = re.match(r'"(.*?)"\s*\[shape=(.*?)\];', line)
            if match:
                node, shape = match.groups()
                dot.node(node, shape=shape)
            else:
                node = re.findall(r'"(.*?)"', line)
                if node:
                    dot.node(node[0])

    nome_arquivo_imagem = 'grafo'
    dot.render(filename=nome_arquivo_imagem, format='png', cleanup=True)
    
    conteudo_html = f'''
    <html>
    <head><title>Grafo</title></head>
    <body>
    <h1>Grafo Gerado</h1>
    <img src="{nome_arquivo_imagem}.png">
    </body>
    </html>
    '''
    
    with open(nome_arquivo_html, 'w') as f:
        f.write(conteudo_html)

# Gerar HTML com a imagem do grafo
nome_arquivo_html = 'grafo.html'
gerar_html_com_imagem(array, nome_arquivo_html)
print(f"Arquivo HTML gerado: {nome_arquivo_html}")