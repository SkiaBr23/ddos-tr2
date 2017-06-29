# Servidor Node.js + Express.js + Servidor Proxy nginx:

## Pré-requisitos:
- Ubuntu 16.04 ou sistema Linux/Unix
- Node.js versão 6.11
- NPM versão 5.0.*
- Yargs versão 8.0.2
- Socket.io versão 2.0.3
- toobusy-js versão 0.5.1
- Express versão 4.15.3

## Como executar:
- `npm install`
- `node server.js --url=seu_ip` (para detectar seu ip digite `hostname -I`)
- O servidor estará disponível em `localhost:3000`

## Configurar nginx:
- Instalar nginx no [Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-set-up-a-node-js-application-for-production-on-ubuntu-16-04)
- Configurar um load balancer de acordo com o `load-balancer.conf` e salvá-lo no diretório `/etc/nginx/conf.d/` e deletar o atalho `default` de `/etc/nginx/sites-enabled/`, mais informações [aqui](https://www.upcloud.com/support/how-to-set-up-load-balancing/). Cada endereço em *upstream* deve ser o endereço de um servidor com a aplicação web ativa.

## Comandos úteis para nginx:
- `sudo systemctl restart nginx` - para reiniciar o *proxy* e refletir mudanças das configurações
- `stop` e `start` podem ser usados no lugar de `restart`
