from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
import pickle
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

class Murid:
    def __init__(self, nama, tanggal_lahir, nik, alamat, email, angkatan):
        self.nama = nama
        self.tanggal_lahir = tanggal_lahir
        self.nik = nik
        self.alamat = alamat
        self.email = email
        self.angkatan = angkatan
        self.id = self.generate_id(nama, tanggal_lahir, nik)

    def generate_id(self, nama, tanggal_lahir, nik):
        hash_object = hashlib.sha256(f"{nama}{tanggal_lahir}{nik}".encode())
        return hash_object.hexdigest()

class DatabaseMurid:
    def __init__(self):
        self.database = self.load_data()

    def tambah_murid(self, murid):
        if murid.id in self.database:
            return f"Murid dengan ID {murid.id} sudah ada di database."
        else:
            self.database[murid.id] = murid
            self.save_data()
            return f"Murid {murid.nama} berhasil ditambahkan."

    def hapus_murid(self, murid_id):
        if murid_id in self.database:
            del self.database[murid_id]
            self.save_data()
            return f"Murid dengan ID {murid_id} berhasil dihapus."
        else:
            return f"Murid dengan ID {murid_id} tidak ditemukan."

    def cari_murid(self, murid_id):
        if murid_id in self.database:
            murid = self.database[murid_id]
            return murid
        else:
            return None

    def edit_murid(self, murid_id, nama, tanggal_lahir, nik, alamat, email, angkatan):
        if murid_id in self.database:
            murid = self.database[murid_id]
            murid.nama = nama
            murid.tanggal_lahir = tanggal_lahir
            murid.nik = nik
            murid.alamat = alamat
            murid.email = email
            murid.angkatan = angkatan
            self.save_data()
            return f"Murid dengan ID {murid_id} berhasil diperbarui."
        else:
            return f"Murid dengan ID {murid_id} tidak ditemukan."

    def tampilkan_semua_murid(self):
        return self.database.values()

    def save_data(self):
        with open('database_murid.pkl', 'wb') as f:
            pickle.dump(self.database, f)

    def load_data(self):
        if os.path.exists('database_murid.pkl'):
            with open('database_murid.pkl', 'rb') as f:
                return pickle.load(f)
        else:
            return {}

class Admin:
    def __init__(self, username, password):
        self.username = username
        self.password_hash = self.hash_password(password)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

class SistemLogin:
    def __init__(self):
        self.admins = self.load_data()
        print("Loaded admins:", self.admins)  # Debugging statement

    def tambah_admin(self, username, password):
        if username in self.admins:
            return "Admin dengan username tersebut sudah ada."
        else:
            self.admins[username] = Admin(username, password)
            self.save_data()
            print(f"Added admin: {username}")  # Debugging statement
            return "Admin berhasil ditambahkan."

    def login(self, username, password):
        print(f"Login attempt with username: {username} and password: {password}")  # Debugging statement
        if username in self.admins and self.admins[username].verify_password(password):
            print("Login successful")  # Debugging statement
            return True
        else:
            print("Login failed")  # Debugging statement
            return False

    def tampilkan_semua_admin(self):
        return self.admins.keys()

    def save_data(self):
        with open('admins.pkl', 'wb') as f:
            pickle.dump(self.admins, f)

    def load_data(self):
        if os.path.exists('admins.pkl'):
            with open('admins.pkl', 'rb') as f:
                return pickle.load(f)
        else:
            return {}

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', logged_in=True)
    return render_template('index.html', logged_in=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if sistem_login.login(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Username atau password salah', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nama = request.form['nama']
        tanggal_lahir = request.form['tanggal_lahir']
        nik = request.form['nik']
        alamat = request.form['alamat']
        email = request.form['email']
        angkatan = request.form['angkatan']
        murid = Murid(nama, tanggal_lahir, nik, alamat, email, angkatan)
        message = db_murid.tambah_murid(murid)
        flash(message, 'success' if 'berhasil' in message else 'danger')
        return redirect(url_for('login'))
    return render_template('add_student.html')

@app.route('/view_students')
def view_students():
    if 'username' not in session:
        return redirect(url_for('login'))
    students = db_murid.tampilkan_semua_murid()
    return render_template('view_students.html', students=students)

@app.route('/edit_student/<murid_id>', methods=['GET', 'POST'])
def edit_student(murid_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    murid = db_murid.cari_murid(murid_id)
    if request.method == 'POST':
        nama = request.form['nama']
        tanggal_lahir = request.form['tanggal_lahir']
        nik = request.form['nik']
        alamat = request.form['alamat']
        email = request.form['email']
        angkatan = request.form['angkatan']
        message = db_murid.edit_murid(murid_id, nama, tanggal_lahir, nik, alamat, email, angkatan)
        flash(message, 'success' if 'berhasil' in message else 'danger')
        return redirect(url_for('view_students'))
    return render_template('edit_student.html', murid=murid)

@app.route('/delete_student/<murid_id>', methods=['POST'])
def delete_student(murid_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    message = db_murid.hapus_murid(murid_id)
    flash(message, 'success' if 'berhasil' in message else 'danger')
    return redirect(url_for('view_students'))

@app.route('/add_admin', methods=['GET', 'POST'])
def add_admin():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        message = sistem_login.tambah_admin(username, password)
        flash(message, 'success' if 'berhasil' in message else 'danger')
        return redirect(url_for('login'))
    return render_template('add_admin.html')

if __name__ == "__main__":
    sistem_login = SistemLogin()
    db_murid = DatabaseMurid()

    # Tambah admin default jika belum ada
    if "1" not in sistem_login.admins:
        print("Menambahkan admin default")
        sistem_login.tambah_admin("1", "1")
    else:
        print("Admin default sudah ada")
    
    app.run(debug=True)
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)