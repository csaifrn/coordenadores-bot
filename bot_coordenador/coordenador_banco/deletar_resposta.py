from database import get_connection 

def deletar_resposta(nome_discord, titulo):
    
    conn = get_connection()
    cursor = conn.cursor()

    # Obter o ID do aluno
    cursor.execute("SELECT id FROM aluno WHERE nome_discord = ?", (nome_discord,))
    aluno = cursor.fetchone()

    if aluno is None:
        conn.close()
        return False  # Retorna False caso o aluno não exista

    aluno_id = aluno[0]

    # Atualizar os campos resposta e timestamp_resposta para NULL
    cursor.execute('''
        UPDATE duvidas 
        SET resposta = NULL, timestamp_resposta = NULL
        WHERE aluno_id = ? AND titulo = ?
    ''', (aluno_id, titulo))

    conn.commit()
    conn.close()