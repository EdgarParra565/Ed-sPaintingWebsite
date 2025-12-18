from flask import Flask
from flask import session, flash, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
import smtplib
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email



app = Flask(__name__)
csrf = CSRFProtect(app)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(basedir, "inquiries.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())

class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    message = TextAreaField("Message", validators=[DataRequired()])


def send_email(inquiry):
    server = os.getenv("MAIL_SERVER")
    port = int(os.getenv("MAIL_PORT"))
    username = os.getenv("MAIL_USERNAME")
    password = os.getenv("MAIL_PASSWORD")
    recipient = os.getenv("MAIL_TO")

    subject = "New Website Inquiry"
    body = f"""
New inquiry received:

Name: {inquiry.name}
Email: {inquiry.email}

Message:
{inquiry.message}
"""

    message = f"Subject: {subject}\n\n{body}"

    with smtplib.SMTP(server, port) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.sendmail(username, recipient, message)


@app.route("/", methods=["GET", "POST"])
def index():
    form = ContactForm()

    if form.validate_on_submit():

        # Honeypot
        if request.form.get("company"):
            return redirect("/")

        inquiry = Inquiry(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )

        try:
            db.session.add(inquiry)
            db.session.commit()
            flash("Your message has been sent successfully!", "success")
        except Exception:
            db.session.rollback()
            flash("Something went wrong. Please try again.", "error")

        return redirect("/")

    return render_template("index.html", form=form)


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
