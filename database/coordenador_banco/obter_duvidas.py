from database.database import get_connection
from datetime import datetime

def obter_duvidas():
    conn = get_connection()
    cursor = conn.cursor()

    query = '''
        SELECT aluno_nome, titulo, mensagem, resposta, visualizada, timestamp_duvida, timestamp_resposta
        FROM duvidas WHERE resposta IS NULL
    '''
    
    cursor.execute(query)
    duvidas = cursor.fetchall()
    conn.close()

    if not duvidas:
        return {}  

    duvidas.sort(key=lambda x: x[5])  
    aluno_alvo = duvidas[0][0]  

    duvidas_aluno = [d for d in duvidas if d[0] == aluno_alvo]
    
    resultado = {aluno_alvo: {}}
    for duvida in sorted(duvidas_aluno, key=lambda x: x[5]):
        aluno_nome, titulo, mensagem, resposta, visualizada, timestamp_duvida, timestamp_resposta = duvida
        resultado[aluno_nome][titulo] = {
            "mensagem": mensagem,
            "resposta": resposta,
            "visualizada": visualizada,
            "timestamp_duvida": timestamp_duvida,
            "timestamp_resposta": timestamp_resposta
        }
    
    return resultado

