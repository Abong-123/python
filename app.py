#================== IMPORT ============================
from flask import Flask, redirect, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from werkzeug.utils import secure_filename
from datetime import date, timedelta

#======================= STARTED ======================
app = Flask(__name__)
app.secret_key = 'aP3R$!x9_SecretKey123'


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/profile/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
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

class Kasir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(50), nullable=False)
    code = db.Column(db.Integer, nullable=False)
    harga = db.Column(db.Integer, nullable=False)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    instagram = db.Column(db.String(50), nullable=False)
    facebook = db.Column(db.String(50), nullable=False)
    foto = db.Column(db.String(200), nullable=True)

class Hidroponik(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    jenis = db.Column(db.String(30), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)

    tanggal_tanam = db.Column(db.Date, nullable=False)
    lama_panen = db.Column(db.Integer, nullable=False)
    tanggal_panen = db.Column(db.Date, nullable=False)

    ganti_pupuk = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

#==================== FUNCTION ==========================
FILE = "todo.json"
def load_tasks():
    if not os.path.exists(FILE):
        return[]
    with open(FILE, "r") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(FILE, "w") as f:
        json.dump(tasks, f)


TANAMAN_FILE = "tanaman.json"
def load_tanaman():
    if not os.path.exists(TANAMAN_FILE):
        return []
    try:
        with open(TANAMAN_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_tanaman(data):
    with open(TANAMAN_FILE, "w") as f:
        json.dump(data, f)

def hitung_ganti_pupuk(jenis):
    if jenis == "daun":
        return 4
    elif jenis == "bunga":
        return 3
    elif jenis == "buah":
        return 2
    elif jenis == "flower":
        return 5
    return 4

def sisa_hari(tanggal_target):
    return(tanggal_target - date.today()).days

def sisa_ganti_pupuk(tanggal_tanam, interval):
    hari_berjalan = (date.today() - tanggal_tanam).days
    return interval - (hari_berjalan % interval)

#==================== ROUTING ==========================
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

@app.route('/kasir', methods=['GET', 'POST'])
def kasir():

    if 'cart' not in session:
        session['cart'] = []
    
    cart = session['cart']
    pesan = None
    if request.method == 'POST':
        action = request.form.get('action')

        match action:
            case 'more':
                code = int(request.form['id'])
                qty = int(request.form['jumlah'])

                barang = Kasir.query.filter_by(code=code).first()

                if not barang:
                    pesan = 'Barang tidak ditemukan'
                else:
                    ditemukan = False
                
                    for item in cart:
                        if item['code'] == code:
                            item['qty'] += qty
                            item['total'] = item['qty'] * item['harga']
                            ditemukan = True
                            break

                    if not ditemukan:
                        cart.append({
                            'code': barang.code,
                            'barang': barang.nama,
                            'harga': barang.harga,
                            'qty': qty,
                            'total': barang.harga * qty
                        })
                    session['cart'] = cart
                    pesan = 'barang ditambahkan ke keranjang'

            case 'hapus':
                code = int(request.form['code'])
                cart = [item for item in cart if item['code'] != code]
                session['cart'] = cart

            
            case 'tambah':
                barang = Kasir(
                    nama = request.form['barang'],
                    code = request.form['code'],
                    harga = request.form['harga']
                )
                db.session.add(barang)
                db.session.commit()
                pesan = 'Barang berhasil ditambahkan ke database'
            
            case 'beli':
                session.pop('cart', None)
                pesan = 'Checkout Berhasil'
    
    grand_total = sum(item['total'] for item in cart)

    return render_template('kasir.html', cart=cart,grand_total=grand_total,pesan=pesan)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    profile = Profile.query.first()
    if request.method == 'POST':
        nama = request.form['nama']
        phone = request.form['phone']
        email = request.form['email']
        instagram = request.form['instagram']
        facebook = request.form['facebook']

        foto = request.files.get('foto')
        filename = None

        if foto and foto.filename != '':
            filename = secure_filename(foto.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # hapus foto lama
            if profile and profile.foto:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], profile.foto)
                if os.path.exists(old_path):
                    os.remove(old_path)

            foto.save(path)

        if profile:
            # UPDATE
            profile.nama = nama
            profile.phone = phone
            profile.email = email
            profile.instagram = instagram
            profile.facebook = facebook
            if filename:
                profile.foto = filename
        else:
            # INSERT
            profile = Profile(
                nama=nama,
                phone=phone,
                email=email,
                instagram=instagram,
                facebook=facebook,
                foto=filename
            )
            db.session.add(profile)

        db.session.commit()

    return render_template('profile.html', profile=profile)

@app.route('/qrgen', methods=['GET', 'POST'])
def qrgen():
    qrimage = None
    if request.method == 'POST':
        qrcode = str(request.form['qrcode'])
        if qrcode == "":
            qrimage = "ERROR"
        else:
            qrimage = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=" + qrcode

    return render_template('qrgen.html', qrimage=qrimage)

@app.route('/todolist', methods=['GET', 'POST'])
def todolist():
    tasks = load_tasks()

    if request.method == 'POST':
        task = str(request.form['task'])

        if task:
            tasks.append(task)
            save_tasks(tasks)
        
        return redirect("/todolist")
    
    return render_template("todolist.html", tasks=tasks)

@app.route("/delete/<int:index>")
def delete(index):
    tasks = load_tasks()
    if index < len(tasks):
        tasks.pop (index)
        save_tasks(tasks)
    
    return redirect("/todolist")

@app.route('/hidroponik', methods=['GET', 'POST'])
def hidroponik():
    if request.method == 'POST':
        nama = str(request.form['tanaman'])
        jenis = request.form.get("jenis")
        jumlah = int(request.form.get("jumlah", 1))
        lama_panen = int(request.form.get("panen"))

        tanggal_tanam = date.today()
        tanggal_panen = tanggal_tanam + timedelta(days=lama_panen)
        ganti_pupuk = hitung_ganti_pupuk(jenis)

        data = Hidroponik(
            nama = nama,
            jenis=jenis,
            jumlah=jumlah,
            tanggal_tanam = tanggal_tanam,
            lama_panen=lama_panen,
            tanggal_panen = tanggal_panen,
            ganti_pupuk = ganti_pupuk
        )
        db.session.add(data)
        db.session.commit()

        return redirect("/hidroponik")
    
    data = Hidroponik.query.all() or []

    for t in data:
        t.sisa_panen = sisa_hari(t.tanggal_panen)
        t.sisa_pupuk = sisa_ganti_pupuk(t.tanggal_tanam, t.ganti_pupuk)
    return render_template("hidroponik.html",data=data)

#=================== CONNECTED ============================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
