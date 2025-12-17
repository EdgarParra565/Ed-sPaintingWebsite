from flask import Flask
from flask import session, flash, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
import smtplib


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "SQLALCHEMY_DATABASE_URI", "sqlite:///inquiries.db"
)
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

        # Spam honeypot check (used later)
        if request.form.get("company"):
            return redirect("/")

        inquiry = Inquiry(
            name=request.form["name"],
            email=request.form["email"],
            message=request.form["message"]
        )

        try:
            db.session.add(inquiry)
            db.session.commit()
            send_email(inquiry)
            flash("Your message has been sent successfully!", "success")
        except Exception:
            db.session.rollback()
            flash("Something went wrong. Please try again.", "error")

        return redirect("/")

    return render_template("index.html")


@app.route("/delete/<int:inquiry_id>", methods=["POST"])
def delete_inquiry(inquiry_id):
    if not session.get("admin_logged_in"):
        return redirect("/login")

    inquiry = Inquiry.query.get_or_404(inquiry_id)
    db.session.delete(inquiry)
    db.session.commit()

    flash("Inquiry deleted", "success")
    return redirect("/admin")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if (
            request.form["username"] == os.getenv("ADMIN_USER")
            and request.form["password"] == os.getenv("ADMIN_PASSWORD")
        ):
            session["admin_logged_in"] = True
            return redirect("/admin")

        flash("Invalid credentials", "error")

    return render_template("login.html")


@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect("/login")

    inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).all()
    return render_template("admin.html", inquiries=inquiries)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
