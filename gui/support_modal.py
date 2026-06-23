import customtkinter as ctk

class SupportModal(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        from utils.path_helper import set_window_icon
        set_window_icon(self)
        
        self.title("Pusat Bantuan")
        self.geometry("450x380")
        self.resizable(False, False)
        self.configure(fg_color="#ffffff")
        
        self.transient(master)
        self.grab_set()
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        lbl_title = ctk.CTkLabel(header_frame, text="❓ Pusat Bantuan", 
                                 font=ctk.CTkFont(size=18, weight="bold"), text_color="#0b1c30")
        lbl_title.pack(side="left")
        
        # Separator
        ctk.CTkFrame(self, height=1, fg_color="#c1c6d5").pack(fill="x")
        
        # Body
        body_frame = ctk.CTkFrame(self, fg_color="transparent")
        body_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Links
        docs_frame = ctk.CTkFrame(body_frame, fg_color="#eff4ff", border_color="#c1c6d5", border_width=1, corner_radius=6)
        docs_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(docs_frame, text="📄 Dokumentasi Teknis", font=ctk.CTkFont(weight="bold", size=14), text_color="#0b1c30").pack(anchor="w", padx=15, pady=(10, 0))
        ctk.CTkLabel(docs_frame, text="Panduan penggunaan format sandi cuaca.", font=ctk.CTkFont(size=12), text_color="#414753").pack(anchor="w", padx=15, pady=(0, 10))
        
        contact_frame = ctk.CTkFrame(body_frame, fg_color="#eff4ff", border_color="#c1c6d5", border_width=1, corner_radius=6)
        contact_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(contact_frame, text="💬 Hubungi Admin IT", font=ctk.CTkFont(weight="bold", size=14), text_color="#0b1c30").pack(anchor="w", padx=15, pady=(10, 0))
        ctk.CTkLabel(contact_frame, text="Laporkan masalah koneksi atau bug aplikasi.\nWhatsApp: 082365111918", font=ctk.CTkFont(size=12), text_color="#414753", justify="left").pack(anchor="w", padx=15, pady=(0, 10))
        
        # Version info
        ctk.CTkFrame(body_frame, height=1, fg_color="#c1c6d5").pack(fill="x", pady=(0, 10))
        
        info_frame1 = ctk.CTkFrame(body_frame, fg_color="transparent")
        info_frame1.pack(fill="x")
        ctk.CTkLabel(info_frame1, text="Versi Aplikasi", text_color="#727784").pack(side="left")
        ctk.CTkLabel(info_frame1, text="v2.1.0-stable", text_color="#0066cc", font=ctk.CTkFont(family="Consolas", weight="bold")).pack(side="right")
        
        info_frame2 = ctk.CTkFrame(body_frame, fg_color="transparent")
        info_frame2.pack(fill="x", pady=(5,0))
        ctk.CTkLabel(info_frame2, text="Terakhir Update", text_color="#727784").pack(side="left")
        ctk.CTkLabel(info_frame2, text="12 Oktober 2024", text_color="#414753").pack(side="right")
        
        # Footer
        footer_frame = ctk.CTkFrame(self, fg_color="#eff4ff", corner_radius=0, height=60)
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)
        
        # Separator above footer
        ctk.CTkFrame(self, height=1, fg_color="#c1c6d5").pack(fill="x", side="bottom")
        
        btn_close = ctk.CTkButton(footer_frame, text="Tutup", font=ctk.CTkFont(weight="bold"),
                                  fg_color="#ffffff", hover_color="#e5eeff", text_color="#414753",
                                  border_color="#c1c6d5", border_width=1, command=self.destroy)
        btn_close.pack(fill="x", padx=20, pady=15)
