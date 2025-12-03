from database import get_connection

def obter_duvidas_filtradas(nome_discord, inicio_periodo, tipo):
    
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
        if tipo == True:
            query += " AND resposta IS NOT NULL"
        elif tipo == False:
            query += " AND resposta IS NULL"

    cursor.execute(query, params)
    duvidas = cursor.fetchall()

    # Montar um dicionário com os resultados
    duvidas_dict = {
        titulo: {
            "mensagem": mensagem,
            "resposta": resposta,
            "visualizada": bool(visualizada),
            "timestamp_duvida": timestamp_duvida,  # Usa o valor diretamente como string
            "timestamp_resposta": timestamp_resposta,  # Usa o valor diretamente como string
        }
        for titulo, mensagem, resposta, visualizada, timestamp_duvida, timestamp_resposta in duvidas
    }
    duvidas_nao_visualizadas = dict(
            sorted(duvidas_dict.items(), key=lambda item: item[1]["timestamp_duvida"], reverse=True)
        )


    conn.close()
    return duvidas_nao_visualizadas
