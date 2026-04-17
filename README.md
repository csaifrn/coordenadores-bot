# Início de um Projeto com Discord Bot

## 1. O que é um Discord Bot?

* Um Discord bot é um programa que automatiza tarefas no servidor do Discord. Ele pode responder a comandos de texto, moderar chats, enviar mensagens e muito mais.

## 2. Pré-requisitos para Criar um Discord Bot

* Conta Discord.
* Conta no Discord Developer Portal.

## 3. Criar um Novo Aplicativo Discord

* Acesse o Discord Developer Portal.
* Clique em **New Application**.
* Defina um nome para o aplicativo (ex.: MeuBot).

> ⚠️ **Observação:** Atualmente, ao criar uma Application, o Discord **já cria automaticamente o bot**. Por isso, pode não aparecer mais o botão "Add Bot".

## 4. Configuração do Bot

* Acesse a aba **Bot** no menu lateral.
* Copie o **TOKEN** do bot.

> 🚨 **Atenção:** Nunca compartilhe o token publicamente.

### ⚠️ Importante sobre "Authorize Flow"

Na aba **Bot**, existe a opção **Authorize Flow**, incluindo a configuração **"Requires OAuth2 Code Grant"**.

❌ **Essa opção NÃO deve ser ativada para bots comuns** feitos com `discord.py`, slash commands ou prefixo.

Essa configuração é usada apenas para:

* Aplicações web
* Sistemas com login via Discord (OAuth2)
* Integrações que utilizam `redirect_uri`

Se ativada indevidamente, o bot **não será adicionado ao servidor**, mesmo após autorizar pelo link.

## 5. Adicionar o Bot ao Servidor (Forma Correta)

### Passo 1 – OAuth2 URL Generator

* Vá em **OAuth2 → URL Generator**
* Marque os escopo:

  * ☑️ `bot`

### Passo 2 – Permissões

* Selecione as permissões desejadas (Administrator seria o ideal)

### Passo 3 – Convite

* Copie o link gerado
* Abra no navegador
* Selecione o servidor
* Autorize

✅ O bot aparecerá automaticamente no servidor.

## O que é preciso para rodar o bot no seu Servidor Discord?

### 1. Baixar o repositório

* Clone o repositório ou baixe o ZIP.
* Abra a pasta no editor de código (ex.: VS Code).

### 2. Instalar o Python

* Instale o Python pelo site oficial.

### 3. Criar um ambiente virtual e instalar as dependências

* Recomenda-se o uso de um **ambiente virtual** para evitar conflitos entre bibliotecas.

**Criar o ambiente virtual:**

```bash
python -m venv venv
```

**Ativar o ambiente virtual:**

* Windows:

```bash
venv\Scripts\activate
```

* Linux / macOS:

```bash
source venv/bin/activate
```

**Instalar as dependências do projeto:**

* As bibliotecas necessárias já estão listadas no arquivo `requirements.txt`.

````bash
pip install -r requirements.txt

````

### 4. Configurar o token

* Crie um arquivo `.env`.
* Dentro dele, adicione:

```env
TOKEN1=token do coordenador
TOKEN2=token do aluno
```

> Não use aspas nem chaves.

## Inicializar o Bot

* No terminal, execute:

```bash
python index.py
```

## Testar o Bot no Discord

* No servidor, digite `/` e selecione um comando disponível.

## Estrutura Básica do Projeto

* **bot_aluno/**: comandos e lógica do bot do aluno.
* **bot_coordenador/**: comandos e lógica do bot do coordenador.
* **database.py**: inicialização e gerenciamento do banco de dados.
* **duvidas.db**: banco de dados compartilhado.
* **index.py**: inicialização geral do sistema.
* **requirements.txt**: dependências do projeto.
* **README.md**: documentação.
* **.gitignore**: arquivos ignorados pelo Git.

---

# AUTORES

| [<img src="https://avatars.githubusercontent.com/u/178320852" width=150><br><sub>Sarah Medeiros dos Santos</sub>](https://github.com/sarahmds) | [<img src="https://avatars.githubusercontent.com/u/161068456" width=150><br><sub>Gabriel</sub>](https://github.com/gabrielzzzs) | [<img src="https://avatars.githubusercontent.com/u/124364195" width=150><br><sub>João Pedro Nascimento</sub>](https://github.com/JpRevolut) |
| :---: | :---: | :---: |
