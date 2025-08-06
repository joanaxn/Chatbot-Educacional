import mysql.connector

def ligar_bd():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="chatbot"
    )
    print("✅ Ligado à base de dados:", conn.database)  # Adiciona isto
    return conn