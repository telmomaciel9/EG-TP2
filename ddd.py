from lark import Lark,Discard,Tree
from lark.tree import pydot__tree_to_png
from lark.visitors import Interpreter
import sys

grammar1 = '''
// Regras Sintaticas
start: (MAIS | MENOS) intervalos
intervalos: intervalo (intervalo)*
intervalo: "[" NUM "," NUM "]"

// Regras Lexicográficas
NUM: /-?\d+/
MAIS:"+"
MENOS:"-"

// Tratamento dos espaços em branco
%import common.WS
%ignore WS
'''

frase = "+ [9,13][14,15][18,25][26,30][35,50]"

p = Lark(grammar1) # cria um objeto parser

tree = p.parse(frase)  # retorna uma tree

print(tree.pretty())

class MyInterpreter(Interpreter):
  def __init__(self):
    self.sinal=1

    self.erroIntervalo = ""
    self.erroIntervalos = ""
    self.elemento1 = 0
    self.elemento0 = 0
    self.entrouIntervalo = -1
    self.erro = 0


  def start(self,elementos):
    if elementos.children[0] == "-":
        self.sinal = -1
    self.visit_children(elementos)
    return (self.erro,f'Erros: {self.erroIntervalo} ||| {self.erroIntervalos}')


  def intervalos(self,intervalos):
    self.visit_children(intervalos)
    return intervalos
  
  def intervalo(self,intervalo):
    elemento0 = int(intervalo.children[0])
    elemento1 = int(intervalo.children[1])
    
    if self.sinal == 1:
        if(elemento0 >= elemento1):
            self.erroIntervalo += f'(+)O intervalo: [{elemento0},{elemento1}] está invalido\n'
            self.erro = 1

        if(self.entrouIntervalo == 1):
            if(self.elemento1 >= elemento0):
                self.erroIntervalos += f'(+) Os intervalos: [{self.elemento0},{self.elemento1};{elemento0},{elemento1}] estão invalidos\n'
                self.erro = 1
    else:
        if(elemento0<=elemento1):
            self.erroIntervalo += f'(-)O intervalo: [{elemento0},{elemento1}] está invalido\n'
            self.erro = 1
        
        if(self.entrouIntervalo == 1):
            if(self.elemento1 <= elemento0):
                self.erroIntervalos += f'(-) Os intervalos: [{self.elemento0},{self.elemento1};{elemento0},{elemento1}] estão invalidos\n'
                self.erro = 1
    
    self.elemento0 = elemento0
    self.elemento1 = elemento1
    self.entrouIntervalo = 1
    return intervalo

  def NUM (self,numero):
    pass

flag,data = MyInterpreter().visit(tree)
print(f"saida :{data}")


################################################################################################################################################
class MyInterpreter2(Interpreter):
  def __init__(self):
      self.sinal=1
      self.amplitude = 0
      self.amplitudeSeq = 0
      self.menor =  sys.maxsize
      self.maior = - sys.maxsize -1

    # [1000,500][100,30]

  def start(self,elementos):
    if elementos.children[0] == "-":
      self.sinal = -1
    self.visit_children(elementos)
    return f'Resultados: {self.amplitude} ||| {abs(self.menor - self.maior)}'

  def intervalos(self,intervalos):
    self.visit_children(intervalos)

    #+ [1,10][11,15][18,25][26,30][35,50] 
    #self.menor =  sys.maxsize
    #self.maior = - sys.maxsize -1
    return intervalos
  
  def intervalo(self,intervalo):
    print("intervalo",intervalo)
    num0 = int(intervalo.children[0])
    num1 = int(intervalo.children[1])
    m = abs(num0-num1)
    if m > self.amplitude:
        self.amplitude=m

    if self.sinal == 1:  
        if num0 < self.menor:
            self.menor = num0

        if num1 > self.maior:
            self.maior = num1
    
    else:  
        if num0 > self.maior:
            self.maior = num0

        if num1 < self.menor:
            self.menor = num1

    return intervalo

  def NUM (self,numero):
    pass

if flag==0 :
    travessiaSegunda = MyInterpreter2().visit(tree)
    print(f"2 travessia :{travessiaSegunda}")


    # def turmas(self,turmas):
    #     self.idT = turmas.children[0]
    #     self.visit(turmas.children[1])
    #     return turmas

    # def alunos(self,alunos):
    #     self.visit_children(alunos)
    #     return alunos

    # def aluno(self,aluno):
    #     nomeAtual = aluno.children[0]
    #     self.nAlunos += 1
    #     self.lastNome = nomeAtual
    #     soma = 0
    #     total = 0
    #     for elemento in aluno.children:
    #         if (isinstance(elemento, Tree) and elemento.data == 'nota'):
    #             total += 1
    #             soma += self.visit(elemento)

    #     self.media[f"{nomeAtual}-{self.idT}"] = soma/total
    #     return aluno
