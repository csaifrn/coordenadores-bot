
from database.database import get_connection 
 # Supondo que base.py cuida da conexão com o banco
from datetime import datetime
def registrar_duvida_no_banco(nome_discord, titulo, mensagens):
    """
    Registra uma dúvida no banco de dados SQLite.
    
    :param nome_discord: Nome do aluno no Discord.
    :param titulo: Título da dúvida.
    :param mensagens: Lista de mensagens da dúvida.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM aluno WHERE nome_discord = ?", (nome_discord,))
    aluno = cursor.fetchone()

    aluno_id = aluno[0]


    cursor.execute('''INSERT INTO duvidas (aluno_id, aluno_nome, titulo, mensagem,timestamp_duvida) 
                      VALUES (?, ?, ?, ?,?)''', 
                   (aluno_id, nome_discord, titulo, mensagens,datetime.now()))
    conn.commit()
    conn.close()