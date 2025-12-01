from database.database import get_connection 
from datetime import datetime
def atualizar_mensagens(nome_discord, titulo, novas_mensagens, novo_titulo):
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM aluno WHERE nome_discord = ?", (nome_discord,))
    aluno = cursor.fetchone()


    aluno_id = aluno[0]

   
    cursor.execute('''UPDATE duvidas 
                    SET titulo = ?, mensagem = ? , timestamp_duvida= ?
                    WHERE aluno_id = ? AND titulo = ?''', 
                (novo_titulo, novas_mensagens,datetime.now(), aluno_id, titulo))
    conn.commit()
    conn.close()
