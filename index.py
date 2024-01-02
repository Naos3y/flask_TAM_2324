from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)
app.debug = True

host = os.environ.get("host")
dbname = os.environ.get("dbname")
user = os.environ.get("user")
password = os.environ.get("password")

# os erros 400 e 201 indicam que exisiu um erro (bad request) ou que algo foi criado, respetivamente
# o 200 indica que esta tudo bem


def connect_to_db():
    return psycopg2.connect(host=host, dbname=dbname, user=user, password=password)


@app.route("/register", methods=["POST"])
def register_user():
    data = request.json
    u_nome = data.get("u_nome")
    u_username = data.get("u_username")
    u_password = data.get("u_password")
    u_email = data.get("u_email")
    u_morada = data.get("u_morada")
    u_data_nascimento = data.get("u_data_nascimento")

    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.callproc(
            "mydbtam.registar_utilizador",
            (u_nome, u_username, u_password, u_email, u_morada, u_data_nascimento),
        )
        result = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        if result == 0:
            return jsonify({"error": "Email ou username já existem."}), 400
        else:
            return (
                jsonify(
                    {"message": "Utilizador registado com sucesso!", "user_id": result}
                ),
                201,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 400


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
                "u_morada": row[4],
                "u_data_nascimento": row[5],
                "u_token": row[6],
            }
            users.append(user)

        cursor.close()
        conn.close()

        return jsonify(users), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
