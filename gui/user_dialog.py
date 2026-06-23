import customtkinter as ctk
import tkinter.messagebox as messagebox
import json
import os

USER_FILE = os.path.join(os.path.dirname(__file__), '..', 'database', 'users.json')

class UserManager:
    @staticmethod
    def get_users():
        if not os.path.exists(USER_FILE):
            return []
        try:
            with open(USER_FILE, 'r') as f:
                return json.load(f)
        except:
            return []

    @staticmethod
    def save_users(users):
        os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)
        with open(USER_FILE, 'w') as f:
            json.dump(users, f)

class UserDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        from utils.path_helper import set_window_icon
        set_window_icon(self)
        
        self.title("Manajemen Petugas Observasi")
        self.geometry("450x500")
        self.resizable(False, False)
        self.configure(fg_color="#ffffff")
        
        self.transient(master)
        self.grab_set()
        
        self.users = UserManager.get_users()
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        lbl_title = ctk.CTkLabel(container, text="Daftar Petugas Observasi", font=ctk.CTkFont(family="Inter", size=20, weight="bold"), text_color="#1e293b")
        lbl_title.pack(anchor="w", pady=(0, 5))
        
        lbl_desc = ctk.CTkLabel(container, text="Kelola nama-nama petugas untuk mempercepat input data.", font=ctk.CTkFont(family="Inter", size=12), text_color="#64748b")
        lbl_desc.pack(anchor="w", pady=(0, 20))
        
        # Add frame
        add_frame = ctk.CTkFrame(container, fg_color="transparent")
        add_frame.pack(fill="x", pady=(0, 20))
        
        self.entry_name = ctk.CTkEntry(add_frame, placeholder_text="Nama Lengkap Petugas", height=38, font=ctk.CTkFont(family="Inter", size=13))
        self.entry_name.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_name.bind("<Return>", lambda e: self._add_user())
        
        btn_add = ctk.CTkButton(add_frame, text="Tambah", width=80, height=38, command=self._add_user, fg_color="#004e9f", hover_color="#003d7a", font=ctk.CTkFont(family="Inter", size=13, weight="bold"))
        btn_add.pack(side="right")
        
        # List frame
        list_container = ctk.CTkFrame(container, fg_color="#f8fafc", border_width=1, border_color="#e2e8f0", corner_radius=8)
        list_container.pack(fill="both", expand=True)
        
        self.scroll_frame = ctk.CTkScrollableFrame(list_container, fg_color="transparent", bg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.refresh_list()
        
    def _add_user(self):
        name = self.entry_name.get().strip()
        if not name:
            return
            
        if name in self.users:
            messagebox.showwarning("Peringatan", "Nama petugas sudah ada di dalam daftar.")
            return
            
        self.users.append(name)
        UserManager.save_users(self.users)
        self.entry_name.delete(0, 'end')
        self.refresh_list()
        
    def _remove_user(self, name):
        if messagebox.askyesno("Konfirmasi", f"Apakah Anda yakin ingin menghapus petugas '{name}'?"):
            if name in self.users:
                self.users.remove(name)
                UserManager.save_users(self.users)
                self.refresh_list()
                
    def refresh_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        if not self.users:
            ctk.CTkLabel(self.scroll_frame, text="Belum ada petugas yang ditambahkan.", font=ctk.CTkFont(family="Inter", size=13, slant="italic"), text_color="#94a3b8").pack(pady=30)
            return
            
        for i, name in enumerate(self.users):
            row = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            lbl = ctk.CTkLabel(row, text=name, font=ctk.CTkFont(family="Inter", size=14), text_color="#0f172a")
            lbl.pack(side="left", padx=10, pady=8)
            
            btn_del = ctk.CTkButton(row, text="Hapus", width=60, height=28, fg_color="#fee2e2", hover_color="#fecaca", text_color="#ef4444", font=ctk.CTkFont(family="Inter", size=12, weight="bold"), command=lambda n=name: self._remove_user(n))
            btn_del.pack(side="right", padx=10, pady=8)
            
            if i < len(self.users) - 1:
                ctk.CTkFrame(self.scroll_frame, height=1, fg_color="#e2e8f0").pack(fill="x", padx=10)
