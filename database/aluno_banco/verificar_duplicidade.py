from database.database import get_connection

def verificar_duplicidade(nome_discord, titulo):
    """
    Verifica se já existe uma dúvida com o mesmo título registrada por um aluno.
    
    :param nome_discord: Nome do aluno no Discord.
    :param titulo: Título da dúvida a ser verificado.
    :return: True se o título já existir, False caso contrário.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM aluno WHERE nome_discord = ?", (nome_discord,))
    aluno = cursor.fetchone()

    if aluno is None:
        conn.close()
        raise ValueError("Usuário não encontrado no sistema.")  
    aluno_id = aluno[0]

    cursor.execute(
        "SELECT COUNT(*) FROM duvidas WHERE aluno_id = ? AND LOWER(titulo) = LOWER(?)",
        (aluno_id, titulo)
    )
    duplicidade = cursor.fetchone()[0]
    conn.close()

    return duplicidade > 0
