from database import get_connection

def atualizar_visualizada(nome_discord, titulo):
    
    conn = get_connection()
    cursor = conn.cursor()

    
    # Obter o ID do aluno
    cursor.execute("SELECT id FROM aluno WHERE nome_discord = ?", (nome_discord,))
    aluno = cursor.fetchone()

    if aluno is None:
        conn.close()
        return False

    aluno_id = aluno[0]

  
    cursor.execute('''UPDATE duvidas 
                    SET visualizada = ? 
                    WHERE aluno_id = ? AND titulo = ?''', 
                (True, aluno_id, titulo))

    conn.commit()
    conn.close()