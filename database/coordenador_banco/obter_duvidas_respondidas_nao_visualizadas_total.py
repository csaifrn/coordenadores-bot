from database.database import get_connection
from datetime import datetime

def obter_duvidas_respondidas_nao_visualizadas_total(inicio_periodo):
    """
    Retorna as dúvidas respondidas de todos os alunos, filtradas por período (se fornecido), 
    ordenadas pela data de resposta (timestamp_resposta) de forma que o aluno com a primeira resposta
    mais antiga apareça primeiro.
    :param inicio_periodo: Data inicial para filtrar as dúvidas (opcional)
    :return: Dicionário com as dúvidas respondidas de todos os alunos
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = '''
        SELECT aluno_nome, titulo, mensagem, resposta, visualizada, timestamp_duvida, timestamp_resposta
        FROM duvidas
        WHERE resposta IS NOT NULL AND visualizada = 0
    '''
    params = []

    if inicio_periodo:
        query += " AND timestamp_resposta >= ?"
        params.append(inicio_periodo)

    cursor.execute(query, params)
    duvidas = cursor.fetchall()

    duvidas_respondidas = {}

    for aluno_nome, titulo, mensagem, resposta, visualizada, timestamp_duvida, timestamp_resposta in duvidas:
        if aluno_nome not in duvidas_respondidas:
            duvidas_respondidas[aluno_nome] = {}

        duvidas_respondidas[aluno_nome][titulo] = {
            "mensagem": mensagem,
            "resposta": resposta,
            "visualizada": visualizada,
            "timestamp_duvida": timestamp_duvida,
            "timestamp_resposta": timestamp_resposta
        }

    for aluno_nome, duvidas_dict in duvidas_respondidas.items():
        sorted_duvidas = dict(sorted(duvidas_dict.items(), key=lambda item: item[1]["timestamp_resposta"], reverse=True))
        duvidas_respondidas[aluno_nome] = sorted_duvidas

    sorted_duvidas_respondidas = dict(
        sorted(
            duvidas_respondidas.items(),
            key=lambda item: max([d["timestamp_resposta"] for d in item[1].values()]),
            reverse=True
        )
    )
    conn.close()
    return sorted_duvidas_respondidas
