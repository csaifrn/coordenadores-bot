from database.database import get_connection

def registrar_aluno_no_banco(nome_discord):
    """
    Verifica se o aluno existe no banco de dados. Se não existir, registra o aluno.
    :param nome_discord: Nome do usuário no Discord.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Verifica se o aluno já existe
    cursor.execute('''SELECT id FROM aluno WHERE nome_discord = ?''', (nome_discord,))
    aluno = cursor.fetchone()

    # Se o aluno não existir, insere o aluno no banco de dados
    if aluno is None:
        cursor.execute('''INSERT INTO aluno (nome_discord) VALUES (?)''', (nome_discord,))
        conn.commit()

    conn.close()
