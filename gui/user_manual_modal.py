import customtkinter as ctk
import os
from PIL import Image

class UserManualModal(ctk.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        from utils.path_helper import set_window_icon
        set_window_icon(self)
        
        self.withdraw() # Sembunyikan window sementara sedang dibangun
        self.title("Panduan Pengguna")
        self.resizable(False, False)
        self.configure(fg_color="#f0f2f5") # Professional gray background
        
        self.transient(master)
        
        # Top Header
        header_frame = ctk.CTkFrame(self, fg_color="#004e9f", corner_radius=0, height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(header_frame, text="Panduan Penggunaan", font=ctk.CTkFont(family="Inter", size=20, weight="bold"), text_color="#ffffff").pack(side="left", padx=24)
        
        # Scrollable Content
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=24, pady=24)
        
        # --- Helper functions for Professional UI ---
        def create_card(title, icon_text=None):
            card = ctk.CTkFrame(self.scroll, fg_color="#ffffff", border_color="#e2e8f0", border_width=1, corner_radius=12)
            card.pack(fill="x", pady=(0, 16))
            
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=20, pady=(16, 12))
            
            if icon_text:
                ctk.CTkLabel(header, text=icon_text, font=ctk.CTkFont(size=18)).pack(side="left", padx=(0, 8))
            
            ctk.CTkLabel(header, text=title, font=ctk.CTkFont(family="Inter", size=16, weight="bold"), text_color="#0b1c30").pack(side="left")
            
            ctk.CTkFrame(card, height=1, fg_color="#f0f2f5").pack(fill="x")
            
            body = ctk.CTkFrame(card, fg_color="transparent")
            body.pack(fill="x", padx=20, pady=16)
            return body

        def add_text(parent, text, bold=False, color="#414753", top_pad=0, bottom_pad=4):
            font = ctk.CTkFont(family="Inter", size=13, weight="bold" if bold else "normal")
            lbl = ctk.CTkLabel(parent, text=text, font=font, text_color=color, justify="left", wraplength=540)
            lbl.pack(anchor="w", pady=(top_pad, bottom_pad))
            
        def add_icon_row(parent, icon_name, title, desc):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=6)
            
            # Load icon safely
            icon_frame = ctk.CTkFrame(row, fg_color="#f8f9ff", width=40, height=40, corner_radius=8)
            icon_frame.pack(side="left", padx=(0, 16))
            icon_frame.pack_propagate(False)
            
            try:
                from utils.path_helper import get_resource_path
                img = ctk.CTkImage(light_image=Image.open(get_resource_path(f"assets/icons/{icon_name}")), size=(20, 20))
                lbl_img = ctk.CTkLabel(icon_frame, text="", image=img)
                lbl_img.place(relx=0.5, rely=0.5, anchor="center")
            except Exception:
                lbl_img = ctk.CTkLabel(icon_frame, text="•", text_color="#004e9f", font=ctk.CTkFont(size=20))
                lbl_img.place(relx=0.5, rely=0.5, anchor="center")
                
            text_frame = ctk.CTkFrame(row, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(text_frame, text=title, font=ctk.CTkFont(family="Inter", size=14, weight="bold"), text_color="#0b1c30", anchor="w").pack(fill="x")
            ctk.CTkLabel(text_frame, text=desc, font=ctk.CTkFont(family="Inter", size=13), text_color="#64748b", justify="left", wraplength=480, anchor="w").pack(fill="x")

        def add_symbol_row(parent, symbol, title, desc, sym_color="#004e9f", bg_color="#f8f9ff"):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=4)
            
            sym_frame = ctk.CTkFrame(row, fg_color=bg_color, width=36, height=36, corner_radius=18)
            sym_frame.pack(side="left", padx=(0, 16))
            sym_frame.pack_propagate(False)
            
            sym_lbl = ctk.CTkLabel(sym_frame, text=symbol, font=ctk.CTkFont(size=16, weight="bold"), text_color=sym_color)
            sym_lbl.place(relx=0.5, rely=0.5, anchor="center")
            
            text_frame = ctk.CTkFrame(row, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(text_frame, text=title, font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#0b1c30", anchor="w").pack(fill="x")
            ctk.CTkLabel(text_frame, text=desc, font=ctk.CTkFont(family="Inter", size=13), text_color="#64748b", justify="left", wraplength=480, anchor="w").pack(fill="x")

        # --- Content ---
        intro_card = create_card("Selamat Datang di Autosender", "👋")
        add_text(intro_card, "Aplikasi ini dirancang untuk menjadwalkan dan mengirimkan pesan (sandi cuaca) secara otomatis pada waktu yang telah ditentukan, berbasis pada standar waktu UTC yang terintegrasi langsung dengan NTP server.", bottom_pad=0)
        
        # Section 1
        c1 = create_card("Bagian Atas (Header)", "🖥️")
        add_text(c1, "• Jam WIT & UTC:", bold=True, bottom_pad=0)
        add_text(c1, "Standar waktu UTC sebagai acuan pengiriman sandi, dan WIT sebagai pembanding lokal.", bottom_pad=8)
        
        add_text(c1, "• Status NTP (↻ NTP SYNCED):", bold=True, bottom_pad=0)
        add_text(c1, "Menandakan jam aplikasi akurat dengan server internet.", bottom_pad=12)
        
        add_text(c1, "Ikon di Pojok Kanan Atas:", bold=True, color="#004e9f", bottom_pad=8)
        add_icon_row(c1, "pengaturan.png", "Pengaturan Kredensial", "Jalan pintas untuk mengatur username dan password pengirim pesan.")
        add_icon_row(c1, "support.png", "Bantuan", "Membuka halaman panduan penggunaan ini.")
        
        # Section 2
        c2 = create_card("Menu Samping (Sidebar)", "📑")
        add_icon_row(c2, "antri.png", "Set up Credential", "Mengatur jalur, konfigurasi jaringan, atau kredensial pengiriman data.")
        add_icon_row(c2, "monitoring.png", "User", "Melihat atau mengatur profil pengguna yang aktif saat ini.")
        add_icon_row(c2, "pengaturan.png", "Settings", "Pengaturan lanjutan untuk sistem dan variabel aplikasi.")
        add_icon_row(c2, "support.png", "Support", "Pusat bantuan teknis serta informasi mengenai versi aplikasi.")
        
        # Section 3
        c3 = create_card("Input Data & Pratinjau", "⌨️")
        add_text(c3, "Saat Anda mengetik sandi cuaca pada kolom input, sistem akan secara otomatis mendeteksi tipe sandi (seperti METAR, SPECI, SYNOP, atau TAFOR) dan mengekstrak waktu target UTC-nya dengan sangat akurat.\n\nJika formatnya sesuai, Anda dapat menekan tombol Proses & Jadwalkan untuk mendaftarkan sandi tersebut ke dalam antrean sistem.", bottom_pad=0)

        # Section 4
        c_dash = create_card("Dashboard Statistik", "📊")
        add_text(c_dash, "Panel ini terletak di bagian atas jendela utama, menampilkan tiga kartu informasi untuk memantau performa pengiriman secara real-time berdasarkan tanggal yang sedang dipilih (atau performa hari ini secara default).", bottom_pad=8)
        add_text(c_dash, "• Sedang Antre:", bold=True, bottom_pad=0)
        add_text(c_dash, "Total pesan yang saat ini menunggu di antrean sistem.", bottom_pad=4)
        add_text(c_dash, "• Berhasil:", bold=True, color="#15803d", bottom_pad=0)
        add_text(c_dash, "Jumlah pesan yang terkonfirmasi sukses dikirim ke GTS.", bottom_pad=4)
        add_text(c_dash, "• Gagal:", bold=True, color="#b91c1c", bottom_pad=0)
        add_text(c_dash, "Jumlah pesan yang gagal terkirim atau dibatalkan.", bottom_pad=8)

        # Section 5
        c4 = create_card("Daftar Pengiriman", "📋")
        add_text(c4, "Tab 'SEDANG ANTRE'", bold=True, color="#004e9f", bottom_pad=2)
        add_text(c4, "Menampilkan daftar pesan yang sedang menunggu waktu untuk dikirim. Anda dapat memantau hitung mundur pengiriman pada kolom Waktu Kirim secara real-time.", bottom_pad=16)
        
        add_text(c4, "Tab 'RIWAYAT PENGIRIMAN'", bold=True, color="#004e9f", bottom_pad=2)
        add_text(c4, "Menyimpan seluruh rekaman transaksi pengiriman yang sudah selesai, baik yang berstatus Berhasil, Gagal, maupun Dibatalkan. Tersedia fitur kalender untuk menelusuri data di tanggal tertentu.", bottom_pad=0)
        
        # Section 5
        c5 = create_card("Arti Status & Tombol Aksi", "💡")
        add_text(c5, "Status Pengiriman", bold=True, color="#0b1c30", bottom_pad=8)
        add_symbol_row(c5, "↻", "ANTRE", "Pesan masih dalam antrean, menunggu gilirannya tiba.", sym_color="#1d4ed8", bg_color="#dbeafe")
        add_symbol_row(c5, "✓", "BERHASIL", "Pesan telah sukses diterima oleh server tujuan.", sym_color="#15803d", bg_color="#dcfce7")
        add_symbol_row(c5, "✕", "GAGAL / DIBATALKAN", "Pesan gagal terkirim karena masalah jaringan, atau sengaja dibatalkan.", sym_color="#b91c1c", bg_color="#fee2e2")
        
        ctk.CTkFrame(c5, height=1, fg_color="#f0f2f5").pack(fill="x", pady=16)
        
        add_text(c5, "Tombol Aksi", bold=True, color="#0b1c30", bottom_pad=8)
        add_symbol_row(c5, "👁", "Detail (Mata)", "Melihat rincian lengkap teks sandi, jadwal, serta log error jika ada.", sym_color="#475569", bg_color="#f1f5f9")
        add_symbol_row(c5, "↻", "Ulangi (Refresh)", "Memasukkan kembali pesan yang gagal/dibatalkan ke dalam antrean.", sym_color="#475569", bg_color="#f1f5f9")
        add_symbol_row(c5, "✕", "Batalkan", "Menghapus pesan dari antrean pengiriman.", sym_color="#b91c1c", bg_color="#fee2e2")
        
        # Footer / Close button
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", padx=24, pady=(0, 24))
        btn_close = ctk.CTkButton(footer_frame, text="Tutup Panduan", font=ctk.CTkFont(family="Inter", size=14, weight="bold"), 
                                  fg_color="#004e9f", text_color="#ffffff", hover_color="#003d7a", height=44, corner_radius=8, command=self.destroy)
        btn_close.pack(anchor="center", fill="x")

        # Posisikan window di tengah dan tampilkan setelah semuanya selesai dirender
        self.update_idletasks()
        if self.master:
            x = self.master.winfo_rootx() + (self.master.winfo_width() // 2) - 340
            y = self.master.winfo_rooty() + (self.master.winfo_height() // 2) - 300
            self.geometry(f"680x600+{x}+{y}")
        else:
            self.geometry("680x600")
            
        self.deiconify() # Tampilkan ke layar
        self.attributes('-topmost', True)
        self.grab_set()
