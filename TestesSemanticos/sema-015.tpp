{Warning: Chamada recursiva para principal}
{Warning: função func nao utilizada}
{Warning: variavel a flutuante recebendo um inteiro}
{Erro: função func do tipo inteiro retornando flutuante}

flutuante: a
inteiro: b

inteiro func()
  a := 10
  retorna(a)
fim

inteiro principal()
	b := 18
	principal()
fim
