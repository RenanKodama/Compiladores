# -*- coding: utf-8 -*-
#Renan Kodama Rodrigues 1602098
#UTFPR-CM DACOM Compiladores


from llvmlite import ir
from Sintatica import Parser
from ply import yacc

class Semantica():

	def __init__(self, code):						#Tipo, Nome_var, 

		self.hash = {} 								#se funcao 	-> Paramentros, Usada, Tipo
		self.escopo = "global"						#inicia global   se variavel-> Usada, Atribuida, Tipo, Escopo		
		self.tree = Parser(code).ast 				#chamada da funcao Sintatica.tree
		self.programa(self.tree)					#inicio da arvore
		self.contem_principal(self.hash)			#funcao para verificar se no arquivo contem a funcao principal
		self.variaveis_utilizadas(self.hash)		#gera warnings se uma variavel foi declarada e nao utilizada 
		self.funcoes_utilizadas(self.hash)			#gera warnings se uma funcao foi declarada e nao utilizada

	def programa(self,node):					#inicio da arvore	
		self.lista_declaracoes(node.filhos[0])	#programa produz lista_declaracoes 

	def lista_declaracoes(self, node):			#segundo passo da arvore
		if len(node.filhos) == 1:				#produçao de lista contem mais de um caso, ou declaraçao ou lista_declaracoes e declaracao 
			self.declaracao(node.filhos[0])	
		else:
			self.lista_declaracoes(node.filhos[0])
			self.declaracao(node.filhos[1])

	def declaracao(self,node):									#como as produçoes para declaracao tem tamanho 1 em seus filhos foram diferenciados atraves do tipo
		if node.filhos[0].tipo == "declaracao_variaveis":
			self.declaracao_variaveis(node.filhos[0])			#produçao para delclaracao_variaveis
		elif (node.filhos[0].tipo == "inicializacao_variaveis"):	
			self.inicializacao_variaveis(node.filhos[0])		#producao para inicializaca_variaveis
		else:							
			if (len(node.filhos[0].filhos) == 1):				#quando as funcoes forem do tipo void 
				self.escopo = node.filhos[0].filhos[0].valor 	#declaracao->declaracao_funcao->cabecalho.valor 					
			else:												#para funcoes diferentes de void
				self.escopo = node.filhos[0].filhos[1].valor  

			self.declaracao_funcao(node.filhos[0])	
			self.escopo = "global"								#volta escopo para global apos fim das declaracoes 


	def declaracao_variaveis(self, node):						#para a declaracao de variaveis foi chamado a funçao lista de variaveis
		variavel_tipo = node.filhos[0].tipo 	
		variavel_nome = ""
		variavel_complemento = ""	
		i = 0	

		for filho in self.lista_variaveis(node.filhos[1]): 		#lista_variaveis retorna um vetor de variaveis, para cada variavel é feito
			if("[" in filho):									#verifica se contem o colchetes na variavel 
				for i in range(len(filho)):
					if (filho[i] == "["):
						break
					variavel_nome += filho[i]					#até nao encontrar o colchetes adiciona os caracteres que compoe o nome da variavel
				variavel_complemento=filho[i:]					#adiciona o complemento da variavel ex:[10]
				filho=variavel_nome

			if ((self.escopo+"-"+filho  in self.hash.keys()) or ("global-"+filho  in self.hash.keys())):
				print("ERRO: variavél já declarada: "+repr(filho)) 					#se o nome da variael estiver no hash hash , nao pode declara lá novamente
				exit(1)

			if filho  in self.hash.keys():
				print("ERRO: já existe uma função com nome: "+repr(node.valor))		#verifica se uma funcao ja foi declarada
				exit(1)

			#adiciona a varivel na tabela se hash
			self.hash[self.escopo+"-"+filho]=["variavel",filho,False,False,variavel_tipo+variavel_complemento,self.escopo] 

		
	def inicializacao_variaveis(self,node):	#funcao inicializacao_variaveis chama apenas atribuicao 
		self.atribuicao(node.filhos[0])	


	def lista_variaveis(self, node): #para a funcao lista_variaveis foi feito
		argumentos = []		
		if (len(node.filhos) == 1): #se o tamanho das producoes forem de tamanho 1 entao apenas uma varivel declarada
			if (len(node.filhos[0].filhos)) == 1: #se a variavel foi array entao é passado o indice para verificalo
				argumentos.append(node.filhos[0].valor+self.indice(node.filhos[0].filhos[0])) #é adicionado em argumentos o "nome_var"[]
			else:
				argumentos.append(node.filhos[0].valor) #se nao for um array entao é adicionado apenas o nome

			return argumentos
		else:
	 		argumentos = self.lista_variaveis(node.filhos[0]) #caso tenha uma lista de variaveis entao é chamado novamente lista_variaveis
 			argumentos.append(node.filhos[1].valor)

	 		return argumentos
 

	def var(self,node):	#funcao var, verifica se uma variavel ja foi declarada
		rotulo = self.escopo+"-"+node.valor #atribui o escopo mais o nome da variavel 

		if(rotulo not in self.hash):	#se o rotulo nao estiver no escopo local
			rotulo = "global-"+node.valor
			
			if(rotulo not in self.hash):	#se o rotulo nao está no escopo global
				print("ERRO: variável não declarada "+node.valor)
				exit(1)
		
		if(self.hash[rotulo][3] == False):	#se a variavel estiver sendo usada sem atribuicao
			print("ERRO: variável sem contudo definido "+rotulo)
			#exit(1)

		self.hash[rotulo][2] = True		#indica que a varivael na hash foi usada

		return self.hash[rotulo][4] 	#retorna o tipo da variavel


	def indice(self, node):	#funcao para verifiar o indice entre os colchetes
		if(len(node.filhos) == 1): #se tamanho igual a 1
			tipo = self.expressao(node.filhos[0]) #recebe o tipo da variavel (expressao->expressao_simples->expressao_aditiva->expressao_multiplicativa->expressao_unaria)


			if(tipo == "inteiro"): #index aceita apenas inteiro
				return("[]")
		
			else:
				print("ERRO: tipo diferento no index do array [?] permitido apenas inteiro")
				exit(1)

		else:	#verificaçao para matriz
			variavel = self.indice(node.filhos[0])
			expressaoTipo = self.expressao(node.filhos[1])
			if(expressaoTipo != "inteiro"):
				print("ERRO: tipo diferento no index do array [?] permitido apenas inteiro")
				exit(1)
			return ("[]"+variavel)
			

	def tipo(self,node):#funcao que retorna o tipo da variavel determinada pela linguagem
		if node.tipo == "inteiro" or node.tipo == "flutuante" or node.tipo == "cientifico":
			return node.tipo
		else:
			print("ERRO: esperado inteiro,flutuante ou cientifico. Foi recebido "+node.tipo)
	

	def declaracao_funcao(self, node): #declaracao_funcao diferenciado pelo tamanho
		if len(node.filhos) == 1: #se tamanho 1 entao tipo é void 
			
			if node.filhos[0].valor in self.hash.keys(): #se a funcao estiver em simbolos entao ela foi declarada
				print ("ERRO: função já declarada: "+repr(node.filhos[0].valor))
				exit(1)
			
			elif "global-"+node.filhos[0].valor in self.hash.keys(): #se a variavel estiver no escopo global entao ela já foi declarada
				print ("ERRO: variável já declarada: "+node.filhos[0].valor)
				exit(1)
			
			self.hash[node.filhos[0].valor] = ["funcao",node.filhos[0].valor,[],False,"void"]	
			self.cabecalho(node.filhos[0])
		
		else: #caso contrario ele tem um tipo definido (inteiro ou flutuante)
			tipo = self.tipo(node.filhos[0])	#recebe o tipo da variavel
			
			self.hash[node.filhos[1].valor] = ["funcao",node.filhos[1].valor,[],False,tipo]
			self.cabecalho(node.filhos[1])	#chamada da funcao cabecalho


	def cabecalho(self,node): 
		parametros = self.lista_parametros(node.filhos[0]) 	#recebe vetor de paramentros 

		self.hash[node.valor][2] = parametros 	#atribui os paramentros no hash de simbolos
		
		returnTipo = self.corpo(node.filhos[1]) 	#recebe o tipo de return 
		funcTipo = self.hash[node.valor][4] 	#recebe o tipo do escopo de funcao
		
		if returnTipo != funcTipo: #compara os tipos
			if(node.valor == "principal"):
				print("Aviso: função "+node.valor+" deveria retornar "+funcTipo+" porem retorna "+returnTipo)
			else:	
				print("ERRO: função "+node.valor+" deveria retornar "+funcTipo+" porem retorna "+returnTipo)
				#exit(1)
			
			


	def lista_parametros(self, node): #lista_parametros produz: listade_parametros parametro|parametro|vazio
			parametros = []
			if len(node.filhos)==1:	#se tamanho do filho for 1 entao pode ser parametro ou vazio
				if(node.filhos[0] == None):	#se o valor do filho em v[0] for null entao é chamado a funcao vazio
					return self.vazio(node.filhos[0])
				else:	#se nao chamar a funcao paramentro pois à apenas um parametro
					parametros.append(self.parametro(node.filhos[0]))
					return parametros

			else: #caso seja uma lista de parametros entao é chamado novamente a funcao 
				parametros = self.lista_parametros(node.filhos[0])
				parametros.append(self.parametro(node.filhos[1]))
				return parametros
					

	def parametro(self, node): #funcao parametro pode produzir tipo|parametro, foi diferenciado pelo tipo pois tamanho sao iguais
		if node.filhos[0].tipo == "parametro": #se tipo for parametro entao é chamado a funcao de parametro
			return self.parametro(node.filhos[0])+"[]"
		self.hash[self.escopo+"-"+node.valor]=["variavel",node.valor,False,True,node.filhos[0].tipo]
		return self.tipo(node.filhos[0]) #caso contrario é chamado a funcao tipo

	def vazio(self, node): #funcao vazio apenas retorna a string vazio
		return "void"
	
	
	def corpo(self, node): #funcao corpo produz: corpo acao|vazio
		if len(node.filhos)==1: #se filho for de tamanho um entao chamar funcao vazia
			return self.vazio(node.filhos[0]) 	
		
		else:	#caso contrario podruz corpo e acao
			self.corpo(node.filhos[0]) #chamada para corpo 
			tipoAcao = self.acao(node.filhos[1])	#chamada para acao e recebe o tipo da acao

			return tipoAcao

	def acao(self, node): 	#funcao acao diferenciada pelo tipo produz: expressao|declaracao_variaveis|se|repita|leia|escreva|retorna|erro
		if node.filhos[0].tipo=="expressao": 	#se tipo for expressao
			return self.expressao(node.filhos[0])

		elif node.filhos[0].tipo=="declaracao_variaveis": 	#se tipo for lista_variaveis
			return self.declaracao_variaveis(node.filhos[0]) 

		elif node.filhos[0].tipo=="se": 	#se for uma condicao SE
			return self.se(node.filhos[0])

		elif node.filhos[0].tipo=="repita":		#se for um laco REPITA
			return self.repita(node.filhos[0])

		elif node.filhos[0].tipo=="leia": 	#se for um operacao LEIA
			return self.leia(node.filhos[0])

		elif node.filhos[0].tipo=="escreva": 	#se for uma operacao ESCREVA
			return self.escreva(node.filhos[0])

		elif node.filhos[0].tipo=="retorna": 	#se for uma operacao de retorno 
			return self.retorna(node.filhos[0])

		elif node.filhos[0].tipo=="error": 	#se for erro definido como error(default)
			return self.error(node.filhos[0])

	def se(self, node): #funcao SE produz: expressao corpo|expressao corpo corpo
		condicao = self.expressao(node.filhos[0]) #chamada da funcao expressao 
		
		if condicao != "logico":
			print("ERRO: não é uma expressao logica, "+condicao)
			exit(1)
		
		if len(node.filhos) == 2: #se tamanho igual a dois entao apenas chamar a funcao corpo
			return self.corpo(node.filhos[1])

		else: #caso contrario há duas produções com corpo
			corpo1 = self.corpo(node.filhos[1]) 	#retornar o escopo da funcao 
			corpo2 = self.corpo(node.filhos[2])

			if corpo1 != corpo2:
				if(corpo1 == "void"):
					return corpo2
				else:
					return corpo1

			return corpo1

	def repita(self, node): #funcao repita produz: corpo expressao
		repeticao = self.expressao(node.filhos[1]) #chamada da funcao corpo

		if repeticao != "logico": #se na expressao da repeticao nao for uma operacao logica 
			print("ERRO: não é uma expressao logica, "+repeticao)
			exit(1)
			
		return self.corpo(node.filhos[0]) #chamada da funcao copor e retorno do corpo
		

	def atribuicao(self, node): 	#chamada de funcao para atribuicao produz: var expressao
		escopo = self.escopo+"-"+node.filhos[0].valor 	#retorno do escopo da funcao
			
		if(self.escopo+"-"+node.filhos[0].valor not in self.hash.keys()): 	#se a variavel usada nao esta no escopo local
			escopo = "global"+"-"+node.filhos[0].valor 	#atribuicao para o escopo global
			if("global"+"-"+node.filhos[0].valor not in self.hash.keys()): 	#se a variavel usada nao esta no escopo global
				print ("ERRO: variável não declarada, "+node.filhos[0].valor)	
				exit(1)	#se a variavel nao esta no escopo local nem global entao ela nao foi declarada 
		
		tipo = self.hash[escopo][4] 	#tipo da variavel antes do simbolo :=
		tipo_exp = self.expressao(node.filhos[1]) 	#tipo da variavel depois do simbolo :=
		
		self.hash[escopo][2] = True	#declaracao correta entao marque -a como usada
		self.hash[escopo][3] = True	#declaracao correta entao marque -a como atribuida 

		if '[' in tipo:
			if(len(node.filhos[0].filhos) == 1):
				if (node.filhos[0].filhos[0].filhos[0].tipo == "indice"):
					self.indice(node.filhos[0].filhos[0].filhos[0])
					auxiliar = node.filhos[0].filhos[0].filhos[1].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].valor
					if ('.' in auxiliar):
						print("ERRO: indice invalido espera -se inteiro, recebido "+repr(auxiliar))
						exit(1)

				else:
					self.indice(node.filhos[0].filhos[0])

		if (len(node.filhos) > 1):
			auxiliar = node.filhos[1].filhos[0].filhos[0]

			while auxiliar.tipo == "expressao_aditiva":
				for noh in auxiliar.filhos:
					if noh.tipo == "expressao_multiplicativa":
						if noh.filhos[0].filhos[0].filhos[0].tipo == "numero":
							if "." in noh.filhos[0].filhos[0].filhos[0].valor and '[' in tipo_exp:
								print("ERRO: indice invalido espera -se inteiro, recebido "+repr(noh.filhos[0].filhos[0].filhos[0].valor))

						elif noh.filhos[0].filhos[0].filhos[0].tipo == "var":
							if (len(node.filhos[1].filhos[0].filhos[0].filhos) != 1):
								
								if noh.filhos[0].filhos[0].filhos[0].tipo != "var":
									if noh.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].tipo == "indice":
										self.indice(noh.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0])

										if (noh.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0] == "indice"): 	
											numero = noh.filhos[0].filhos[0].filhos[0].filhos[0].filhos[1].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].valor
												
											if ('.' in numero):
												print("ERRO: indice invalido espera -se inteiro, recebido "+repr(numero))
												exit(1)

									else:
										self.indice(noh.filhos[0].filhos[0].filhos[0].filhos[0])
								else:
									try:
										self.hash[self.escopo+'-'+noh.filhos[0].filhos[0].filhos[0].valor]
									except:
										try:
											self.hash["global-"+noh.filhos[0].filhos[0].filhos[0].valor]
										except:									
											print("Variavel não declarada "+repr(noh.filhos[0].filhos[0].filhos[0].valor))
											exit(1)


				auxiliar = auxiliar.filhos[0]
				
		if ('[' in tipo):
			tipo = tipo.replace("[",'')
			tipo = tipo.replace("]",'')			

		if ('[' in tipo_exp): 	#se conter um colchete após o sinal de atribuicao entao é um vetor
			tipo_exp = tipo_exp.replace("[",'')
			tipo_exp = tipo_exp.replace("]",'')


		if (tipo != tipo_exp): #se os tipos da variavel e sua atibuicao forem diferentes entao
			print ("ERRO: Coerção de tipos esperado: "+repr(tipo)+" recebido: "+repr(tipo_exp))
			#exit(1)
		
		return "void"


	def leia(self, node): 	#funcao nao tem producao
		if self.escopo+"-"+node.valor not in self.hash.keys(): #se a variavel passada para print nao estiver no escopo local
			if "global-"+node.valor not in self.hash.keys():	#se a variavel para print nao estiver no escopo global
				print("ERRO: variável não declarada" + repr(node.valor))	# entao a variavel nao foi declarada
				exit(1)
		
		return "void"

	def escreva(self, node): 	#funcao escreva produz uma expressao
		expressao = self.expressao(node.filhos[0]) 	#recebe o típo da expressao
		
		if expressao == "logico":	#se expressao nao for do tipo logico entao invalido
			print("ERRO: expressão inválida")
			exit(1)

		return "void"
		
	def retorna(self, node): 	#funcao retorna produz uma expressao
		expressao = self.expressao(node.filhos[0])	#recebe o tipo de expressao
		
		if expressao == "logico": 	#se expressao for logica entao invalida
			print("ERRO: expressão inválida")	
			exit(1)

		return expressao
		

	def expressao(self, node): 	#funcao expressao produz: expressao_simples|atribuicao
		if node.filhos[0].tipo=="expressao_simples": 	#diferenciado atraves do tipo
			return self.expressao_simples(node.filhos[0])
		else:
			return self.atribuicao(node.filhos[0])


	def expressao_simples(self, node): #funcao expressao_simples produz: expressao_aditiva|exp_simples operador_relacional exp_aditiva 
		if len(node.filhos) == 1: 	#se tamanho igual a 1 entao expressao_aditiva
			return self.expressao_aditiva(node.filhos[0])
		
		else: 	#senao 
			expressao_simplesTipo=self.expressao_simples(node.filhos[0])	#recebe o tipo da primeira parte da expressao exp_simples
			
			self.operador_relacional(node.filhos[1])	#chamada da funcao operador_relacional
			
			expressao_aditivaTipo=self.expressao_aditiva(node.filhos[2])	#recebe o tipo da segunda parte da expressao exp_aditiva
			
			if(expressao_simplesTipo!=expressao_aditivaTipo): 	#se os tipo das ambas expressoes forem diferentes estao aviso
				print("Aviso: Operacao com tipos diferentes "+repr(expressao_simplesTipo)+"' e '"+expressao_aditivaTipo)
				
			return "logico"


	def expressao_aditiva(self, node): 	#funcao expressao_aditiva produz: expressao_multiplicativa|expressao_aditiva operador_soma expressao_multiplicativa
		if len(node.filhos) == 1:		#se filho tiver tamanho 1 entao chamar funcao_multiplicativa
			return self.expressao_multiplicativa(node.filhos[0])
		
		else: 	#senao produz: expressao_aditiva operador_soma expressao_multiplicativa
			
			expressao_aditivaTipo = self.expressao_aditiva(node.filhos[0]) #recebe o tipo da expressao_aditiva
			
			self.operador_soma(node.filhos[1])
			
			expressao_multiplicativaTipo = self.expressao_multiplicativa(node.filhos[2])	#recebe o tipo da expressao_multiplicativa

			if (expressao_aditivaTipo != expressao_multiplicativaTipo): 	#compara os tipo das expressoes
				print("Aviso: operação com valores diferentes '"+expressao_aditivaTipo+"' e '"+expressao_multiplicativaTipo)
			
			if ((expressao_aditivaTipo == "flutuante") or (expressao_multiplicativaTipo == "flutuante")):	#retorna o tipo da expressao se flutuante
				return "flutuante"
			
			else:
				return "inteiro"	#retorna se inteiro


	def expressao_multiplicativa(self, node):	#funcao expressao_multiplicativa produz: expressao_unaria|exp_multiplicativa operador_multiplicacao exp_unaria 
		if len(node.filhos) == 1: 	#se tamanho 1 entao expressao_unaria
			return self.expressao_unaria(node.filhos[0])
		
		else: 	#caso contrario produz: exp_multiplicativa operador_multiplicacao exp_unaria 
			
			expressao_multiplicativaTipo=self.expressao_multiplicativa(node.filhos[0]) 	#recebe tipo da expressa_multiplicativa
			
			self.operador_multiplicacao(node.filhos[1]) 	#chama a funcao operador_relacional
			 
			expressao_unariaTipo=self.expressao_unaria(node.filhos[2])	#recebe o tipo da expressao_unaria
			
			if (expressao_multiplicativaTipo!=expressao_unariaTipo): 	#compara ambos os tipo da exp_unaria e multplicativa, se tipos diferentes
				print("Aviso: operaçãao com valores diferentes '"+expressao_multiplicativaTipo+"' e '"+expressao_unariaTipo)
			
			if ((expressao_multiplicativaTipo == "flutuante") or (expressao_unariaTipo == "flutuante")):
				return "flutuante"
			else:
				return "inteiro"


	def expressao_unaria(self, node): 	#funcao expressao_unaria produz: fator|operador_soma fator
		if len(node.filhos)==1:		#se filho tiber tamanho 1 entao fator
			return self.fator(node.filhos[0]) 	#chamada da funcao fator
		
		else: 	#caso contrario produz: operador_soma fator
			self.operador_soma(node.filhos[0]) 	#chamada da funcao operador_soma 
			return self.fator(node.filhos[1])	#retorno do tipo do fator


	def operador_relacional(self, node): 	
		return None

	def operador_soma(self, node):
		return None

	def operador_multiplicacao(self, node):
		return None


	def fator(self, node):	#funcao fator produz: expressao|var|chamada_funcao|numero
		if(node.filhos[0].tipo == "var"):	#filhos diferenciados atraves do tipo, se var
			return self.var(node.filhos[0])
		
		if(node.filhos[0].tipo == "chamada_funcao"): 	#se tipo for uma chamada_funcao
			return self.chamada_funcao(node.filhos[0])
		
		if(node.filhos[0].tipo == "numero"): 	#se tipo for um numero
			return self.numero(node.filhos[0])
		
		else:
			return self.expressao(node.filhos[0]) 	#se tipo for uma expressao


	def numero(self, node): #funcao numero nao contem producao
		variavel_conteudo = repr(node.valor) 	#recebe o conteudo da variavel

		if (("e" in variavel_conteudo) or ("E" in variavel_conteudo)): 	#se na variavel_conteudo conter um e ou E entao cientifico
			return "cientifico"

		elif "." in variavel_conteudo: 	#se na variavel_conteudo conter o simbolo . entao é um flutuante
			return "flutuante"

		else: 	#caso nenhuma das anteriores entao variavel_conteudo é um inteiro
			return "inteiro"


	def chamada_funcao(self, node): 	#funcao chamada_funcao produz: lista_argumentos
		if (node.valor == "principal" and self.escopo == "principal"): 	#se o nome da chamada de funcao for principal e o escopo local é a principal entao
			print("Aviso: recursão para a função principal")

		if (node.valor == "principal" and self.escopo != "principal"): 	#se a chamada da funcao for principal e o escopo for diferente de principal...
			print("ERRO: chamada para principal pela função "+self.escopo) 	# ...entao é uma chamada para principal por outra funcao fora do escopo
			#exit(1)
		
		if node.valor not in self.hash.keys(): 	#se o nome da funcao nao estiver no hash entao ela nao foi declarada
			print ("ERRO: função não declarada "+repr(node.valor))
			exit(1)
		
		argumentosPassados = [] 	
		argumentosPassados.append(self.lista_argumentos(node.filhos[0]))	#adiciona lista de algumentos passados

		if (argumentosPassados[0] == None):		#se nao foi passado nenhum argumento entao lista vazia
			argumentosPassados = []

		elif (type(argumentosPassados[0]) != str):	#se a lista nao for str entao lista_argumentos->lista_argumentos->expressao
			argumentosPassados = argumentosPassados[0]

		argumentosEsperados = self.hash[node.valor][2] 	#recebe a lista de argumentos 
		
		if (type(argumentosEsperados) is str): 	
			argumentosEsperados = []

		if (len(argumentosPassados) != len(argumentosEsperados)): 	#se tamanho diferente nas listas de argumentos entao erro
			print("ERRO: argumentos esperados por "+repr(node.valor) +" "+repr(len(argumentosEsperados))+", passados: "+repr(len(argumentosPassados)))
			exit(1)

		for i in range(len(argumentosPassados)): 	#se o tamanho é igual entao é comparado tipo por tipo dos argumentos passados e esperados
			if (argumentosPassados[i] != argumentosEsperados[i]):  #caso o tipo seja diferente entao erro 
				print("ERRO: esperado "+argumentosEsperados[i]+", passado "+argumentosPassados[i]+" na posição "+repr(i))
				#exit(1)
		
		self.hash[node.valor][3] = True 	#sinaliza que a funcao foi utlizada
		return self.hash[node.valor][4] 	#retorno do tipo da funcao


	def lista_argumentos(self, node): 	#funcao lista_argumentos produz: lista_argumentos expressao|expressao|vazio
	 	if (len(node.filhos) == 1): 	#se tamanho igual a 1 entao produz: expressao|vazio
	 		if (node.filhos[0] == None): 	#se vazio entao
	 			return 
	 		
	 		if (node.filhos[0].tipo == "expressao"):	#caso o tipo seja expressao entao é chamado a funcao expressao
	 			return (self.expressao(node.filhos[0]))

	 		else:
	 			return []

	 	else: 	#caso contrario produz: lista_argumentos expressao 
	 		argumentos = []
	 		argumentos.append(self.lista_argumentos(node.filhos[0])) 	#recebe vetor argumentos
	 		
	 		if(type(argumentos[0]) != str):
	 			argumentos = argumentos[0]

	 		argumentos.append(self.expressao(node.filhos[1])) 	
	 		
	 		return argumentos 	#retorna vetor de argumentos


	def contem_principal(self, hash):	#funcao que verifica se contem principal no hash
	 	if("principal" not in hash.keys()): 	
	 		print("ERRO: função principal não foi declarada")
	 		#exit(1)


	def funcoes_utilizadas(self, hash): 	#verifica funcao nao utilizadas
		for(chave,valores) in hash.items():	 #para toda key se seu conteudo 
			if(valores[0] == "funcao" and chave != "principal"):  #se nao for principal e for funcao
				if(valores[3] == False): 	#posicao 3 indica se foi utilizada, se falso entao nao utilizada
					print("Aviso: função nunca utilizada " + repr(chave))


	def variaveis_utilizadas(self, hash):	#verifica quais variaveis nao foram utilizadas
		for chave,valores in hash.items():  	#para toda chave se seu valor 
			if (valores[0] == "variavel"): 	#verificando apenas variaveis 	
				
				if (valores[2] == False): 	#se a variavel nao foi utilizada 
					escopo = chave.split("-") 	
					
					if (escopo[0] != "global"): #se nao esta no escopo global 
						printf = escopo[0]
					
					else:
						printf = "global"
					
					print("Aviso: variável "+repr(valores[1])+" em "+repr(printf)+" nunca é utilizada")



def ver_ArvoreTerminal(node, level="-"):
    if node != None:
        print("%s %s %s" %(level, node.tipo, node.valor))
        for son in node.filhos:
            ver_ArvoreTerminal(son, level+"-")


def ver_hasLista(hash):
    for k,v in hash.items():
    	print(v)


if __name__ == '__main__':
	import sys
	code = open(sys.argv[1])
	s = Semantica(code.read())
	
	ver_hasLista(s.hash)
	ver_ArvoreTerminal(s.tree)
