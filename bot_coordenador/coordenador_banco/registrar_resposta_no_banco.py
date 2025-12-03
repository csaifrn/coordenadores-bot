from database import get_connection 

        
from datetime import datetime
def registrar_resposta_no_banco(nome_discord, titulo, resposta):
 
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM aluno WHERE nome_discord = ?", (nome_discord,))
    aluno = cursor.fetchone()

    if aluno is None:
        conn.close()
        return False

    aluno_id = aluno[0]

  
    cursor.execute('''UPDATE duvidas 
                    SET resposta = ? , timestamp_resposta = ?
                    WHERE aluno_id = ? AND titulo = ?''', 
                (resposta,datetime.now(),aluno_id, titulo))
    
    conn.commit()
    conn.close()
