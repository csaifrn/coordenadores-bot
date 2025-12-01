from database.database import get_connection

def deletar_duvida(nome_discord, titulo):
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM aluno WHERE nome_discord = ?", (nome_discord,))
    aluno = cursor.fetchone()

    if aluno is None:
        conn.close()
        return False  

    aluno_id = aluno[0]

    cursor.execute('''DELETE FROM duvidas 
                      WHERE aluno_id = ? AND titulo = ?''', 
                   (aluno_id, titulo))

    conn.commit()
    conn.close()
