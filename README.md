# bot para fazer carga do solar

Este projeto usa o poetry para gerenciar as dependências

## Para instalar as dependências

`poetry install`

## Usuário e Senha

Dentro da pasta app, deve-se criar um arquivo **.env** com as seguintes variáveis:

```text
USUARIO=
SENHA=
SENHA_EMAIL=
REMETENTE=
DESTINATARIOS=
```

## Para rodar o bot

Dentro da pasta app, execute o comando:

`poetry run python main.py`

## Resultado da carga

O resultado da carga estará no arquivo **output.log** localizado dentro da pasta app.
