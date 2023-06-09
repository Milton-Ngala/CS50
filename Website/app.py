import os
from cs50 import SQL
from flask import Flask, redirect, render_template, request, url_for, session, jsonify
from flask_session import Session
from flask_mail import Mail, Message
import csv 
from dotenv import load_dotenv

app = Flask(__name__) 
app.debug = True
db = SQL("sqlite:///shows.db")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

load_dotenv()

sender = os.getenv("MAIL_DEFAULT_SENDER")
password = os.getenv("MAIL_PASSWORD")
username = os.getenv("MAIL_USERNAME")

app.config["MAIL_DEFAULT_SENDER"] = sender
app.config["MAIL_PASSWORD"] = password
app.config["MAIL_PORT"] = 587
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = username

mail = Mail(app)

REGISTRANTS = {}

SPORTS = [
    "Football",
    "Basketball",
    "Volleyball",
    "Mathletics"    
]


@app.route("/")
def index():
    if not session.get("name"):
        return redirect("/login")
    return render_template("index.html")
    # return render_template("search.html", name=request.args.get("name", "there!")) 

@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        if request.form.get("sport") not in SPORTS:
            return render_template("failure.html", sport=request.form.get("sport"))
        email = request.form.get("email")
        sport = request.form.get("sport")
        REGISTRANTS[email] = sport
        with open("registrants.csv", "a", newline="") as csvfile:
            # csvfile.seek(0)
            writer = csv.writer(csvfile)
            if REGISTRANTS:
                for email, sport in REGISTRANTS.items():
                    writer.writerow([email, sport])
        
        # db.execute("INSERT INTO registrants (name, sport) VALUES (?, ?)",email, sport)        
        
        message = Message(f"Dear {email},Your registration to the {sport} club was successful", recipients=[email])
        message.body = "Congratulations! you have managed to send an email via google smtp server. This is a milestone in your developers journey. Mark this day on your calendar!."
        mail.send(message)
        
        return redirect("/registrants")
    if request.method == 'GET':
        return render_template("register.html", sports=SPORTS)

@app.route("/registrants")
def registrants():
    with open("registrants.csv", "r", newline="") as csvfile:
            reader = csv.reader(csvfile)
            registrants = {row[0]: row[1] for row in reader}
    return render_template("registrants.html", registrants=registrants)
            
@app.route("/login", methods=['POST', 'GET'])
def login_handler():
    if request.method == "POST":
        name = request.form.get("username") 
        session["name"] = request.form.get("username")
        return redirect("/")
    return render_template("login.html")

@app.route("/logout", methods=['POST', 'GET'])
def logout_handler():
    session["name"] = None 
    return redirect("/")

@app.route("/store", methods=['POST', 'GET'])
def store():
    books = db.execute("SELECT * FROM books")
    return render_template("books.html", books=books)

@app.route("/store/cart", methods=['POST', 'GET'])
def cart_handler():
    # Ensure cart exists
    if "cart" not in session:
        session["cart"] = []

    # POST
    if request.method == 'POST':
        id = request.form.get("id")
        if id not in session["cart"]: 
            session["cart"].append(id)
        return redirect("/store/cart")
    
    #GET 
    books = db.execute("SELECT * FROM books WHERE id IN (?)", session["cart"])
    return render_template("cart.html", books=books)

@app.route("/delete_item", methods=['POST'])
def remove_from_cart():
    id = request.form.get("id")
    print(id)
    print(session["cart"])
    if id in session["cart"]:
        session["cart"].remove(id)
    print(id)
    print(session["cart"])
    return redirect("/store/cart")

@app.route("/search", methods=["GET", "POST"])
def movie_search_handler():
    # db.execute("CREATE INDEX idx_shows_title ON shows (title)")
    if len(request.args.get("q")) < 3:
        shows = []
    else:
        shows = db.execute("SELECT * FROM shows INDEXED BY idx_shows_title WHERE title LIKE ? LIMIT ?", "%" + request.args.get("q") + "%", 30)
    return jsonify(shows)
    
if __name__ == "__main__":
    app.run(debug=True)