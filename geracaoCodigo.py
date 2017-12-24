# -*- coding: utf-8 -*-
#Renan Kodama Rodrigues 1602098
#UTFPR-CM DACOM Compiladores

from llvmlite import ir
from Sintatica import Parser
from Semantica import Semantica

class LLVMCodeGenerator():
    def __init__(self, code):

        seman = Semantica(code)
        self.tree = Parser(code).ast
        self.module = ir.Module("programaTpp")
        
        self.simbolos = seman.hash
        self.pRintFI = None
        self.pRintFF = None
        self.sCanf = None
        self.sCanfF = None
        self.sCanfI = None
        self.escopo = "global"
        self.builder = None
        self.func = None    

        self.gen_programa(self.tree)
        
        
        print_trees(self.simbolos)
        print ("\n\n\n\n\n")
        print(self.module)

        arquivo = open('./SaidaGera/saida_modulo.ll', 'w')
        arquivo.write(str(self.module))
        arquivo.close()

                         
    def gen_inicializacao_variaveis(self,node):
        self.gen_atribuicao(node.filhos[0])

    def gen_declaracao_variaveis(self, node):
        tipo = node.filhos[0].tipo
        string=""
        i=0 
        complemento=""  
        var = None

        for son in self.gen_lista_variaveis(node.filhos[1]):      
            if self.escopo == "global":
                if("[" in son):                            
                    for i in range(len(son)):
                        if (son[i]=="["):
                            break
                        string += son[i]
                    complemento=son[i:]
                    son=string
                if(self.escopo == "global"):
                    if(tipo == "inteiro"):
                        var = ir.GlobalVariable(self.module, ir.IntType(32),son)
                        var.initializer = ir.Constant(ir.IntType(32), 0)
                        var.linkage = "common"
                        var.align = 4
                    if(tipo == "flutuante"):
                        var = ir.GlobalVariable(self.module, ir.FloatType(),son)
                        var.initializer = ir.Constant(ir.FloatType(), 0)
                        var.linkage = "common"
                        var.align = 4
            else:
                if(tipo=="inteiro"):
                    var = self.builder.alloca(ir.IntType(32), name=son)
                    var.align = 4
               
                if(tipo=="flutuante"):
                    var = self.builder.alloca(ir.FloatType(), name=son)
                    var.align = 4


            self.simbolos[self.escopo+"-"+son] = ["variavel",son,False,False,tipo+complemento,self.escopo,var]           
        return "void"

    def gen_lista_variaveis(self, node):
        ret_args=[]
        if(len(node.filhos)==1):                              
            if(len(node.filhos[0].filhos))==1:
                ret_args.append(node.filhos[0].valor+self.indice(node.filhos[0].filhos[0]))
            else:
                ret_args.append(node.filhos[0].valor)
            return ret_args
        else:                                                     
            ret_args=self.gen_lista_variaveis(node.filhos[0])
            if(len(node.filhos[1].filhos))==1:
                ret_args.append(node.filhos[1].valor)+self.indice(node.filhos[1].filhos[0])    
            else:
                ret_args.append(node.filhos[1].valor)        

            return ret_args    

    def gen_declaracao_funcao(self, node):
        if len(node.filhos) == 1:         
            tipo = "void"
            if(self.simbolos[node.filhos[0].valor][2]==None):
                str_args = ir.VoidType()
            else:
                str_args = self.simbolos[node.filhos[0].valor][2]
            self.escopo = node.filhos[0].valor
            return_tipo = ir.VoidType()

            args_tipo = []
            
            if(str_args!="void"):
                for i in str_args:
                    if(i == "inteiro"):
                        args_tipo.append(ir.IntType(32))
                    if(i == "flutuante"):
                        args_tipo.append(ir.FloatType())
            
            fnReturntipo = ir.VoidType()
            
            t_func = ir.FunctionType(fnReturntipo, args_tipo)
            
            self.func = ir.Function(self.module, t_func, name=node.filhos[0].valor)
            
            entryBlock = self.func.append_basic_block('entry')
            endBasicBlock = self.func.append_basic_block('exit')
            
            self.builder = ir.IRBuilder(entryBlock)
            self.simbolos[node.filhos[0].valor]=["funcao",node.filhos[0].valor,[],tipo,0,self.escopo,self.func] 
            self.gen_cabecalho(node.filhos[0])
        
        else:                              
            tipo = self.gen_tipo(node.filhos[0])  
            return_tipo = None
            str_args = None

            if(self.simbolos[node.filhos[1].valor][2] == None):
                str_args = ir.Voidtipo()
            else:
                str_args = self.simbolos[node.filhos[1].valor][2]
            

            self.escopo = node.filhos[1].valor
            

            if(tipo == ir.IntType(32)):
                return_tipo = ir.IntType(32)

            if(tipo == ir.FloatType()):
                return_tipo = ir.FloatType()
            

            args_tipo = []
            
            if(str_args != "void"):
                for i in str_args:
                    if(i == "inteiro"):
                        args_tipo.append(ir.IntType(32))
                    if(i == "flutuante"):
                        args_tipo.append(ir.FloatType())

            fnReturntipo = return_tipo
            t_func = ir.FunctionType(fnReturntipo, args_tipo)
            self.func = ir.Function(self.module, t_func, name=node.filhos[1].valor)

            entryBlock = self.func.append_basic_block('entry')
            #endBasicBlock = self.func.append_basic_block('exit')
            
            self.builder = ir.IRBuilder(entryBlock)
            self.simbolos[node.filhos[1].valor]=["funcao",node.filhos[1].valor,[],tipo,0,self.escopo,self.func] 
            self.gen_cabecalho(node.filhos[1])


    def gen_programa(self,node):
        self.gen_lista_declaracoes(node.filhos[0])

    def gen_lista_declaracoes(self, node):
        if len(node.filhos)==1:          
            self.gen_declaracao(node.filhos[0])
        else:
            self.gen_lista_declaracoes(node.filhos[0])
            self.gen_declaracao(node.filhos[1])

    def gen_declaracao(self,node):                       
        if node.filhos[0].tipo == "declaracao_variaveis":
            self.gen_declaracao_variaveis(node.filhos[0])
        elif(node.filhos[0].tipo=="inicializacao_variaveis"):
            self.gen_inicializacao_variaveis(node.filhos[0])
        else:
            if(len(node.filhos[0].filhos)==1):               
                self.escopo=node.filhos[0].filhos[0].valor    
            else:                                          
                self.escopo=node.filhos[0].filhos[1].valor   

            self.gen_declaracao_funcao(node.filhos[0])   
            self.escopo="global"


    def gen_cabecalho(self,node):
        lista_par = self.gen_lista_parametros(node.filhos[0]) 
        self.simbolos[node.valor][2]=lista_par
        tipo_corpo=self.gen_corpo(node.filhos[1])
        tipo_fun = self.simbolos[node.valor][3]

    def gen_lista_parametros(self, node):   
            lista_param = []            
            if len(node.filhos)==1:      
                if(node.filhos[0] == None):  
                    return self.gen_vazio(node.filhos[0])
                else:
                    lista_param.append(self.gen_parametro(node.filhos[0]))   
                    return lista_param                                  

            else:                                                       
                lista_param = self.gen_lista_parametros(node.filhos[0])      
                lista_param.append(self.gen_parametro(node.filhos[1]))       
                return lista_param

    def gen_vazio(self, node):
        return "void"

    def gen_parametro(self, node):
        if node.filhos[0].tipo == "parametro":               
            return self.gen_parametro(node.filhos[0])+"[]"
        self.simbolos[self.escopo+"-"+node.valor]=["variavel",node.valor,False,True,node.filhos[0].tipo,self.escopo] 
        return self.gen_tipo(node.filhos[0])                     

    def gen_tipo(self,node):
        if node.tipo == "inteiro":
            return ir.IntType(32)
        if node.tipo == "flutuante":
            return ir.FloatType()

    def gen_corpo(self, node):      
        if len(node.filhos)==1:                      
            return self.gen_vazio(node.filhos[0])
        
        else:                                      
            tipo1c = self.gen_corpo(node.filhos[0])   
            tipo2c = self.gen_acao(node.filhos[1])  
            if(tipo2c!=None):
                return tipo2c

    def gen_acao(self, node):
        tipo_ret_acao = "void"
        if node.filhos[0].tipo=="expressao":                    
            return self.gen_expressao(node.filhos[0])
        elif node.filhos[0].tipo=="declaracao_variaveis":        
            return self.gen_declaracao_variaveis(node.filhos[0])
        elif node.filhos[0].tipo=="se":                          
            return self.gen_se(node.filhos[0])
        elif node.filhos[0].tipo=="repita":                 
            return self.gen_repita(node.filhos[0])
        elif node.filhos[0].tipo=="leia":                       
            return self.gen_leia(node.filhos[0])
        elif node.filhos[0].tipo=="escreva":                   
            return self.gen_escreva(node.filhos[0])

        elif node.filhos[0].tipo == "retorna":
            endBasicBlock = self.func.append_basic_block('exit')
            self.builder.branch(endBasicBlock)
            self.builder = ir.IRBuilder(endBasicBlock)

            

            if node.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].tipo == 'numero':
                valor = node.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].valor    
                if '.' not in valor:
                    res = ir.Constant(ir.IntType(32), int(valor))
                else:
                    res = ir.Constant(ir.FloatType(), float(valor))

                self.builder.ret(res)

            else:   #retorna tipo variavel
                if node.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].tipo == "var":
                    valor = node.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].valor
                    
                    try:
                        self.builder.ret(self.simbolos[self.escopo+'-'+valor][6])
                    except:
                        self.builder.ret(self.simbolos['global-'+valor][6])
                else:
                    
                    auxiliar = node.filhos[0].filhos[0].filhos[0].filhos[0]

                    operador = None
                    while auxiliar.tipo == "expressao_aditiva":
                        for noh in auxiliar.filhos:
                            if noh.tipo == "operador_soma" or noh.tipo == "operador_multiplicacao":
                                operador = noh.valor

                            if noh.tipo == "expressao_multiplicativa":
                                if noh.filhos[0].filhos[0].filhos[0].tipo == "var":
                                    nomeVar = noh.filhos[0].filhos[0].filhos[0].valor

                        auxiliar = auxiliar.filhos[0]


                    
                    self.builder.ret(ir.Constant(ir.IntType(32), int(0)))


            return self.gen_retorna(node.filhos[0])
        elif node.filhos[0].tipo == "error":                      
            return self.gen_error(node.filhos[0])

    def gen_expressao(self, node):        
        if node.filhos[0].tipo=="expressao_simples":             
            return self.gen_expressao_simples(node.filhos[0])
        else:                                                  
            return self.gen_atribuicao(node.filhos[0])


    def gen_expressao_simples(self, node):
        if len(node.filhos)==1:                                    
            return self.gen_expressao_aditiva(node.filhos[0])
        else:                                              
            tipo1=self.gen_expressao_simples(node.filhos[0])     
            self.gen_operador_relacional(node.filhos[1])         
            tipo2=self.gen_expressao_aditiva(node.filhos[2])    
            return "logico"

    def gen_expressao_aditiva(self, node):          
        if len(node.filhos)==1:                                   
            return self.gen_expressao_multiplicativa(node.filhos[0])
        else:                                                       
            tipo1=self.gen_expressao_aditiva(node.filhos[0])   
            self.gen_operador_soma(node.filhos[1])                     
            tipo2=self.gen_expressao_multiplicativa(node.filhos[2])
            if((tipo1=="flutuante") or (tipo2=="flutuante")):        
                return "flutuante"
            else:
                return "inteiro"

    def gen_expressao_multiplicativa(self, node):
        if len(node.filhos)==1:                              
            return self.gen_expressao_unaria(node.filhos[0])
        else:                                                     
            tipo1=self.gen_expressao_multiplicativa(node.filhos[0])      
            self.gen_operador_multiplicacao(node.filhos[1])              
            tipo2=self.gen_expressao_unaria(node.filhos[2])              
            if((tipo1=="flutuante") or (tipo2=="flutuante")):         
                return "flutuante"
            else:
                return "inteiro"

    def gen_expressao_unaria(self, node):
        if len(node.filhos)==1:                                
            return self.gen_fator(node.filhos[0])
        else:                                               
            self.gen_operador_soma(node.filhos[0])
            return self.gen_fator(node.filhos[1])

    def gen_fator(self, node):
        if(node.filhos[0].tipo=="var"):                     
            return self.gen_var(node.filhos[0])
        if(node.filhos[0].tipo=="chamada_funcao"):       
            return self.gen_chamada_funcao(node.filhos[0])
        if(node.filhos[0].tipo=="numero"):               
            return self.gen_numero(node.filhos[0])
        else:                                           
            return self.gen_expressao(node.filhos[0])

    def gen_atribuicao(self, node):                             
        try:
            nomevariavel = self.escopo+'-'+node.filhos[0].valor
            variavelCodigo = self.simbolos[nomevariavel][6]
        except:
            nomevariavel = 'global-'+node.filhos[0].valor
            variavelCodigo = self.simbolos[nomevariavel][6]

        self.gen_expressao(node.filhos[1])

        self.simbolos[nomevariavel][2] = True 
        self.simbolos[nomevariavel][3] = True  

        if node.filhos[1].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].tipo == "numero":
            valorAtt = node.filhos[1].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].valor

            if '.' not in valorAtt:
                try:
                    self.builder.store(ir.Constant(ir.IntType(32),int(valorAtt)), self.simbolos[nomevariavel][6])
                except:
                    self.builder.store(ir.Constant(ir.IntType(32),float(valorAtt)), self.builder.load(self.simbolos[nomevariavel][6]))
            else:
                try:
                    self.builder.store(ir.Constant(ir.FloatType(),float(valorAtt)), self.simbolos[nomevariavel][6])
                except:
                    self.builder.store(ir.Constant(ir.FloatType(),int(valorAtt)), self.simbolos[nomevariavel][6])
        else:
            auxiliar = node.filhos[1].filhos[0].filhos[0]
            auxiliar1 = auxiliar
            numeroCodigo = None
            numeroCodigo1 = None
            operador = None
            numero = None
            numero1 = None
            res = None

            while auxiliar1 == "expressao_aditiva":
                auxiliar1 = auxiliar1.filhos[0]


            if auxiliar1.filhos[0].filhos[0].filhos[0].filhos[0].tipo == "var":
                try:
                    nomeAttVar = self.escopo+'-'+auxiliar1.filhos[0].filhos[0].filhos[0].filhos[0].valor
                    codigAttVat = self.simbolos[nomeAttVar][6]
                except:
                    nomeAttVar = 'global-'+auxiliar1.filhos[0].filhos[0].filhos[0].filhos[0].valor
                    codigAttVat = self.simbolos[nomeAttVar][6]


                self.builder.store(self.builder.load(codigAttVat),self.simbolos[nomevariavel][6])

            else:
                if auxiliar1.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].tipo == "numero":
                    numero = auxiliar1.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].valor
                    if '.' not in numero:
                        numeroCodigo = ir.Constant(ir.IntType(32),int(numero))
                    else:
                        numeroCodigo = ir.Constant(ir.FloatType(),float(numero))



            while auxiliar.tipo == "expressao_aditiva":
                for noh in auxiliar.filhos:
                    if noh.tipo == "operador_soma" or noh.tipo == "operador_multiplicacao":
                        operador = noh.valor
                    
                    if noh.tipo == "expressao_multiplicativa":
                        if noh.filhos[0].filhos[0].filhos[0].tipo == "numero":
                            numero1 = noh.filhos[0].filhos[0].filhos[0].valor


                            if '.' not in numero1:
                                numeroCodigo1 =  ir.Constant(ir.IntType(32),int(numero1))
                            else:
                                numeroCodigo1 =  ir.Constant(ir.FloatType(),float(numero1))

                            if (numeroCodigo1 != None and numeroCodigo != None):
                                if operador == '+':
                                    res = self.builder.fadd(numeroCodigo1, numeroCodigo, name='add')
                                elif operador == '-':
                                    res = self.builder.fsub(numeroCodigo1, numeroCodigo, name='sub')
                                elif operador == '*':
                                    res = self.builder.fmul(numeroCodigo1, numeroCodigo, name='mul')
                                elif operador == '/':
                                    res = self.builder.fdiv(numeroCodigo1, numeroCodigo, name='div')

                            if res != None:
                                self.builder.store(res,self.simbolos[nomevariavel][6])

                if auxiliar.filhos[0] != "expressao_aditiva":
                    break
                else:
                    auxiliar = auxiliar.filhos[0]

        return "void"

    def gen_lista_argumentos(self, node):
        if(len(node.filhos) == 1):                
            if(node.filhos[0] == None):
                return 
            if(node.filhos[0].tipo == "expressao"):
                return (self.gen_expressao(node.filhos[0]))


            else:
                return []
        else:                                  
            ret_args = []
            ret_args.append(self.gen_lista_argumentos(node.filhos[0]))
            if(not(tipo(ret_args[0]) is str)):
                ret_args = ret_args[0]

            ret_args.append(self.gen_expressao(node.filhos[1]))
            return ret_args




    def indice(self, node):         
        if(len(node.filhos)==1):    
            tipo = self.gen_expressao(node.filhos[0]) 

            return("[]")
        else:
            variavel=self.indice(node.filhos[0])      
            tipo=self.expressao(node.filhos[1])      

            return ("[]"+variavel)   

    

    def gen_operador_relacional(self, node):
        return None

    def gen_operador_soma(self, node):      
        return None

    def gen_operador_multiplicacao(self, node):
        return None

    
    
    def gen_var(self,node):
        name =self.escopo+"-"+node.valor
        if(len(node.filhos)==1):                        
            if(name not in self.simbolos):              
                name = "global-"+node.valor

            self.simbolos[name][4] = self.simbolos[name][4] 
            self.simbolos[name][2] = True
            return self.simbolos[name][4]

        else:                                       

            if(name not in self.simbolos):          
                name = "global-"+node.valor

            self.simbolos[name][2] = True           
            return self.simbolos[name][4] 

    def gen_numero(self, node):                 
        string = repr(node.valor)                        
        if "."in string:                                
            return "flutuante"
        else:
            return "inteiro"


    def gen_chamada_funcao(self, node):                         
        nome_func = node.valor
        func = self.builder.load(self.simbolos[nome_func][6])
        argsToFunc = []
        argsToFuncLoad = []

        auxiliar = node.filhos[0]
        while auxiliar.tipo == "lista_argumentos":
            auxiliar = auxiliar.filhos[0]
        
        if auxiliar.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0] == "var":
            nomeVar = auxiliar.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].valor
            try:
                argsToFunc.append(self.simbolos[self.escopo+'-'+nomeVar][6])
            except:
                argsToFunc.append(self.simbolos['global-'+nomeVar][6])



        auxiliar = node.filhos[0]
        while auxiliar.tipo == "lista_argumentos":
            for noh in auxiliar.filhos:
                if noh.tipo == "expressao":
                    if noh.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].tipo == "var":
                        nomeVar = noh.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].valor
                        
                        try:
                            argsToFunc.append(self.simbolos[self.escopo+'-'+nomeVar][6])
                        except:
                            argsToFunc.append(self.simbolos['global-'+nomeVar][6])
            
            auxiliar = auxiliar.filhos[0]


        for i in argsToFunc:
            argsToFuncLoad.append(self.builder.load(i))


        try:
            self.builder.call(func,argsToFuncLoad,name=nome_func)
        except:
            print("chamadaFuncaoExcpt")


        return self.simbolos[node.valor][3]             

    

    def gen_se(self, node):
        tipo_se = self.gen_expressao(node.filhos[0])
        
        exp1 = None
        exp2 = None
        operador = None

        entao_se = self.func.append_basic_block('Se')
        

        if node.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].tipo == "var":
            nome = node.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].valor
            try:
                exp1 = (self.simbolos[self.escopo+'-'+nome][6])
            except:
                exp1 = (self.simbolos['global-'+nome][6])
        else:
            numero = node.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].valor
            if '.' not in numero:
                exp1 = ir.Constant(ir.IntType(32),int(numero))
            else:
                exp1 = ir.Constant(ir.FloatType(),float(numero))


        if node.filhos[0].filhos[0].filhos[0].tipo == "expressao_simples":
            for noh in node.filhos[0].filhos[0].filhos:
                if noh.tipo == "operador_relacional":
                    operador = noh.valor

                if noh.tipo == "expressao_aditiva":

                    if noh.filhos[0].filhos[0].filhos[0].filhos[0].tipo == "var":
                        nome = noh.filhos[0].filhos[0].filhos[0].filhos[0].valor
                        try:
                            exp2 = (self.simbolos[self.escopo+'-'+nome][6])
                        except:
                            exp2 = (self.simbolos['global-'+nome][6])
                    else:
                        numero = noh.filhos[0].filhos[0].filhos[0].filhos[0].valor
                        if '.' not in numero:
                            exp2 = ir.Constant(ir.IntType(32),int(numero))
                        else:
                            exp2 = ir.Constant(ir.FloatType(),float(numero))

        res = self.builder.icmp_signed(operador, self.builder.load(exp1), exp2)

        if len(node.filhos) == 3:
             senao_se = self.func.append_basic_block('Senão')
        fim_se = self.func.append_basic_block('FIM')

        if len(node.filhos) == 3:
            self.builder.cbranch(res, entao_se, senao_se)
        else:
            self.builder.cbranch(res, entao_se, fim_se)

        self.builder.position_at_start(entao_se)
        self.gen_corpo(node.filhos[1])
        self.builder.branch(fim_se)

        if len(node.filhos) == 3:
            self.builder.position_at_start(senao_se)
            self.gen_corpo(node.filhos[2])
            self.builder.branch(fim_se)
            self.builder.position_at_start(fim_se)


    def gen_repita(self, node):
        repita = self.func.append_basic_block('Repita')
        fim = self.func.append_basic_block('Fim')
        self.builder.branch(repita)
        self.builder.position_at_start(repita)
        self.gen_corpo(node.filhos[0])

        exp1 = None
        exp2 = None
        operador = None

        if node.filhos[1].tipo == "expressao":
            if node.filhos[1].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].tipo == "var":
                nome = node.filhos[1].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].valor
                try:
                    exp1 = (self.simbolos[self.escopo+'-'+nome][6])
                except:
                    exp1 = (self.simbolos['global-'+nome][6])

            else:
                numero = node.filhos[1].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].valor
                if '.' not in numero:
                    exp1 = ir.Constant(ir.IntType(32),int(numero))
                else:
                    exp1 = ir.Constant(ir.FloatType(),float(numero))


            for noh in node.filhos[1].filhos[0].filhos:
                if noh.tipo == "operador_relacional":
                    operador = noh.valor
                if noh.tipo == "expressao_aditiva":
                    if noh.filhos[0].filhos[0].filhos[0].filhos[0].tipo == "numero":
                        numero = noh.filhos[0].filhos[0].filhos[0].filhos[0].valor

                        if '.' not in numero:
                            exp2 = ir.Constant(ir.IntType(32),int(numero))
                        else:
                            exp2 = ir.Constant(ir.FloatType(),float(numero))
        



        if operador == "=":
            operador = "=="

        res = self.builder.icmp_signed(operador, exp1, exp2)
        self.builder.cbranch(res, fim, repita)
        self.builder.position_at_start(fim)

       
        return self.gen_expressao(node.filhos[1])

    def gen_leia(self, node):
        codeVar = None
        tipo = None
        res = None

        try:
            codeVar = self.simbolos[self.escopo+"-"+node.valor][6]
            tipo =  self.simbolos[self.escopo+"-"+node.valor][4]
        except:
            codeVar = self.simbolos["global-"+node.valor][6]
            tipo =  self.simbolos["global-"+node.valor][4]


        if codeVar != None:
            if self.pRintFI == None:
                leia_FunctionCode = ir.FunctionType(ir.IntType(32),[])
                self.pRintFI = ir.Function(self.module,leia_FunctionCode,'LeiaI')
                

            if self.pRintFF == None:
                leia_FunctionCode = ir.FunctionType(ir.FloatType(),[])
                self.pRintFF = ir.Function(self.module,leia_FunctionCode,'LeiaF')
                
            
            if tipo == "inteiro":
                res = self.builder.call(self.pRintFI,[])
            else:
                res = self.builder.call(self.pRintFF,[])


            if res != None:
                self.builder.store(res,codeVar)

        
        return "void"

    def gen_escreva(self, node):
        tipo_exp = self.gen_expressao(node.filhos[0])
        nomeVar = None
        codigoVar = None
        tipo = None


        if node.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].tipo == "var":
            nomeVar = node.filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].filhos[0].valor
    
            try:    
                tipo = self.simbolos[self.escopo+'-'+nomeVar][4]
            except:
                tipo = self.simbolos['global-'+nomeVar][4]            

            if self.sCanfI == None:
                escreva_Function_Code = ir.FunctionType(ir.VoidType(), [ir.IntType(32)])    
                self.sCanfI = ir.Function(self.module,escreva_Function_Code,'EscrevaI')                
            
            if self.sCanfF == None:
                escreva_Function_Code = ir.FunctionType(ir.VoidType(), [ir.FloatType()])            
                self.sCanfF = ir.Function(self.module,escreva_Function_Code,'EscrevaF') 

            try: 
                codigoVar = self.simbolos[self.escopo+"-"+nomeVar][6]
            except:
                codigoVar = self.simbolos["global-"+nomeVar][6]     

            loadVar = self.builder.load(codigoVar)

            try:
                if tipo == "inteiro":
                    self.builder.call(self.sCanfI,[loadVar])
                else:
                    self.builder.call(self.sCanfF,[loadVar])
            except:
                aux = ir.Constant(ir.IntType(32), 0)
                self.builder.call(self.sCanfI,[aux])
                print("gen_escrevaExcept")
            

        return "void"
        
    def gen_retorna(self, node):
        
        
        tipo_exp = self.gen_expressao(node.filhos[0])

        return tipo_exp

def print_trees(simbolos):
    for k,v in simbolos.items():
        print(repr(k)+repr(v))

if __name__ == '__main__':
    import sys
    code = open(sys.argv[1])
    LLVMCodeGenerator(code.read())