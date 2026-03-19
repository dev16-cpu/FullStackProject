from flask import Flask, render_template
from model.users import Users
from model.users import db

from form import RegisterForm


app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key_here"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:Nopassword%4003@localhost/test"
)
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        user = Users(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return render_template(
            "login.html", message="Registration successful! Please log in."
        )
    return render_template("register.html", form=form)


@app.route("/login")
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
