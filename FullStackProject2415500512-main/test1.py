from flask import Flask, render_template

app = Flask(__name__)

@app.route("/hit")
def get_student():
	return "Rishab"


@app.route("/html")
def html_test():
	name = "Rishab"
	return render_template("test.html", name=name )

if __name__ == "__main__":
	app.run()