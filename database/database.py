import sqlite3
def get_connection():
    """
    Retorna uma conexão com o banco de dados SQLite.
    """
    return sqlite3.connect("duvidas.db")

def criar_banco_e_tabelas():
    """
    Cria o banco de dados SQLite e as tabelas necessárias (aluno e duvidas).
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS aluno (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_discord TEXT NOT NULL UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS duvidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aluno_id INTEGER NOT NULL,
        aluno_nome TEXT NOT NULL,
        titulo TEXT NOT NULL,
        mensagem TEXT NOT NULL,
        resposta TEXT,
        visualizada BOOLEAN DEFAULT FALSE,
        timestamp_duvida DATETIME ,
        timestamp_resposta DATETIME,      
        FOREIGN KEY (aluno_id) REFERENCES aluno (id)
    )
    ''')

    conn.commit()
    conn.close()
    print("Banco de dados e tabelas criados com sucesso!")


        
if __name__ == "__main__":
    criar_banco_e_tabelas()
