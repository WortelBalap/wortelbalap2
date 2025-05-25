import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from io import BytesIO

# =========================
# ⚙ Konfigurasi Page
# =========================
st.set_page_config(
    page_title="Wortel Balap 🥕",
    page_icon="🥕",
    layout="centered"
)

# =========================
# 🔐 Login & Session State
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

# Dummy hardcoded credentials
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "buyer": {"password": "buyer123", "role": "buyer"}
}

# =========================
# 🔐 Login & Register Page
# =========================
def login_page():
    st.title("🔐 Login / Register")
    tab_login, tab_register = st.tabs(["Login", "Buat Akun"])

    # --- Login Tab ---
    with tab_login:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            # Cek hardcoded user dulu
            user = USERS.get(username)
            if user and user["password"] == password:
                st.session_state.logged_in = True
                st.session_state.role = user["role"]
                st.session_state.username = username
                st.success(f"Selamat datang, {username} ({user['role']})!")
                st.rerun()
            else:
                # Cek database
                conn = sqlite3.connect("users.db")
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
                result = c.fetchone()
                conn.close()
                if result:
                    st.session_state.logged_in = True
                    st.session_state.username = result[4]
                    st.session_state.role = result[6]
                    st.success(f"Selamat datang, {result[1]} ({result[6]})!")
                    st.rerun()
                else:
                    st.error("Username atau password salah.")

    # --- Register Tab ---
    with tab_register:
        new_name = st.text_input("Nama Lengkap")
        new_alamat = st.text_area("Alamat")
        new_hp = st.text_input("No. Telepon")
        new_username = st.text_input("Buat Username")
        new_password = st.text_input("Buat Password", type="password")

        if st.button("Daftar"):
            if new_name and new_alamat and new_hp and new_username and new_password:
                try:
                    conn = sqlite3.connect("users.db")
                    c = conn.cursor()
                    c.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nama TEXT,
                            alamat TEXT,
                            no_hp TEXT,
                            username TEXT UNIQUE,
                            password TEXT,
                            role TEXT
                        )
                    """)
                    c.execute("INSERT INTO users (nama, alamat, no_hp, username, password, role) VALUES (?, ?, ?, ?, ?, ?)",
                              (new_name, new_alamat, new_hp, new_username, new_password, "buyer"))
                    conn.commit()
                    conn.close()
                    st.success("Pendaftaran berhasil! Silakan login.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Username sudah digunakan. Coba yang lain.")
            else:
                st.warning("Harap isi semua data.")

if not st.session_state.logged_in:
    login_page()
    st.stop()

def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.rerun()

# =========================
# 🔧 Init DB for Keuangan
# =========================
def init_db():
    conn = sqlite3.connect("keuangan.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_produk TEXT,
            jumlah INTEGER,
            subtotal INTEGER,
            tanggal TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# =========================
# 🎨 Custom CSS for UI
# =========================
st.markdown("""
    <style>
        .stButton>button {
            background-color: #FF8000;
            color: white;
            font-weight: bold;
            border-radius: 10px;
        }
        .stSidebar {
            background-color: #E0FFE0;
        }
        .block-container {
            padding-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# =========================
# 🥕 Data Produk
# =========================
if "produk" not in st.session_state:
    st.session_state.produk = {
        "Wortel Premium (per kg)": {"harga": 12000, "stok": 300, "satuan": "kg"},
        "Pupuk Kompos (1 kg)": {"harga": 7000, "stok": 50, "satuan": "kg"},
        "Pupuk Organik Cair (1 liter)": {"harga": 50000, "stok": 30, "satuan": "liter"},
        "Box Sayur (25 unit)": {"harga": 15000, "stok": 250, "satuan": "pak (25 unit)"}
    }

# =========================
# 🛒 Keranjang
# =========================
if "keranjang" not in st.session_state:
    st.session_state.keranjang = {}

# =========================
# 🚪 Sidebar Navigasi
# =========================
st.sidebar.title("🥕 Wortel Balap")
st.sidebar.markdown(f"Login sebagai: {st.session_state.role}")
if st.sidebar.button("🔓 Logout"):
    logout()

menu = st.sidebar.radio("Navigasi", ["Home", "Product", "Checkout", "Transaksi", "Contact"])

# =========================
# 🏠 Landing Page
# =========================
if menu == "Home":
    st.image("logo.png", width=120)
    st.title("Selamat Datang di Wortel Balap 🥕")
    st.image("wortel bg.jpg", use_container_width=True)
    st.subheader("Bertani Cerdas, Belanja Cepat")
    st.markdown("""
    Kami hadir untuk memudahkan para petani dan pelanggan dalam memenuhi kebutuhan pertanian:
    - Pembelian wortel segar dan bibit berkualitas
    - Beragam pupuk dan alat pertanian
    """)

# =========================
# 🛒 Daftar Produk
# =========================
elif menu == "Product":
    st.title("🛒 Daftar Produk")
    if st.session_state.role != "buyer":
        st.warning("Halaman ini hanya dapat diakses oleh pembeli.")
    else:
        for nama, info in st.session_state.produk.items():
            st.write(f"📦 {nama}")
            st.write(f"Harga: Rp{info['harga']} / {info['satuan']} | Stok: {info['stok']} {info['satuan']}")
            jumlah = st.number_input(
                f"Jumlah beli ({info['satuan']}) - {nama}",
                min_value=0,
                max_value=info["stok"],
                key=f"jumlah_{nama}"
            )
            if st.button(f"Tambah ke Keranjang - {nama}", key=f"btn_{nama}"):
                if jumlah > 0:
                    if nama in st.session_state.keranjang:
                        st.session_state.keranjang[nama] += jumlah
                    else:
                        st.session_state.keranjang[nama] = jumlah
                    st.success(f"{jumlah} {info['satuan']} {nama} ditambahkan ke keranjang.")
                else:
                    st.warning("Masukkan jumlah minimal 1.")

# =========================
# ✅ Checkout Page
# =========================
elif menu == "Checkout":
    st.title("🧾 Checkout & Keranjang Belanja")
    if st.session_state.role != "buyer":
        st.warning("Halaman ini hanya untuk pembeli.")
    elif st.session_state.keranjang:
        total = 0
        for nama, jumlah in st.session_state.keranjang.items():
            harga = st.session_state.produk[nama]["harga"]
            satuan = st.session_state.produk[nama]["satuan"]
            subtotal = harga * jumlah
            st.write(f"{nama} - {jumlah} {satuan} x Rp{harga} = Rp{subtotal}")
            total += subtotal
        st.markdown(f"💰 Total Belanja: Rp{total}")

        st.subheader("📦 Alamat Pengiriman")
        alamat = st.text_area("Masukkan alamat lengkap Anda", placeholder="Contoh: Jl. Mawar No. 123, Bandung")

        st.subheader("💳 Metode Pembayaran")
        opsi_metode = ["--Pilih Bank--", "BCA", "Mandiri", "DANA"]
        metode = st.radio("Pilih metode pembayaran", opsi_metode)
        if metode == "BCA":
            st.info("💳 Nomor rekening: 58442352208 a.n. Wortel Balap")
        elif metode == "Mandiri":
            st.info("💳 Nomor rekening: 12344567890 a.n. Wortel Balap")
        elif metode == "DANA":
            st.info("💳 Nomor rekening: 085955557777 a.n. Wortel Balap")

        st.markdown("""
        📧 Jangan lupa kirim *bukti pembayaran* ke email kami ya!
        Cek info lengkapnya di menu *Contact* (sidebar). Agar pesananmu bisa segera kami proses. 
        Terima kasih!🥕
        """)

        if st.button("✅ Place Order"):
            conn = sqlite3.connect("keuangan.db")
            c = conn.cursor()
            for nama, jumlah in st.session_state.keranjang.items():
                harga = st.session_state.produk[nama]["harga"]
                subtotal = harga * jumlah
                tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO transaksi (nama_produk, jumlah, subtotal, tanggal) VALUES (?, ?, ?, ?)",
                          (nama, jumlah, subtotal, tanggal))
                st.session_state.produk[nama]["stok"] -= jumlah
            conn.commit()
            conn.close()
            st.success("Pesanan berhasil diproses dan disimpan! Terima kasih.")
            st.session_state.keranjang.clear()
    else:
        st.info("Keranjang masih kosong.")

# =========================
# 📊 Transaksi Penjualan
# =========================
elif menu == "Transaksi":
    st.title("📊 Transaksi Penjualan")
    if st.session_state.role != "admin":
        st.warning("Halaman ini hanya untuk admin.")
    else:
        conn = sqlite3.connect("keuangan.db")
        df = pd.read_sql_query("SELECT * FROM transaksi", conn)
        conn.close()

        if df.empty:
            st.warning("Tidak ada data untuk diekspor.")
        else:
            st.dataframe(df)
            total_pendapatan = df["subtotal"].sum()
            st.markdown(f"💵 Total Pendapatan: Rp{total_pendapatan}")

            tanggal_hari_ini = datetime.today().strftime('%Y-%m-%d_%H%M%S')
            buffer = BytesIO()

            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name="Laporan")
            buffer.seek(0)

            st.download_button(
                label="📥 Download Laporan (Excel)",
                data=buffer,
                file_name=f"laporan_keuangan_{tanggal_hari_ini}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# =========================
# 📞 Kontak
# =========================
elif menu == "Contact":
    st.title("📞 Hubungi Kami")
    st.write("📧 Email: wortelbalappp@gmail.com")
    st.write("📱 WhatsApp: +6289515557063")
