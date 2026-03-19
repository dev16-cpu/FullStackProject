from flask import Flask, render_template

from form import RegisterForm


app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data

        # Here you would typically save the user to the database
        return f"Registration successful for {username} with email {email}!"
    return render_template("register.html", form=form)


app.run(debug=True)
