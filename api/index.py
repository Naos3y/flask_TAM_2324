from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

DB_HOST = "aid.estgoh.ipc.pt"
DB_PORT = "5432"
DB_NAME = "db2021141279"
DB_USER = "a2021141279"
DB_PASSWORD = "2021141279"


def connect_to_db():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )


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

        query = """
        INSERT INTO mydbtam.utilizador (u_nome, u_username, u_password, u_email, u_morada, u_data_nascimento)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id_utilizador;
        """

        cursor.execute(
            query,
            (u_nome, u_username, u_password, u_email, u_morada, u_data_nascimento),
        )
        user_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        return (
            jsonify(
                {"message": "Utilizador registrado com sucesso!", "user_id": user_id}
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
