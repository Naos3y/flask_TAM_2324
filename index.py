from flask import Flask, request, jsonify
import psycopg2
import jwt
from datetime import datetime, timedelta
import os
from functools import wraps

app = Flask(__name__)
app.debug = True

host = os.environ.get("host")
dbname = os.environ.get("dbname")
user = os.environ.get("user")
password = os.environ.get("password")
SECRET_KEY = os.environ.get("SECRET_KEY")

NOT_FOUND_CODE = 400
OK_CODE = 200
SUCCESS_CODE = 201
BAD_REQUEST_CODE = 400
UNAUTHORIZED_CODE = 401
FORBIDDEN_CODE = 403
NOT_FOUND = 404
SERVER_ERROR = 500


def connect_to_db():
    return psycopg2.connect(host=host, dbname=dbname, user=user, password=password)


# Função para verificar a validade do token
def verify_token(token):
    print("Secret key abaixo:")
    print(SECRET_KEY)
    print("Token na verify_token abaixo:")
    print(token)
    print()
    print("tipo")
    print()
    print(type(token))

    try:
        # Verifica se "Bearer" está presente no token
        if "Bearer" in token:
            # Divide a string pelo espaço e pega o último elemento
            token = token.split(" ")[1]  # Atribui o token extraído à variável token
            print()
            print("token depois do bearer")
            print(token)
            print()
            print("tipoe")
            print()
            print(type(token))

            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            if decoded_token["expiration"] < str(datetime.utcnow()):
                return False, "Token expirou!"

            return True, "Token válido."

    except jwt.ExpiredSignatureError:
        return False, "O Token expirou!"
    except jwt.InvalidTokenError as e:
        return False, f"Token inválido. Detalhes: {str(e)}"
    except Exception as e:
        return False, f"Erro ao verificar o token: {str(e)}"


# Middleware para verificar o token antes de cada solicitação para inserir medicamento
@app.before_request
def before_request():
    if request.endpoint == "inserir_medicamento":
        token = request.headers.get("Authorization")
        print("token no request headers: ")
        print(token)
        print()
        if not token:
            return (
                jsonify({"Erro": "Token está em falta!", "Code": UNAUTHORIZED_CODE}),
                401,
            )

        is_valid, message = verify_token(token)
        if not is_valid:
            return jsonify({"Erro": message, "Code": UNAUTHORIZED_CODE}), 401


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    u_username = data.get("u_username")
    u_password = data.get("u_password")

    if "u_username" not in data or "u_password" not in data:
        return jsonify({"Code": BAD_REQUEST_CODE, "Erro": "Parâmetros inválidos"})

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.callproc("mydbtam.verifica_login", (u_username, u_password))
        id_utilizador = cursor.fetchone()[0]

        expiration_time = datetime.utcnow() + timedelta(hours=1)
        if id_utilizador > 0:
            token = jwt.encode(
                {
                    "id_utilizador": id_utilizador,
                    "username": u_username,
                    "expiration": expiration_time.strftime("%Y-%m-%d %H:%M:%S"),
                },
                SECRET_KEY,
                algorithm="HS256",
            )
            token_str = token.decode("utf-8")
            print("token descodificado no login em baixo: ")
            print(token_str)
            print()
            cursor.close()
            conn.close()
            return jsonify({"access_token": token_str}), OK_CODE
        else:
            return jsonify({"Erro": "Credenciais inválidas"}), UNAUTHORIZED_CODE

    except Exception as e:
        return jsonify({"Erro": str(e)}), SERVER_ERROR


@app.route("/register", methods=["POST"])
def register_user():
    data = request.json
    u_nome = data.get("u_nome")
    u_username = data.get("u_username")
    u_password = data.get("u_password")
    u_email = data.get("u_email")

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.callproc(
            "mydbtam.registar_utilizador",
            (u_nome, u_username, u_password, u_email),
        )
        result = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        if result == 0:
            return jsonify({"error": "Email ou username já existem."}), NOT_FOUND_CODE
        else:
            return (
                jsonify(
                    {"message": "Utilizador registado com sucesso!", "user_id": result}
                ),
                SUCCESS_CODE,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), NOT_FOUND_CODE


@app.route("/insert_medicamento", methods=["POST"])
def inserir_medicamento():
    data = request.json
    m_nome = data.get("m_nome")
    m_dosagem = data.get("m_dosagem")
    m_formafarmaceutica = data.get("m_formafarmaceutica")
    m_posologia = data.get("m_posologia")
    m_quantidade = data.get("m_quantidade")
    m_duracao = data.get("m_duracao")
    m_datainiciotratamento = data.get("m_datainiciotratamento")
    m_administrado = data.get("m_administrado")
    utilizador_id = data.get("utilizador_id_utilizador")
    m_horario1 = data.get("m_horario1")
    m_horario2 = data.get("m_horario2")
    m_horario3 = data.get("m_horario3")
    m_horario4 = data.get("m_horario4")

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.callproc(
            "mydbtam.inserir_medicamento",
            (
                m_nome,
                m_dosagem,
                m_formafarmaceutica,
                m_posologia,
                m_quantidade,
                m_duracao,
                m_datainiciotratamento,
                m_administrado,
                utilizador_id,
                m_horario1,
                m_horario2,
                m_horario3,
                m_horario4,
            ),
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Medicamento inserido com sucesso!"}), SUCCESS_CODE

    except Exception as e:
        return jsonify({"error": str(e)}), SERVER_ERROR


@app.route("/users", methods=["GET"])
def get_all_users():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        query = "SELECT * FROM mydbtam.mostrar_utilizadores;"
        cursor.execute(query)

        users = []
        for row in cursor.fetchall():
            user = {
                "user_id": row[0],
                "u_nome": row[1],
                "u_username": row[2],
                "u_email": row[3],
                "u_password": row[4],
            }
            users.append(user)

        cursor.close()
        conn.close()

        return jsonify(users), OK_CODE

    except Exception as e:
        return jsonify({"error": str(e)}), NOT_FOUND_CODE


@app.route("/medicamentos", methods=["GET"])
def get_all_medicamentos():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        query = "SELECT * FROM mydbtam.mostrar_medicamentos;"
        cursor.execute(query)

        medicamentos = []
        for row in cursor.fetchall():
            medicamento = {
                "id_medicamentos": row[0],
                "m_nome": row[1],
                "m_dosagem": row[2],
                "m_formafarmaceutica": row[3],
                "m_posologia": row[4],
                "m_horario1": row[5],
                "m_horario2": row[6],
                "m_horario3": row[7],
                "m_horario4": row[8],
                "m_quantidade": row[9],
                "m_duracao": row[10],
                "m_datainiciotratamento": row[11],
                "m_administrado": row[12],
                "utilizador_id_utilizador": row[13],
            }
            medicamentos.append(medicamento)

        cursor.close()
        conn.close()

        return jsonify(medicamentos), OK_CODE

    except Exception as e:
        return jsonify({"error": str(e)}), NOT_FOUND_CODE


if __name__ == "__main__":
    app.run(debug=True)
