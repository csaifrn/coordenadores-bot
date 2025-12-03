

from database import get_connection
def obter_duvidas_com_resposta_nao_visualizada(nome_discord):
   
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM aluno WHERE nome_discord = ?", (nome_discord,))
    aluno = cursor.fetchone()

    if aluno is None:
        conn.close()
        return {} 
    aluno_id = aluno[0]

    cursor.execute('''
    SELECT titulo, mensagem, resposta, visualizada, timestamp_duvida, timestamp_resposta
    FROM duvidas
    WHERE aluno_id = ? AND resposta IS NOT NULL AND visualizada = 0
    ''', (aluno_id,))

    duvidas = cursor.fetchall()
    duvidas_dict = {}

    for duvida in duvidas:
        titulo, mensagem, resposta, visualizada, timestamp_duvida, timestamp_resposta = duvida
        duvidas_dict[titulo] = {
            "mensagem": mensagem,
            "resposta": resposta,
            "visualizada": visualizada,
            "timestamp_duvida": timestamp_duvida,
            "timestamp_resposta": timestamp_resposta
        }
    duvidas_nao_visualizadas = dict(
            sorted(duvidas_dict.items(), key=lambda item: item[1]["timestamp_resposta"], reverse=True)
        )


    conn.close()
    return duvidas_nao_visualizadas
