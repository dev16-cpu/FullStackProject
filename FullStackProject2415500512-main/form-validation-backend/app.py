from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("name")
        mobile = request.form.get("mobile")
        password = request.form.get("password")

        errors = []

        if not username or len(username) < 5:
            errors.append("Username must be at least 5 characters long.")

        if not mobile or len(mobile) < 10:
            errors.append("Mobile number must be at least 10 characters long.")

        if not password or len(password) < 8:
            errors.append("Password must be at least 8 characters long.")

        if errors:
            return "<br>".join(errors)
        else:
            # return "Registration successful!"
            return render_template("login.html", name=username)
    return render_template("form.html")


app.run(debug=True)
