from flask import Flask, render_template, request, redirect, session
from database import db, init_db
from models import User, Product
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "mysupersecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gadgethub.db"
db.init_app(app)

@app.before_first_request
def setup():
    init_db(app)

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect("/dashboard")
        return render_template("login.html", error="Invalid login")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/dashboard")
def dashboard():
    products = Product.query.all()
    product_names = [p.name for p in products]
    product_stock = [p.stock for p in products]
    return render_template("dashboard.html",
                           product_names=product_names,
                           product_stock=product_stock)

@app.route("/products")
def view_products():
    products = Product.query.all()
    return render_template("products.html", products=products)

@app.route("/products/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        product = Product(
            name=request.form["name"],
            description=request.form["description"],
            price=float(request.form["price"]),
            stock=int(request.form["stock"])
        )
        db.session.add(product)
        db.session.commit()
        return redirect("/products")

    return render_template("add_product.html")

@app.route("/products/edit/<int:id>", methods=["GET", "POST"])
def edit_product(id):
    product = Product.query.get(id)
    if request.method == "POST":
        product.name = request.form["name"]
        product.description = request.form["description"]
        product.price = float(request.form["price"])
        product.stock = int(request.form["stock"])
        db.session.commit()
        return redirect("/products")

    return render_template("edit_product.html", product=product)

@app.route("/products/delete/<int:id>")
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return redirect("/products")

if __name__ == "__main__":
    app.run(debug=True)
