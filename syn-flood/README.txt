Universidade de Brasília
Teleinformática e Redes 2 - 01/2017
Ataque SYN Flood

Alunos: Maximillian Fan Xavier - 12/0153271
        Rafael Dias da Costa - 12/0133253

 - Objetivo da tarefa
Esta tarefa tem como objetivo simular ataques DoS do tipo SYN Flood.

- Implementação
A tarefa foi implementada em SO Ubuntu 16.04 (64 bits) em linguagem Python, utilizando Python 2.7. 

==================================================================================
- Execução
Antes de executar a ferramenta "hbordimg", é recomendado rodar o comando -help:

$ python hbordimg.py --help

Serão mostrados no terminal os argumentos utilizáveis.

Para rodar um simples envio de 10 pacotes SYN para um servidor XXX.XXX.XX.X:

$ sudo python hbordimg.py -d XXX.XXX.XX.X -c 10

Para rodar um ataque (SYN Flood) no mesmo endereço:

$ sudo python hbordimg.py --flood -d XXX.XXX.XX.X

Para rodar o servidor, apenas rodar o código passando como argumento o IP e a porta desejados:

$ sudo python server.py IP PORT

==================================================================================
