from flask import Flask, render_template
from list_st import fetch_list_of_students

app = Flask(__name__)

@app.route("/")
def root_route():
	return "Root route"


@app.route("/hit")
def get_student():
	return "Rishab"


@app.route("/students")
def html_test():
	list_of_students = fetch_list_of_students()
	return render_template("jinja_1501.html", los=list_of_students)

def fetch_list_of_students():
	return ["student1", "student2", "student3"]
print(fetch_list_of_students)

if __name__ == "__main__":
	app.run(debug=True)