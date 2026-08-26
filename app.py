import json
import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "requests.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key"


def get_database():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_database() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS course_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                student_name TEXT NOT NULL,
                department TEXT NOT NULL,
                requested_date TEXT NOT NULL,
                courses TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


initialize_database()


@app.route("/", methods=["GET", "POST"])
def course_request():
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        student_name = request.form.get("student_name", "").strip()
        department = request.form.get("department", "").strip()
        requested_date = request.form.get("requested_date", "")
        course_titles = request.form.getlist("course_title[]")
        course_sections = request.form.getlist("course_section[]")

        courses = [
            {"title": title.strip(), "section": section.strip()}
            for title, section in zip(course_titles, course_sections)
            if title.strip()
        ]

        if not all([student_id, student_name, department, requested_date]) or not courses:
            flash("Complete all required fields and add at least one course title.", "error")
            return render_template("index.html", today=date.today().isoformat())

        with get_database() as connection:
            connection.execute(
                """
                INSERT INTO course_requests
                    (student_id, student_name, department, requested_date, courses)
                VALUES (?, ?, ?, ?, ?)
                """,
                (student_id, student_name, department, requested_date, json.dumps(courses)),
            )

        flash("Your course request has been submitted.", "success")
        return redirect(url_for("course_request"))

    return render_template("index.html", today=date.today().isoformat())


if __name__ == "__main__":
    app.run(debug=True)