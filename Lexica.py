# -*- coding: utf-8 -*-
#Renan Kodama Rodrigues 1602098
#UTFPR-CM DACOM Compiladores

import ply.lex as lex

class Lexica:

    def __init__(self):
        self.lexer = lex.lex(debug=False, module=self, optimize=False)
    
    #Lista das ReservTags
    keywords = {
        'inteiro' : 'INTEIRO',
        'flutuante' : 'FLUTUANTE',
        'cientifico' : 'CIENTIFICO',
        'senão' : 'SENAO',
        'se' : 'SE',
        'fim' : 'FIM',
        'repita' : 'REPITA',
        'até' : 'ATE',
        'então' : 'ENTAO',
        'retorna' : 'RETORNA',
        'leia' : 'LEIA',
        'escreva' : 'ESCREVA',
    }

    #Lista das FreeTags
    tokens = [
        'NUMERO',
        'ADICAO',
        'SUBTRACAO',
        'MULTIPLICACAO',
        'DIVISAO',
        'PARENTESES_DIR',
        'PARENTESES_ESQ',
        'COLCHETE_DIR',
        'COLCHETE_ESQ',
        'SIMB_MENOR',
        'SIMB_MAIOR',
        'SIMB_MAIORIGUAL',
        'SIMB_MENORIGUAL',
        'ATRIBUICAO',
        'IGUAL',
        'ID',
        'STRING',
        'DIFERENTEDE',
        'NEGACAO',
        'VIRGULA',
        'E_LOGICO',
        'DOIS_PONTOS',
        
        #'CHAVE_DIR',
        #'CHAVE_ESQ',
        #'IGUALDADE',
    ] + list(keywords.values())


    #Expressões regulares
    t_ADICAO = r'\+'
    t_SUBTRACAO = r'\-'
    t_MULTIPLICACAO = r'\*'
    t_DIVISAO = r'/'
    t_IGUAL = r'='
    t_DIFERENTEDE = r'<>'
    t_VIRGULA = r'\,'
    t_ATRIBUICAO = r':=' 
    t_SIMB_MENOR = r'<'
    t_SIMB_MAIOR = r'>'
    t_SIMB_MAIORIGUAL = r'>='
    t_SIMB_MENORIGUAL = r'<='
    t_COLCHETE_DIR = r'\]'
    t_COLCHETE_ESQ = r'\['
    t_PARENTESES_DIR = r'\)'
    t_PARENTESES_ESQ = r'\('
    t_DOIS_PONTOS = r':'
    t_NUMERO = r'(\+|\-)?[0-9]+(\.[0-9]+)?'
    t_CIENTIFICO = r'(\+|\-)?[0-9]+(\.[0-9]+)?.e(\+|\-)?[0-9]+([0-9]+)?'
    t_NEGACAO = r'\!'
    t_E_LOGICO = r'\&\&'

    #t_IGUALDADE = r'=='
    #t_CHAVE_DIR = r'\}'
    #t_CHAVE_ESQ = r'\{'
    
    

    #Identificador de ID
    def t_ID(self, t):
        r'[a-zA-Zá-ñÁ-Ñ][_a-zA-Zá-ñÁ-Ñ0-9]*'
        t.type = self.keywords.get(t.value, 'ID')
        return t

    #Expressao para Comentarios
    def t_COMMENT(self,t):
        r'\{[^}]*[^{]*\}'

    #Contador de Linhas
    def t_newline(self,t):
        r'\n+'
        t.lexer.lineno += len (t.value)

    #Expressões ignoradas
    t_ignore = ' \t'

    #Expressao de erro
    def t_error(self,t):
        print("Caractere Ilegal '%s'" % t.value[0])
        t.lexer.skip(1)

    #Inicio da Análise
    def analiseLexica(arquivo):
        arq = open(arquivo)
        data = arq.read()

        #Direcionamento para pasta Saida
        arq_saida = arquivo.replace("/Testes/","/Saidas/")
        arq_saida = arq_saida.replace(".tpp","")
        arq_saida = open(arq_saida+"_saida.data",'w')

        lexer = lex.lex()
        lexer.input(data)

        #cabecalho do arquivo saída e resultados
        print ("\nArquivo Fonte: "+arquivo+'\n')
        print "Inicio da gravação...\n"
        print("(<Tipo>,<Valor>,<Linha>,<Coluna>)\n")
        arq_saida.write("Arquivo Fonte: "+arquivo+'\n')
        arq_saida.write('(<Tipo>,<Valor>,<Linha>,<Coluna>)\n\n') 

        #tokens
        while True:
            tok = lexer.token()

            if not tok:
                break
            
            print (tok.type,tok.value,tok.lineno,tok.lexpos)
            arq_saida.write('('+repr(tok.type)+' ')
            arq_saida.write(' '+repr(tok.value)+' ')
            arq_saida.write(' '+repr(tok.lineno)+' ')
            arq_saida.write(' '+repr(tok.lexpos)+') ')
            arq_saida.write('\n')

        arq.close()
        print "\nGravação concluida!"

if __name__ == '__main__':
    from sys import argv
    lexer = Lexica()
    f = open(argv[1])
    lexer.test(f.read())