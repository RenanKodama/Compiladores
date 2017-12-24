# -*- coding: utf-8 -*-
#Renan Kodama Rodrigues 1602098
#UTFPR-CM DACOM Compiladores

import Lexica
import Sintatica


def main ():
	print "Arquivos Exemplos: \n"
	
	print "\tbubble_sort.tpp" 		
	print "\tbusca_linear.tpp"
	print "\tfat.tpp"
	print "\tmultiplicavetor.tpp"
	print "\tprimo.tpp"
	print "\tsomavet.tpp"
	print "\tteste-1.tpp"
	print "\tteste-2.tpp"
	print "Entre com o Caminho do arquivo .(tpp): "
	
	local_arquivo = "./TestesLexicos/"+raw_input("\t")
	
	Lexica.analiseLexica(local_arquivo)


if __name__ == "__main__":
    main()