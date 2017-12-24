# -*- coding: utf-8 -*-
#Renan Kodama Rodrigues 1602098
#UTFPR-CM DACOM Compiladores

from ply import yacc
from Lexica import Lexica
from graphviz import Digraph


class Tree: 
	def __init__(self, tipo_no, filhos=[], valor=''):
		self.tipo = tipo_no
		self.filhos = filhos
		self.valor = valor

	def __str__(self):
		return self.tipo

class Parser:
	def __init__(self, code):
		lex = Lexica()
		self.tokens = lex.tokens
		self.precedence = (
			('left','SENAO'),
			('left','IGUAL','SIMB_MAIORIGUAL','SIMB_MAIOR','SIMB_MENORIGUAL','SIMB_MENOR'),
			('left', 'ADICAO', 'SUBTRACAO'),
			('left', 'MULTIPLICACAO', 'DIVISAO'),
		)	

		parser = yacc.yacc(debug=False, module=self, optimize=False)
		self.ast = parser.parse(code)

	def p_programa(self, p):
		'programa : lista_declaracoes'
		p[0] = Tree('programa', [p[1]])


	def p_lista_declaracoes(self, p):
		'lista_declaracoes : lista_declaracoes declaracao'
		p[0] = Tree('lista_declaracoes', [p[1],p[2]])

	def p_lista_declaracoes1(self, p):
		'lista_declaracoes : declaracao'
		p[0] = Tree('lista_declaracoes', [p[1]])


	def p_declaracao(self, p):
		'''
			declaracao 	: declaracao_variaveis
						| inicializacao_variaveis
						| declaracao_funcao
		'''
		p[0] = Tree('declaracao', [p[1]])


	def p_declaracao_variaveis(self, p):
		'declaracao_variaveis : tipo DOIS_PONTOS lista_variaveis'
		p[0] = Tree('declaracao_variaveis', [p[1],p[3]])


	def p_inicializacao_variaveis(self, p):
		'inicializacao_variaveis : atribuicao'
		p[0] = Tree('inicializacao_variaveis', [p[1]])


	def p_lista_variaveis(self, p):
		'lista_variaveis : lista_variaveis VIRGULA var'
		p[0] = Tree('lista_variaveis', [p[1],p[3]])

	def p_lista_variaveis1(self, p):
		'lista_variaveis : var'
		p[0] = Tree('lista_variaveis', [p[1]])
	

	def p_var(self,p):
		'var : ID'
		p[0] = Tree('var', [], p[1])

	def p_var1(self,p):
		'var : ID indice'
		p[0] = Tree('var', [p[2]], p[1])


	def p_indice(self,p):
		'indice : indice COLCHETE_ESQ expressao COLCHETE_DIR'
		p[0] = Tree('indice', [p[1],p[3]])

	def p_indice1(self,p):
		'indice : COLCHETE_ESQ expressao COLCHETE_DIR'
		p[0] = Tree('indice', [p[2]])

	
	def p_tipo(self,p):
		'tipo : INTEIRO'
		p[0] = Tree('inteiro')

	def p_tipo1(self,p):
		'tipo : FLUTUANTE'
		p[0] = Tree('flutuante')

	def p_tipo2(self,p):
		'tipo : CIENTIFICO'
		p[0] = Tree('cientifico')

	def p_tipo3(self,p):
		'tipo : STRING'
		p[0] = Tree('string')

	def p_declaracao_funcao(self,p):
		'declaracao_funcao : tipo cabecalho'
		p[0] = Tree('declaracao_funcao', [p[1],p[2]])

	def p_declaracao_funcao1(self,p):
		'declaracao_funcao : cabecalho'		
		p[0] = Tree('declaracao_funcao', [p[1]])
	

	def p_cabecalho(self,p):
		'cabecalho : ID PARENTESES_ESQ lista_parametros PARENTESES_DIR corpo FIM'
		p[0] = Tree('cabecalho', [p[3],p[5]], p[1])


	def p_lista_parametros(self,p):
		'lista_parametros : lista_parametros VIRGULA parametro'
		p[0] = Tree('lista_parametros', [p[1],p[3]])

	def p_lista_parametros1(self,p):
		'''
				lista_parametros 	: parametro
									| vazio
		'''
		p[0] = Tree('lista_parametros', [p[1]])


	def p_parametro(self,p):
		'parametro : tipo DOIS_PONTOS ID'
		p[0] = Tree('parametro',[p[1]],p[3])
		
	def p_parametro1(self,p):
		'parametro : parametro COLCHETE_ESQ COLCHETE_DIR'
		p[0] = Tree('parametro', [p[1]])
	

	def p_corpo(self,p):
		'corpo 	: corpo acao'
		p[0] = Tree('corpo', [p[1],p[2]])

	def p_corpo1(self, p):	
		'corpo : vazio'		
		p[0] = Tree('corpo', [p[1]])


	def p_acao(self,p):
		'''
			acao 	: expressao
					| declaracao_variaveis
					| se
					| repita
					| leia
					| escreva
					| retorna
					| error
		'''
		p[0] = Tree('acao', [p[1]])


	def p_se(self,p):
		'se : SE expressao ENTAO corpo FIM'
		
		p[0] = Tree('se', [p[2],p[4]])
		
	def p_se1(self,p):
		'se : SE expressao ENTAO corpo SENAO corpo FIM'
		p[0] = Tree('se',[p[2],p[4],p[6]])


	def p_repita(self,p):
		'repita : REPITA corpo ATE expressao'
		p[0] = Tree ('repita', [p[2],p[4]])


	def p_atribuicao(self,p):
		'atribuicao : var ATRIBUICAO expressao'
		p[0] = Tree ('atribuicao', [p[1],p[3]])


	def p_leia(self,p):
		'leia : LEIA PARENTESES_ESQ ID PARENTESES_DIR'
		p[0] = Tree('leia', [], p[3])


	def p_escreva(self,p):
		'escreva : ESCREVA PARENTESES_ESQ expressao PARENTESES_DIR'
		p[0] = Tree('escreva', [p[3]])


	def p_retorna(self,p):
		'retorna : RETORNA PARENTESES_ESQ expressao PARENTESES_DIR'
		p[0] = Tree('retorna', [p[3]])


	def p_expressao(self,p):
		'''
			expressao 	: expressao_simples
						| atribuicao 
		''' 
		p[0] = Tree('expressao', [p[1]])

	def p_expressao_simples(self,p):
		'expressao_simples : expressao_aditiva'
		p[0] = Tree('expressao_simples', [p[1]])
	
	def p_expressao_simples1(self,p):
		'expressao_simples : expressao_simples operador_relacional expressao_aditiva'
		p[0] = Tree('expressao_simples', [p[1],p[2],p[3]])


	def p_expressao_aditiva(self,p):
		'expressao_aditiva : expressao_multiplicativa'
		p[0] = Tree('expressao_aditiva', [p[1]])

	def p_expressao_aditiva1(self,p):
		'expressao_aditiva : expressao_aditiva operador_soma expressao_multiplicativa'
		p[0] = Tree('expressao_aditiva', [p[1],p[2],p[3]])


	def p_expressao_multiplicativa(self,p):
		'expressao_multiplicativa : expressao_unaria'											
		p[0] = Tree('expressao_multiplicativa', [p[1]])

	def p_expressao_multiplicativa1(self,p):
		'expressao_multiplicativa : expressao_multiplicativa operador_multiplicacao expressao_unaria'
		p[0] = Tree('expressao_multiplicativa', [p[1],p[2],p[3]])		


	def p_expressao_unaria(self,p):
		'expressao_unaria : fator'
		p[0] = Tree('expressao_unaria', [p[1]])

	def p_expressao_unaria1(self,p):
		'expressao_unaria : operador_soma fator'
		p[0] = Tree('expressao_unaria', [p[1],p[2]])


	def p_operador_relacionar(self,p):
		'''	
			operador_relacional 	: SIMB_MENOR
									| SIMB_MAIOR
									| IGUAL
									| DIFERENTEDE
									| SIMB_MENORIGUAL 
									| SIMB_MAIORIGUAL
									| E_LOGICO
									| NEGACAO
		'''
		p[0] = Tree('operador_relacional', [],p[1])	


	def p_operador_soma(self,p):
		'''
			operador_soma 	: ADICAO
							| SUBTRACAO
		'''
		p[0] = Tree('operador_soma', [],p[1])	


	def p_operador_multiplicacao(self,p):
		'''
			operador_multiplicacao 	: MULTIPLICACAO
									| DIVISAO
		'''
		p[0] = Tree('operador_multiplicacao', [],p[1])	


	def p_fator(self,p):
		'''	
			fator 	: var
					| chamada_funcao
					| numero
		'''
		p[0] = Tree('fator', [p[1]])

	def p_fator1(self,p):
		'fator : PARENTESES_ESQ expressao PARENTESES_DIR'
		p[0] = Tree('fator', [p[2]])


	def p_numero(self,p):
		'''
			numero 	: NUMERO  
					| CIENTIFICO 
		'''		
		p[0] = Tree('numero', [],p[1])	


	def p_chamada_funcao(self,p):
		'chamada_funcao : ID PARENTESES_ESQ lista_argumentos PARENTESES_DIR'
		p[0] = Tree('chamada_funcao', [p[3]],p[1])


	def p_lista_argumentos(self,p):
		'lista_argumentos 	: lista_argumentos VIRGULA expressao'		
		p[0] = Tree('lista_argumentos', [p[1],p[3]])
		
	def p_lista_argumentos1(self,p):
		'''
			lista_argumentos 	: expressao
								| vazio
		'''
		p[0] = Tree('lista_argumentos', [p[1]])

	def p_vazio(self, p):
		'vazio :'

	def p_error(self, p):
		if p:
			print("Erro sintático: '%s', linha %d" % (p.value, p.lineno))
			exit(1)

		else:
			#yacc.restart()
			print('Erro sintático: definições incompletas!')
			exit(1)


def verArvoreTerminal(node,level="-"):
	if node != None:
		print("%s %s %s" %(level, node.tipo, node.valor))
		for son in node.filhos:	
			verArvoreTerminal(son,level+"-")

def verArvoreTexto(node,w,i):
	if node != None:
		if (node.valor != ''):
			value1 = node.valor + str(i)
		else:
			value1 = node.tipo + str(i)
		i = i + 1
		for son in node.filhos:
			w.edge(value1,str(son)+ str(i))
			verArvoreTexto(son,w,i)			

if __name__ == '__main__':
	from sys import argv, exit
	f = open(argv[1])
	arvore = Parser(f.read())

	verArvoreTerminal(arvore.ast)

	w = Digraph('G', filename='./Saidas/ArvoreRepr.gv')
	verArvoreTexto(arvore.ast,w,i = 0)
	w.view()


	file_object = open("./Saidas/SaidaArvore.txt", "w")
	file_object.write(w.source)
	file_object.close()