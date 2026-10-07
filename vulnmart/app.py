"""
VulnMart - An intentionally vulnerable e-commerce web app
Built as a training lab (Final Assignment - VaultofCodes - Custom Vulnerable Lab option)

WARNING: This application contains DELIBERATE security vulnerabilities.
Run locally only. Never deploy to a public server or use real data.

Vulnerabilities implemented (for educational demonstration):
  1. SQL Injection      - login form (string-concatenated query)
  2. Stored XSS          - product review comments (unsanitized output)
  3. IDOR                 - order details page (no ownership check)
  4. Weak Authentication - plaintext passwords, no rate limiting, predictable passwords
"""

import sqlite3
from flask import Flask, request, render_template, redirect, session, url_for, g, jsonify
from reliability_models import (
    JelinskiMorandaModel,
    SchumanModel,
    NelsonCorcoranModel,
)

app = Flask(__name__)
RELIABILITY_CONFIG = {
    "N0": 50,
    "phi": 0.0001,
    "I": 10000,
    "E0": 50,
    "Ks": 0.0001,
    "nelson_P": [0.6, 0.4],
    "nelson_n": [5, 2],
    "nelson_N": [100, 50],
    "corcoran_N0": 970,
    "corcoran_Ni": [20, 10],
    "corcoran_ai": [0.7, 0.3],
}
app.secret_key = "vulnmart-lab-secret-not-for-production"  # intentionally weak, static secret
DB = "vulnmart.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.executescript("""
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS reviews;
        DROP TABLE IF EXISTS orders;

        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL   -- VULNERABILITY: plaintext, no hashing
        );

        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT NOT NULL
        );

        CREATE TABLE reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            comment TEXT NOT NULL
        );

        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            shipping_address TEXT NOT NULL,
            card_last4 TEXT NOT NULL
        );
    """)

    # Seed users with weak, predictable passwords (mirrors the pattern from
    # the Recon -> Risk -> Report / Cracked Glass assignments in this same course)
    c.executemany(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        [
            ("admin", "password123"),
            ("sarah", "sarah1995"),
            ("devraj", "devraj_2001"),
        ],
    )

    c.executemany(
        "INSERT INTO products (name, price, description) VALUES (?, ?, ?)",
        [
            ("Mechanical Keyboard", 3499.00, "Hot-swappable, tactile brown switches."),
            ("Wireless Mouse", 899.00, "Silent click, 2.4GHz + Bluetooth."),
            ("USB-C Hub", 1299.00, "7-in-1, HDMI + SD card reader."),
        ],
    )

    c.executemany(
        "INSERT INTO orders (user_id, product_name, quantity, shipping_address, card_last4) VALUES (?, ?, ?, ?, ?)",
        [
            (1, "Mechanical Keyboard", 1, "Admin HQ, Server Room 4, Mumbai", "4242"),
            (2, "Wireless Mouse", 2, "Sarah's House, 12 Palm Street, Pune", "1881"),
            (3, "USB-C Hub", 1, "Devraj's Flat, 9th Floor, Bengaluru", "5566"),
        ],
    )

    conn.commit()
    conn.close()


@app.route("/")
def index():
    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()
    return render_template("index.html", products=products, user=session.get("username"))


# ------------------------------------------------------------------
# VULNERABILITY 1 + 4: SQL Injection + Weak Authentication
# The query below concatenates raw user input directly into SQL.
# A username like:   admin' --
# with ANY password bypasses authentication entirely, because the
# trailing "--" comments out the password check.
# There is also no rate limiting, so this endpoint is brute-forceable.
# ------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        # INTENTIONALLY VULNERABLE: string-concatenated SQL query
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        try:
            user = db.execute(query).fetchone()
        except sqlite3.OperationalError:
            user = None

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
        else:
            error = "Invalid credentials."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ------------------------------------------------------------------
# VULNERABILITY 2: Stored XSS
# Review comments are inserted into the page via the |safe filter,
# meaning any HTML/JS a user submits is rendered as-is for every
# visitor who views that product page.
# ------------------------------------------------------------------
@app.route("/product/<int:product_id>", methods=["GET"])
def product_detail(product_id):
    db = get_db()
    product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if product is None:
        return render_template("not_found.html", item="product"), 404
    reviews = db.execute("SELECT * FROM reviews WHERE product_id = ?", (product_id,)).fetchall()
    return render_template("product.html", product=product, reviews=reviews, user=session.get("username"))


@app.route("/product/<int:product_id>/review", methods=["POST"])
def add_review(product_id):
    db = get_db()
    username = session.get("username", "Guest")
    comment = request.form["comment"]  # not sanitized, not escaped on output either
    db.execute(
        "INSERT INTO reviews (product_id, username, comment) VALUES (?, ?, ?)",
        (product_id, username, comment),
    )
    db.commit()
    return redirect(url_for("product_detail", product_id=product_id))


# ------------------------------------------------------------------
# VULNERABILITY 3: Insecure Direct Object Reference (IDOR)
# Any logged-in user can view ANY order by guessing/incrementing the
# ID in the URL. There is no check that order.user_id == session user.
# ------------------------------------------------------------------
@app.route("/orders")
def my_orders():
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    orders = db.execute("SELECT * FROM orders WHERE user_id = ?", (session["user_id"],)).fetchall()
    return render_template("orders.html", orders=orders, user=session.get("username"))


@app.route("/order/<int:order_id>")
def order_detail(order_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    # VULNERABLE: no WHERE user_id = session['user_id'] check
    order = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    status = 200 if order is not None else 404
    return render_template("order_detail.html", order=order, user=session.get("username")), status


@app.route("/reliability", methods=["GET"])
def reliability_report():
    """
    Calculate software reliability using all three models.
    """

    t = request.args.get("t", default=100, type=float)
    i = request.args.get("i", default=30, type=int)
    Ec = request.args.get("Ec", default=30, type=int)

    # Jelinski-Moranda model
    jm = JelinskiMorandaModel(
        N0=RELIABILITY_CONFIG["N0"],
        phi=RELIABILITY_CONFIG["phi"],
    )

    # Schuman model
    sch = SchumanModel(
        I=RELIABILITY_CONFIG["I"],
        E0=RELIABILITY_CONFIG["E0"],
        Ks=RELIABILITY_CONFIG["Ks"],
    )

    # Nelson-Corcoran model
    nc = NelsonCorcoranModel(
        P=RELIABILITY_CONFIG["nelson_P"],
        n=RELIABILITY_CONFIG["nelson_n"],
        N=RELIABILITY_CONFIG["nelson_N"],
        N0=RELIABILITY_CONFIG["corcoran_N0"],
        Ni=RELIABILITY_CONFIG["corcoran_Ni"],
        ai=RELIABILITY_CONFIG["corcoran_ai"],
    )

    result = {
        "time_hours": t,
        "corrected_errors": i,

        "jelinski_moranda": {
            "R": round(jm.reliability(t, i), 4),
            "MTTF": round(jm.mttf(i), 2),
            "lambda": round(jm.failure_intensity(i), 6),
        },

        "schuman": {
            "R": round(sch.reliability(t, Ec), 8),
            "MTTF": round(sch.mttf(Ec), 0),
            "lambda": round(sch.failure_intensity(Ec), 8),
        },

        "nelson_corcoran": {
            "R_nelson": round(nc.reliability_nelson(), 4),
            "R_corcoran": round(nc.reliability_corcoran(), 4),
            "R_simple": round(nc.reliability_simple(), 4),
        },
    }

    return jsonify(result)


if __name__ == "__main__":
    import os

    if not os.path.exists(DB):
        init_db()

    # This application is intentionally vulnerable for educational use.
    app.run(host="0.0.0.0", port=5055, debug=False)

if __name__ == "__main__":

    import os
    if not os.path.exists(DB):
        init_db()
    # Bound to localhost only. This app is unsafe by design and must never
    # be reachable from another machine on the network.
    app.run(host="0.0.0.0", port=5055, debug=False)
