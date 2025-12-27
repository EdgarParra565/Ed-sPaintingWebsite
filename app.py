from functools import wraps
from threading import Thread

from flask import Flask, session, flash, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Email
from datetime import datetime
from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import check_password_hash

from estimatePredictionTool import PaintEstimator, EpoxyEstimator

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

# -----------------------------
# Flask & Config
# -----------------------------
app = Flask(__name__)
csrf = CSRFProtect(app)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")
basedir = os.path.abspath(os.path.dirname(__file__))
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is not set")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# -----------------------------
# Database
# -----------------------------
# Replace your database initialization section with this:
try:
    db = SQLAlchemy(app)


    class Inquiry(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), nullable=False)
        message = db.Column(db.Text, nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.now)


    # Initialize database tables
    def init_db():
        try:
            with app.app_context():
                db.create_all()
                print("Database tables created successfully")
        except Exception as e:
            print(f"Database initialization error: {e}")


    init_db()

except Exception as e:
    print(f"Database setup error: {e}")
    raise

init_db()
# -----------------------------
# Contact Form
# -----------------------------
class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    message = TextAreaField("Message", validators=[DataRequired()])

# -----------------------------
# Admin Login Form
# -----------------------------
class AdminLoginForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])

# -----------------------------
# Rate Limiter
# -----------------------------
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# -----------------------------
# Helper Functions
# -----------------------------
@app.route("/admin")
def admin_redirect():
    return redirect("/admin/login")


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect("/admin/login")  # redirect to login page
        return f(*args, **kwargs)
    return decorated

@app.route("/admin/inquiries")
@admin_required
def admin_inquiries():
    try:
        inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(100).all()
        return render_template("admin_inquiries.html", inquiries=inquiries)
    except Exception as e:
        app.logger.error(f"Error fetching inquiries: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        flash("Error loading inquiries. Please check the logs.", "error")
        return render_template("admin_inquiries.html", inquiries=[])

# Changed to this email now
def send_email_async(inquiry_data):
    """Pass inquiry data as dict instead of SQLAlchemy object"""
    Thread(target=send_email, args=(inquiry_data,)).start()


def send_email(inquiry_data):
    """inquiry_data is a dict with name, email, message"""
    try:
        server = os.getenv("MAIL_SERVER")
        port = int(os.getenv("MAIL_PORT", "0"))
        username = os.getenv("MAIL_USERNAME")
        password = os.getenv("MAIL_PASSWORD")
        to_email = os.getenv("MAIL_TO")

        # Log configuration (without password)
        app.logger.info(f"Email config - Server: {server}, Port: {port}, Username: {username}, To: {to_email}")

        if not all([server, port, username, password, to_email]):
            app.logger.warning(
                f"Email not configured - Missing: server={bool(server)}, port={bool(port)}, username={bool(username)}, password={bool(password)}, to_email={bool(to_email)}")
            return

        msg = EmailMessage()
        msg["Subject"] = "New Website Contact Inquiry"
        msg["From"] = username
        msg["To"] = to_email
        msg["Reply-To"] = inquiry_data['email']
        msg.set_content(
            f"Name: {inquiry_data['name']}\n"
            f"Email: {inquiry_data['email']}\n\n"
            f"{inquiry_data['message']}"
        )

        app.logger.info(f"Attempting to send email to {to_email}...")

        with smtplib.SMTP(server, port, timeout=10) as smtp:
            smtp.starttls()
            app.logger.info("TLS started")
            smtp.login(username, password)
            app.logger.info("Login successful")
            smtp.send_message(msg)
            app.logger.info(f"Email sent successfully to {to_email}")

    except Exception as e:
        app.logger.error(f"Email error: {e}")
        import traceback
        app.logger.error(traceback.format_exc())

# -----------------------------
# Routes
# -----------------------------

@app.route("/", methods=["GET", "POST"])
@limiter.limit("60 per minute")
def index():
    form = ContactForm()
    if form.validate_on_submit():
        # Honeypot
        if request.form.get("company", "").strip():
            return redirect("/")

        inquiry = Inquiry(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )

        try:
            db.session.add(inquiry)
            db.session.commit()

            # Pass data as dict instead of SQLAlchemy object
            inquiry_data = {
                'name': inquiry.name,
                'email': inquiry.email,
                'message': inquiry.message
            }

            try:
                send_email_async(inquiry_data)  # ← NOW PASSING DICT
            except Exception as e:
                app.logger.error(f"Email failed: {e}")

            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Database error: {e}")
            flash("Something went wrong. Please try again.", "error")

        return redirect("/")

    return render_template("index.html", form=form)

@app.route("/admin/login", methods=["GET", "POST"])
@limiter.limit("10 per 15 minutes")
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        password = form.password.data
        admin_hash = os.getenv("ADMIN_PASSWORD_HASH")
        if not admin_hash:
            flash("Admin login not configured", "danger")
            return redirect("/admin/login")

        if check_password_hash(admin_hash, password):
            session["admin_logged_in"] = True
            return redirect("/admin/inquiries")
        flash("Invalid password", "danger")
        return redirect("/admin/login")
    return render_template("admin_login.html", form=form)


@app.route("/admin/delete/<int:inquiry_id>", methods=["POST"])
@admin_required
def delete_inquiry(inquiry_id):
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    db.session.delete(inquiry)
    db.session.commit()
    flash("Inquiry deleted successfully.", "success")
    return redirect("/admin/inquiries")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect("/admin/login")


# -----------------------------
# Error Handlers
# -----------------------------
@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template("rate_limit.html"), 429

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# -----------------------------
# Gallery & Estimate Routes
# -----------------------------
@app.route("/gallery/painting")
def painting_gallery():
    return render_template("painting_gallery.html")

@app.route("/gallery/epoxy")
def epoxy_gallery():
    return render_template("epoxy_gallery.html")

@app.route("/estimate", methods=["GET", "POST"])
def estimate():
    estimate_result = None
    custom_message = ""
    selected_service = "painting"

    if request.method == "POST":
        selected_service = request.form.get("service_type", "painting")

        if selected_service == "painting":
            paint = PaintEstimator()
            length = float(request.form.get("length", 0))
            width = float(request.form.get("width", 0))
            full_repaint = request.form.get("full_repaint") == "yes"
            paint_ceiling = request.form.get("paint_ceiling") == "yes"
            ceiling_repaint = request.form.get("ceiling_repaint") == "yes"
            baseboards = request.form.get("baseboards") == "yes"
            crown = request.form.get("crown") == "yes"
            paint.estimate_walls(length, width, full_repaint)
            paint.estimate_ceiling(paint_ceiling, ceiling_repaint)
            paint.estimate_trim(baseboards, crown)
            estimate_result = paint.total()

        elif selected_service == "epoxy":
            length = float(request.form.get("length", 0))
            width = float(request.form.get("width", 0))
            epoxy_type = request.form.get("floor_type", "solid")
            epoxy = EpoxyEstimator()
            epoxy.estimate_floor(length, width, epoxy_type)
            estimate_result = epoxy.total()
            custom_message = getattr(epoxy, "custom_message", "")

    return render_template(
        "estimate.html",
        estimate=estimate_result,
        message=custom_message,
        selected_service=selected_service,
        floor_type_selected=request.form.get("floor_type", "color"),
        height_value=request.form.get("height", ""),
        full_repaint_value=request.form.get("full_repaint", "no"),
        paint_ceiling_value=request.form.get("paint_ceiling", "no"),
        ceiling_repaint_value=request.form.get("ceiling_repaint", "no"),
        baseboards_value=request.form.get("baseboards", "no"),
        crown_value=request.form.get("crown", "no"),
    )


# -----------------------------
# Health
# -----------------------------
@app.route("/health")
def health_check():
    return {"status": "healthy"}, 200

# -----------------------------
# Main
# -----------------------------
# Put at creation of db now
"""
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    """
    # No app.run() here — WSGI server (Waitress) will run the app

