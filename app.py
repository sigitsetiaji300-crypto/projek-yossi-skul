from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import os

app = Flask(__name__)

DATABASE = "tmp/database.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS anggota (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            nis TEXT NOT NULL,
            kelas TEXT NOT NULL,
            jenis_kelamin TEXT NOT NULL,
            ekstrakurikuler TEXT NOT NULL,
            kategori TEXT NOT NULL,
            no_hp TEXT
        )
    """)

    conn.commit()
    conn.close()



@app.route("/")
def index():
    db = get_db()

    anggota = db.execute(
        "SELECT * FROM anggota ORDER BY id DESC"
    ).fetchall()

    total = len(anggota)

    jumlah_ekskul = db.execute(
        "SELECT COUNT(DISTINCT ekstrakurikuler) FROM anggota"
    ).fetchone()[0]

    data_ekskul = db.execute("""
        SELECT ekstrakurikuler, COUNT(*) AS jumlah
        FROM anggota
        GROUP BY ekstrakurikuler
        ORDER BY jumlah DESC
    """).fetchall()

    jumlah_per_ekskul = {
        row["ekstrakurikuler"]: row["jumlah"]
        for row in data_ekskul
    }

    return render_template(
        "index.html",
        anggota=anggota,
        total=total,
        jumlah_ekskul=jumlah_ekskul,
        jumlah_per_ekskul=jumlah_per_ekskul
    )

@app.route("/tambah", methods=["GET", "POST"])
def tambah():
    if request.method == "POST":
        nama = request.form["nama"]
        nis = request.form["nis"]
        kelas = request.form["kelas"]
        jenis_kelamin = request.form["jenis_kelamin"]
        ekstrakurikuler = request.form["ekstrakurikuler"]
        kategori = request.form["kategori"]
        no_hp = request.form["no_hp"]

        conn = get_db()

        conn.execute("""
            INSERT INTO anggota
            (nama, nis, kelas, jenis_kelamin,
             ekstrakurikuler, kategori, no_hp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            nama,
            nis,
            kelas,
            jenis_kelamin,
            ekstrakurikuler,
            kategori,
            no_hp
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("tambah.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()

    data = conn.execute(
        "SELECT * FROM anggota WHERE id = ?",
        (id,)
    ).fetchone()

    if not data:
        conn.close()
        return "Data tidak ditemukan", 404

    if request.method == "POST":
        nama = request.form["nama"]
        nis = request.form["nis"]
        kelas = request.form["kelas"]
        jenis_kelamin = request.form["jenis_kelamin"]
        ekstrakurikuler = request.form["ekstrakurikuler"]
        kategori = request.form["kategori"]
        no_hp = request.form["no_hp"]

        conn.execute("""
            UPDATE anggota SET
                nama = ?,
                nis = ?,
                kelas = ?,
                jenis_kelamin = ?,
                ekstrakurikuler = ?,
                kategori = ?,
                no_hp = ?
            WHERE id = ?
        """, (
            nama,
            nis,
            kelas,
            jenis_kelamin,
            ekstrakurikuler,
            kategori,
            no_hp,
            id
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    conn.close()

    return render_template("edit.html", data=data)


@app.route("/hapus/<int:id>")
def hapus(id):
    conn = get_db()

    conn.execute(
        "DELETE FROM anggota WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


@app.route("/download")
def download():
    return send_file(
        __file__,
        as_attachment=True,
        download_name="app.py"
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5050)