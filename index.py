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


def auth_user(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"Erro": "Token está em falta!", "Code": UNAUTHORIZED_CODE})

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])

            if data["expiration"] < str(datetime.utcnow()):
                return jsonify({"Erro": "O Token expirou!"}), NOT_FOUND_CODE

        except Exception as e:
            return jsonify({"Erro": "Token inválido"}), FORBIDDEN_CODE

        return func(*args, **kwargs)

    return decorated


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
        result = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        if result:
            token = jwt.encode(
                {
                    "username": u_username,
                    "expiration": str(datetime.utcnow() + timedelta(hours=1)),
                },
                SECRET_KEY,
            )
            token_str = token.decode("utf-8")
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


if __name__ == "__main__":
    app.run(debug=True)
