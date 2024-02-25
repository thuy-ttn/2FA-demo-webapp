from flask import Flask, render_template, request, session, jsonify, make_response, redirect
from werkzeug.security import check_password_hash
import qrcode
from base64 import b64encode
from secrets import SystemRandom
from io import BytesIO
from utils import get_db, verify

app = Flask(__name__)
app.secret_key = "super secret key"

@app.route('/home')
def home():
    return render_template("home.html")

@app.route("/")
def index():
    """
    index() renders the landing page of the application.
    """

    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    """
    Log in a registered user by adding the username to the session.
    """

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        db.close()

        if user is None or not check_password_hash(user["password"], password):
            error = "Incorrect username or password."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["username"] = user["username"]
            session["enable_2FA"] = user["enable_2FA"]
            return make_response(jsonify(error=error, id=user["id"], enable_2FA=user["enable_2FA"]), 200)
        else:
            return make_response(jsonify(error=error), 400)


@app.route("/logout")
def logout():
    """
    Clear the current session, including the stored user id.
    """

    session.clear()
    return redirect("/")

@app.route("/register-2fa", methods=["POST"])
def register_2fa():
    """
    Generate QR code for 2FA
    """

    if request.method == "POST":
        username = request.form["username"]

        #generate a random base32 key with length 32
        chars = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")
        key = "".join(SystemRandom().choice(chars) for _ in range(32))
        #update to db
        db = get_db()
        db.execute("UPDATE users SET enable_2FA = ?, secret_key = ? WHERE username = ?", (1, key, username))
        db.commit()
        db.close()

        #generate QR
        base_uri = "otpauth://{0}/2FAWebApp:{1}?secret={2}&issuer=2FAWebApp"
        uri = base_uri.format("totp", username, key)
        img = qrcode.make(uri)
        # Convert the PNG image to bytes
        img_bytes_io = BytesIO()
        img.save(img_bytes_io)
        img_bytes = img_bytes_io.getvalue()
        # Base64 encode the image bytes
        base64_encoded_img = b64encode(img_bytes).decode('utf-8')

        return make_response(jsonify(img=base64_encoded_img), 200)
    

@app.route("/verify-2fa", methods=["POST"])
def verify_2fa():
    """
    Verify OTP
    """

    if request.method == "POST":
        username = session["username"]
        otp = request.form["otp"]

        #get user secret key
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if user:
            secret_key = user[4]
            #verify OTP
            if verify(otp, secret_key) :
                return make_response(jsonify(status="success"), 200)
            else:
                return make_response(jsonify(status="fail"), 200)