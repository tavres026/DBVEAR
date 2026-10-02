from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Nome do banco SQLite
DATABASE = "biblioteca.db"


# Função responsável por conectar ao banco
def conectar_banco():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row

    # Ativa o uso das chaves estrangeiras
    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao


# Página inicial
@app.route("/")
def inicio():

    conexao = conectar_banco()

    quantidade_livros = conexao.execute(
        "SELECT COUNT(*) AS total FROM livros"
    ).fetchone()["total"]

    quantidade_autores = conexao.execute(
        "SELECT COUNT(*) AS total FROM autores"
    ).fetchone()["total"]

    quantidade_categorias = conexao.execute(
        "SELECT COUNT(*) AS total FROM categorias"
    ).fetchone()["total"]

    conexao.close()

    return render_template(
        "index.html",
        quantidade_livros=quantidade_livros,
        quantidade_autores=quantidade_autores,
        quantidade_categorias=quantidade_categorias
    )


# Página de cadastro
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    conexao = conectar_banco()

    # Busca os autores cadastrados
    autores = conexao.execute(
        "SELECT * FROM autores ORDER BY nome"
    ).fetchall()

    # Busca as categorias cadastradas
    categorias = conexao.execute(
        "SELECT * FROM categorias ORDER BY nome"
    ).fetchall()

    # Quando o formulário for enviado
    if request.method == "POST":

        titulo = request.form["titulo"]
        isbn = request.form["isbn"]
        ano = request.form["ano"]
        autor_id = request.form["autor_id"]
        categoria_id = request.form["categoria_id"]

        conexao.execute("""
            INSERT INTO livros
            (titulo, isbn, ano, autor_id, categoria_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            titulo,
            isbn,
            ano if ano else None,
            autor_id,
            categoria_id
        ))

        conexao.commit()
        conexao.close()

        # Depois de cadastrar, vai para o acervo
        return redirect(url_for("acervo"))

    conexao.close()

    return render_template(
        "cadastro.html",
        autores=autores,
        categorias=categorias
    )


# Página de consulta do acervo
@app.route("/acervo")
def acervo():

    conexao = conectar_banco()

    livros = conexao.execute("""
        SELECT
            livros.id,
            livros.titulo,
            livros.isbn,
            livros.ano,
            autores.nome AS autor,
            categorias.nome AS categoria

        FROM livros

        INNER JOIN autores
            ON livros.autor_id = autores.id

        INNER JOIN categorias
            ON livros.categoria_id = categorias.id

        ORDER BY livros.titulo
    """).fetchall()

    conexao.close()

    return render_template(
        "acervo.html",
        livros=livros
    )


# Inicia o servidor
if __name__ == "__main__":
    app.run(debug=True)
