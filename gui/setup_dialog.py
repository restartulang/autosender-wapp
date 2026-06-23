import customtkinter as ctk
import tkinter.messagebox as messagebox
from utils.credentials import save_credentials, has_credentials
import threading

class SetupDialog(ctk.CTkToplevel):
    def __init__(self, master, sender_factory):
        super().__init__(master)
        from utils.path_helper import set_window_icon
        set_window_icon(self)
        
        self.title("Setup Kredensial CMSS")
        self.geometry("520x420")
        self.resizable(False, False)
        self.configure(fg_color="#ffffff")
        
        # Make modal
        self.transient(master)
        self.grab_set()
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.sender_factory = sender_factory
        
        # Container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Header
        lbl_title = ctk.CTkLabel(container, text="Konfigurasi Awal", font=ctk.CTkFont(family="Inter", size=24, weight="bold"), text_color="#1e293b")
        lbl_title.pack(pady=(0, 10))
        
        lbl_info = ctk.CTkLabel(container, text="Masukkan username dan password BMKGSoft\nAnda untuk menghubungkan pengiriman data.", 
                                font=ctk.CTkFont(family="Inter", size=13), text_color="#64748b", justify="center")
        lbl_info.pack(pady=(0, 30))
        
        # Username Field
        lbl_user = ctk.CTkLabel(container, text="USERNAME BMKGSOFT", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color="#475569")
        lbl_user.pack(anchor="w", pady=(0, 5))
        
        user_frame = ctk.CTkFrame(container, fg_color="#f8fafc", border_width=1, border_color="#cbd5e1", corner_radius=8, height=55)
        user_frame.pack(fill="x", pady=(0, 10))
        user_frame.pack_propagate(False)
        
        ctk.CTkLabel(user_frame, text="👤", font=ctk.CTkFont(size=18), text_color="#94a3b8").pack(side="left", padx=(15, 10))
        self.entry_user = ctk.CTkEntry(user_frame, placeholder_text="Masukkan Username BMKGSoft", fg_color="transparent", bg_color="transparent", border_width=0, corner_radius=0, text_color="#0f172a", font=ctk.CTkFont(family="Inter", size=14))
        self.entry_user.pack(side="left", fill="both", expand=True, padx=(0, 15), pady=2)
        
        # Password Field
        lbl_pass = ctk.CTkLabel(container, text="PASSWORD BMKGSOFT", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color="#475569")
        lbl_pass.pack(anchor="w", pady=(0, 5))
        
        pass_frame = ctk.CTkFrame(container, fg_color="#f8fafc", border_width=1, border_color="#cbd5e1", corner_radius=8, height=55)
        pass_frame.pack(fill="x", pady=(0, 20))
        pass_frame.pack_propagate(False)
        
        ctk.CTkLabel(pass_frame, text="🔒", font=ctk.CTkFont(size=18), text_color="#94a3b8").pack(side="left", padx=(15, 10))
        self.entry_pass = ctk.CTkEntry(pass_frame, placeholder_text="Masukkan Password BMKGSoft", show="*", fg_color="transparent", bg_color="transparent", border_width=0, corner_radius=0, text_color="#0f172a", font=ctk.CTkFont(family="Inter", size=14))
        self.entry_pass.pack(side="left", fill="both", expand=True, padx=(0, 15), pady=2)
        
        try:
            from utils.credentials import get_credentials
            current_user, _ = get_credentials()
            self.entry_user.insert(0, current_user)
        except Exception:
            pass

        
        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        btn_test = ctk.CTkButton(btn_frame, text="Test Koneksi", command=self._test_koneksi, fg_color="#f8fafc", hover_color="#e2e8f0", text_color="#475569", border_width=1, border_color="#cbd5e1", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), height=40, corner_radius=8)
        btn_test.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn_save = ctk.CTkButton(btn_frame, text="Simpan Credentials", command=self._simpan, fg_color="#10b981", hover_color="#059669", text_color="#ffffff", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), height=40, corner_radius=8)
        btn_save.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
    def _test_koneksi(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        if not user or not pwd:
            messagebox.showwarning("Peringatan", "Isi username dan password dulu.")
            return
            
        def run_test():
            # Create a temporary sender just to test
            try:
                # Temporarily save to test with Playwright
                save_credentials(user, pwd)
                sender = self.sender_factory.create()
                import asyncio
                res = asyncio.run(sender.health_check())
                if res:
                    messagebox.showinfo("Sukses", "Login berhasil diverifikasi!")
                else:
                    messagebox.showerror("Gagal", "Login BMKGSoft gagal diverifikasi.")
            except Exception as e:
                messagebox.showerror("Error", f"Terjadi kesalahan: {e}")
                
        threading.Thread(target=run_test, daemon=True).start()
        
    def _simpan(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        if not user or not pwd:
            messagebox.showwarning("Peringatan", "Isi username dan password dulu.")
            return
            
        try:
            save_credentials(user, pwd)
            messagebox.showinfo("Sukses", "Credentials berhasil disimpan.")
            self.grab_release()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan credentials: {e}")
            
    def _on_closing(self):
        if not has_credentials():
            messagebox.showwarning("Peringatan", "Anda harus memasukkan credentials sebelum bisa menggunakan aplikasi.")
        else:
            self.grab_release()
            self.destroy()
