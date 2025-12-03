from database import get_connection 

def obter_duvidas_nao_respondidas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT aluno_nome, titulo, mensagem, timestamp_duvida
    FROM duvidas
    WHERE resposta IS NULL
    ''')

    duvidas = cursor.fetchall()
    # Organizando as dúvidas não respondidas por aluno
    duvidas_nao_respondidas = {}

    for duvida in duvidas:
        aluno_nome, titulo, mensagem, timestamp_duvida = duvida

        if aluno_nome not in duvidas_nao_respondidas:
            duvidas_nao_respondidas[aluno_nome] = {}

        duvidas_nao_respondidas[aluno_nome][titulo] = {
            "mensagem": mensagem,
            "resposta": None,
            "visualizada": False,
            "timestamp_duvida": timestamp_duvida,
            "timestamp_resposta": None
        }

    duvidas_nao_respondidas = dict(sorted(duvidas_nao_respondidas.items(), key=lambda item: item[1][list(item[1].keys())[0]]["timestamp_duvida"]))

    for aluno_nome, duvidas_dict in duvidas_nao_respondidas.items():
        duvidas_nao_respondidas[aluno_nome] = dict(sorted(duvidas_dict.items(), key=lambda item: item[1]["timestamp_duvida"]))

    conn.close()

    return duvidas_nao_respondidas
