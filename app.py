from flask import Flask, redirect, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'aP3R$!x9_SecretKey123'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= MODEL (TABEL) =================
class Rapor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    kelas = db.Column(db.String(50), nullable=False)
    tahun = db.Column(db.Integer, nullable=False)
    rata_rata = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(2), nullable=False)
    status = db.Column(db.String(20), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/', methods =['GET', 'POST'])
def home():
    a = b = c = None
    if request.method == 'POST':
        a = str(request.form['a'])
        b = int(request.form['b'])
        c = str(request.form['c'])

    return render_template('index.html', a=a, b=b, c=c)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/service')
def service():
    return render_template('service.html')

@app.route('/calculator',  methods=['GET', 'POST'])
def calculator():
    display = ""
    if request.method == 'POST':
        display = request.form.get('display', '')
        btn = request.form.get('btn')

        if btn == 'C':
            display = ""
        
        elif btn == '⌫':
            display = display[:-1]
        
        elif btn == '=':
            try:
                if '²' in display:
                    num = float(display.replace('²', ''))
                    display = str(num ** 2)
                else:
                    display = str(eval(display))
            except:
                display = "Error"
        
        elif btn == '^':
            display += '**'
        
        elif btn == '%':
            display += '/100'

        else:
            display += btn
    return render_template('calculator.html', display=display)

@app.route('/rapor', methods=['GET', 'POST'])
def rapor():
    a = b = None
    c = None
    rata_rata = None
    status = ""
    grade = ""
    nilai = []
    sekolah = "SMP 7 Jayakarta"

    if request.method == 'POST':
        a = request.form['a']
        b = request.form['b']
        c = int(request.form['c'])

        nilai = list(map(int, request.form.getlist('nilai[]')))
        rata_rata = sum(nilai) / len(nilai)

        if rata_rata >= 90:
            grade, status = "A", "Lulus"
        elif rata_rata >= 80:
            grade, status = "B", "Lulus"
        elif rata_rata >= 75:
            grade, status = "C", "Lulus"
        else:
            grade, status = "D", "Tidak Lulus"

        data = Rapor(
            nama=a,
            kelas=b,
            tahun=c,
            rata_rata=rata_rata,
            grade=grade,
            status=status
        )
        db.session.add(data)
        db.session.commit()

    return render_template('rapor.html', a=a, b=b, c=c, status=status,rata_rata=rata_rata,nilai=nilai,sekolah=sekolah,grade=grade)
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        password_hash = generate_password_hash(request.form['password'])

        user = User(
            email = request.form['email'],
            phone = request.form['phone'],
            username = request.form['username'],
            password = password_hash
        )

        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        except:
            db.session.rollback()
            return"Username sudah digunakan"
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username = request.form['username']
        ).first()

        if user and check_password_hash(user.password, request.form['password']):
            session['user'] = user.username
            return redirect('/dashboard')
        
        return "Username atau password salah"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html', user=session['user'])




@app.route('/konversi', methods=['GET', 'POST'])
def konversi():
    a = None
    status = ""
    operator = ""
    b = c = d = None

    if request.method == 'POST':
        a = float(request.form['a'])
        operator = request.form['operator']

        match operator :
            case 'farenheit':
                celsius = (a - 32) * 5 / 9
            case 'celsius':
                celsius = a
            case 'reamur':
               celsius = a * 5 / 4
            case 'kelvin':
               celsius = a - 273.15
            case _:
                celsius = 0
        
        farenheit = (celsius * 9/5) + 32
        reamur    = celsius * 4/5
        kelvin    = celsius + 273.15

        match operator:
            case 'celsius':
                b, c, d = farenheit, reamur, kelvin
            case 'farenheit':
                b, c, d = celsius, reamur, kelvin
            case 'reamur':
                b, c, d = celsius, farenheit, kelvin
            case 'kelvin':
                b, c, d = celsius, farenheit, reamur

        if operator == 'farenheit' and a > 90:
            status = 'Panas'
        elif operator == 'farenheit' and a < 60:
            status = 'Dingin'
        elif operator == 'celsius' and a > 35:
            status = 'Panas'
        elif operator == 'celsius' and a < 10:
            status = 'Dingin'
        elif operator == 'reamur' and a > 27:
            status = 'Panas'
        elif operator == 'reamur' and a < 10:
            status = 'Dingin'
        elif operator == 'kelvin' and a > 310:
            status = 'Panas'
        elif operator == 'kelvin' and a < 285:
            status = 'Dingin'
        else:
            status = 'Normal'

    return render_template('konversi.html', a=a, status=status, b=b, c=c, d=d)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
