# Início de um Projeto com Discord Bot

## 1. O que é um Discord Bot?

Um Discord bot é um programa que automatiza tarefas em servidores do Discord. Ele pode responder a comandos (slash commands), enviar mensagens, gerenciar interações e auxiliar na organização do servidor.

---

## 2. Pré-requisitos

* **Conta no Discord**
* **Conta no Discord Developer Portal**
* **Python 3.10+** instalado
* Editor de código (ex.: VS Code)

---

## 3. Criando o Aplicativo no Discord Developer

1. Acesse o **Discord Developer Portal**.
2. Clique em **New Application**.
3. Defina um nome para o aplicativo (ex.: *MeuBot*).

---

## 4. Criando o Bot

1. No menu lateral, acesse **Bot**.
2. Clique em **Add Bot**.
3. (Opcional) Defina nome e avatar do bot.

> ⚠️ **Importante:** Ative apenas os *Privileged Gateway Intents* necessários (ex.: *Message Content*, se o projeto exigir).

---

## 5. Token do Bot

* Copie o **Bot Token**.
* Guarde com segurança e **nunca publique** esse token.

---

## 6. Adicionando o Bot ao Servidor (Forma Correta)

1. Vá em **OAuth2 → URL Generator**.
2. Em **Scopes**, selecione **bot** (e **applications.commands**, se usar slash commands).
3. Em **Bot Permissions**, marque apenas as permissões necessárias (ex.: *Send Messages*, *Use Slash Commands*, *Administrator* apenas se realmente precisar).
4. Copie o link gerado, acesse-o no navegador e selecione o servidor.

> ❗ **Não marque** a opção *Requires OAuth2 Code Grant* para bots comuns. Ela é usada apenas para integrações externas.

---

# Rodando o Bot Localmente

## 1. Baixar o Repositório

* Use `git clone` **ou** baixe o ZIP.
* Abra a pasta no editor de código.

---

## 2. Instalar Dependências

No terminal:

```bash
pip install -r requirements.txt
```

---

## 3. Configurar o Token

* Crie um arquivo **.env** (caso não exista).
* Adicione:

```env
TOKEN=seu_token_aqui
```

> Obs.: não use aspas nem chaves.

---

## 4. Iniciar o Bot

No terminal, execute:

```bash
python index.py
```

---

## 5. Testar no Discord

* Abra o servidor onde o bot foi adicionado.
* Digite `/` e selecione um comando disponível.

---

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

| [<img src="https://avatars.githubusercontent.com/u/124364476?v=4" width=150><br><sub>David Paiva</sub>](https://github.com/davidmtg) | [<img src="https://avatars.githubusercontent.com/u/107737145?v=4" width=150><br><sub>Pedro Edi</sub>](https://github.com/Pedro-Edi) |
| :---: | :---: |

