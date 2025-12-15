from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import smtplib

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inquiries.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        inquiry = Inquiry(
            name=request.form["name"],
            email=request.form["email"],
            message=request.form["message"]
        )
        db.session.add(inquiry)
        db.session.commit()
        send_email(inquiry)
        return redirect("/")
    return render_template("index.html")


def send_email(inquiry):
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        server.sendmail(
            os.getenv("EMAIL_USER"),
            os.getenv("EMAIL_USER"),
            f"""New Inquiry

Name: {inquiry.name}
Email: {inquiry.email}

Message:
{inquiry.message}
"""
        )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)