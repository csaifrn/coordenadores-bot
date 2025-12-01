from database.database import get_connection

def obter_duvidas(nome_discord, inicio_periodo, tipo):
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM aluno WHERE nome_discord = ?", (nome_discord,))
    aluno = cursor.fetchone()

    if aluno is None:
        conn.close()
        return {} 

    aluno_id = aluno[0]

    query = '''
        SELECT titulo, mensagem, resposta, visualizada, timestamp_duvida, timestamp_resposta
        FROM duvidas
        WHERE aluno_id = ?
    '''
    params = [aluno_id]

    # Adicionar filtro por período, se fornecido
    if inicio_periodo:
        query += " AND timestamp_duvida >= ?"
        params.append(inicio_periodo)

    # Adicionar filtro por tipo (respondidas ou não respondidas)
    if tipo:
        if tipo == "duvidas_com_resposta":
            query += " AND resposta IS NOT NULL"
        elif tipo == "duvidas_sem_resposta":
            query += " AND resposta IS NULL"
        elif tipo=="duvidas_nao_visualizadas":
            query += " AND resposta IS NOT NULL AND visualizada IS FALSE"

    cursor.execute(query, params)
    duvidas = cursor.fetchall()

    # Montar um dicionário com os resultados
    duvidas_dict = {
        titulo: {
            "mensagem": mensagem,
            "resposta": resposta,
            "visualizada": bool(visualizada),
            "timestamp_duvida": timestamp_duvida, 
            "timestamp_resposta": timestamp_resposta, 
        }
        for titulo, mensagem, resposta, visualizada, timestamp_duvida, timestamp_resposta in duvidas
    }
    duvidas_nao_visualizadas = dict(
            sorted(duvidas_dict.items(), key=lambda item: item[1]["timestamp_duvida"], reverse=True)
        )


    conn.close()
    return duvidas_nao_visualizadas
