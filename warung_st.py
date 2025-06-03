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
# 💰 Fungsi Format Rupiah
# =========================
def format_rupiah(angka):
    return f"Rp {angka:,.0f}".replace(",", ".")

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
            user = USERS.get(username)
            if user and user["password"] == password:
                st.session_state.logged_in = True
                st.session_state.role = user["role"]
                st.session_state.username = username
                st.success(f"Selamat datang, {username} ({user['role']})!")
                st.rerun()
            else:
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
# 🎨 Custom CSS
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
# 🥕 Produk
# =========================
if "produk" not in st.session_state:
    st.session_state.produk = {
        "Wortel Premium (per kg)": {"harga": 12000, "stok": 300, "satuan": "kg"},
        "Pupuk Kompos (1 kg)": {"harga": 7000, "stok": 50, "satuan": "kg"},
        "Pupuk Organik Cair (1 liter)": {"harga": 50000, "stok": 30, "satuan": "liter"},
        "Box Sayur (25 unit)": {"harga": 15000, "stok": 250, "satuan": "pak (25 unit)"}
    }

if "keranjang" not in st.session_state:
    st.session_state.keranjang = {}

# =========================
# 🚪 Sidebar
# =========================
st.sidebar.title("🥕 Wortel Balap")
st.sidebar.markdown(f"Login sebagai: {st.session_state.role}")
if st.sidebar.button("🔓 Logout"):
    logout()

menu = st.sidebar.radio("Navigasi", ["Home", "Product", "Checkout", "Transaksi", "Update Stok", "Contact"])

# =========================
# 🏠 Home
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
# 🛒 Produk
# =========================
elif menu == "Product":
    st.title("🛒 Daftar Produk")
    if st.session_state.role != "buyer":
        st.warning("Halaman ini hanya dapat diakses oleh pembeli.")
    else:
        for nama, info in st.session_state.produk.items():
            st.write(f"📦 {nama}")
            st.write(f"Harga: {format_rupiah(info['harga'])} / {info['satuan']} | Stok: {info['stok']} {info['satuan']}")
            jumlah = st.number_input(f"Jumlah beli ({info['satuan']}) - {nama}",
                                     min_value=0, max_value=info["stok"], key=f"jumlah_{nama}")
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
# ✅ Checkout
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
            st.write(f"{nama} - {jumlah} {satuan} x {format_rupiah(harga)} = {format_rupiah(subtotal)}")
            total += subtotal
        st.markdown(f"💰 *Total Belanja: {format_rupiah(total)}*")

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
        📧 Jangan lupa kirim bukti pembayaran ke email kami ya!
        Cek info lengkapnya di menu Contact (sidebar). Agar pesananmu bisa segera kami proses. 
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
# 📊 Transaksi (Admin)
# =========================
elif menu == "Transaksi":
    st.title("📊 Transaksi Penjualan")
    if st.session_state.role != "admin":
        st.warning("Halaman ini hanya untuk admin.")
    else:
        conn = sqlite3.connect("keuangan.db")
        df = pd.read_sql_query("SELECT * FROM transaksi", conn)
        conn.close()

        # Salin untuk tampilan saja
        df_display = df.copy()
        df_display['subtotal'] = df_display['subtotal'].apply(lambda x: f"Rp{x:,.0f}".replace(",", "."))

        if df.empty:
            st.warning("Tidak ada data untuk diekspor.")
        else:
            st.dataframe(df_display)  # ✅ tampilkan yang sudah diformat

            total_pendapatan = df["subtotal"].sum()
            st.markdown(f"💵 *Total Pendapatan: {format_rupiah(total_pendapatan)}*")

            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name="Laporan")
                workbook  = writer.book
                worksheet = writer.sheets["Laporan"]
                format_rp = workbook.add_format({'num_format': 'Rp #,##0'})
                worksheet.set_column('D:D', 18, format_rp)
            buffer.seek(0)

            st.download_button(
                label="📥 Download Laporan (Excel)",
                data=buffer,
                file_name=f"laporan_keuangan_{datetime.today().strftime('%Y-%m-%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

from datetime import datetime  # Pastikan ini ada di awal file

# =========================
# 📦 Update Stok (Admin)
# =========================
if menu == "Update Stok":
    st.title("Update Stok")
    
    if st.session_state.role != "admin":
        st.warning("Halaman ini hanya untuk admin.")
    else:
        # Inisialisasi dict produk jika belum ada
        if "produk" not in st.session_state:
            st.session_state.produk = {}

        # Inisialisasi riwayat jika belum ada
        if "riwayat_stok" not in st.session_state:
            st.session_state.riwayat_stok = []

        st.subheader("📋 Kelola Produk yang Ada")
        produk_list = list(st.session_state.produk.keys())
        if produk_list:
            produk_terpilih = st.selectbox("Pilih produk", produk_list)

            col1, col2 = st.columns(2)
            with col1:
                stok_perubahan = st.number_input("Ubah stok (positif: tambah, negatif: kurang)", value=0)
            with col2:
                harga_input = st.number_input(
                    "Ubah harga (kosongkan jika tidak ingin diubah)",
                    value=st.session_state.produk[produk_terpilih]["harga"]
                )

            if st.button("💾 Simpan Perubahan"):
                old_stok = st.session_state.produk[produk_terpilih]["stok"]
                old_harga = st.session_state.produk[produk_terpilih]["harga"]

                st.session_state.produk[produk_terpilih]["stok"] += stok_perubahan
                st.session_state.produk[produk_terpilih]["harga"] = harga_input

                st.session_state.riwayat_stok.append({
                    "produk": produk_terpilih,
                    "aksi": "Update Stok/Harga",
                    "stok_awal": old_stok,
                    "stok_akhir": st.session_state.produk[produk_terpilih]["stok"],
                    "harga_awal": old_harga,
                    "harga_akhir": harga_input,
                    "oleh": st.session_state.username,
                    "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                st.success(f"{produk_terpilih} berhasil diperbarui.")

        else:
            st.info("Belum ada produk.")

        st.markdown("---")
        st.subheader("➕ Tambah Produk Baru")
        with st.form("form_tambah_produk"):
            nama_baru = st.text_input("Nama produk")
            harga_baru2 = st.number_input("Harga produk", min_value=0)
            satuan_baru = st.text_input("Satuan (contoh: kg, pcs, ikat)")
            stok_awal = st.number_input("Stok awal", min_value=0)
            submitted = st.form_submit_button("Tambah Produk")

            if submitted:
                if nama_baru in st.session_state.produk:
                    st.warning("Produk sudah ada. Gunakan bagian atas untuk memperbarui.")
                elif nama_baru == "":
                    st.warning("Nama produk tidak boleh kosong.")
                else:
                    st.session_state.produk[nama_baru] = {
                        "harga": harga_baru2,
                        "satuan": satuan_baru,
                        "stok": stok_awal
                    }

                    st.session_state.riwayat_stok.append({
                        "produk": nama_baru,
                        "aksi": "Tambah Produk Baru",
                        "stok_awal": 0,
                        "stok_akhir": stok_awal,
                        "harga_awal": 0,
                        "harga_akhir": harga_baru2,
                        "oleh": st.session_state.username,
                        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                    st.success(f"Produk '{nama_baru}' berhasil ditambahkan.")

        st.markdown("---")
        st.subheader("📜 Riwayat Perubahan Stok")
        if st.session_state.riwayat_stok:
            for log in reversed(st.session_state.riwayat_stok[-10:]):
                st.markdown(f"""
                🔹 *[{log["waktu"]}]* {log["aksi"]} oleh *{log["oleh"]}*  
                Produk: *{log["produk"]}*  
                Stok: {log["stok_awal"]} ➝ {log["stok_akhir"]} | Harga: Rp{log["harga_awal"]} ➝ Rp{log["harga_akhir"]}
                """)
        else:
            st.info("Belum ada riwayat stok.")


# =========================
# 📞 Kontak
# =========================
elif menu == "Contact":
    st.title("📞 Hubungi Kami")
    st.write("📧 Email: wortelbalappp@gmail.com")
    st.write("📱 WhatsApp: +6289515557063")
