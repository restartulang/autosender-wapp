import customtkinter as ctk

class SettingsModal(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        from utils.path_helper import set_window_icon
        set_window_icon(self)
        
        self.title("Pengaturan Konfigurasi")
        self.geometry("450x400")
        self.resizable(False, False)
        self.configure(fg_color="#ffffff")
        
        self.transient(master)
        self.grab_set()
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        lbl_title = ctk.CTkLabel(header_frame, text="⚙ Pengaturan Konfigurasi", 
                                 font=ctk.CTkFont(size=18, weight="bold"), text_color="#0b1c30")
        lbl_title.pack(side="left")
        
        # Separator
        ctk.CTkFrame(self, height=1, fg_color="#c1c6d5").pack(fill="x")
        
        # Body
        body_frame = ctk.CTkFrame(self, fg_color="transparent")
        body_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Station ID
        lbl_station = ctk.CTkLabel(body_frame, text="STATION ID (ICAO)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#727784")
        lbl_station.pack(anchor="w", pady=(0, 5))
        
        self.entry_station = ctk.CTkEntry(body_frame, placeholder_text="WAAA", font=ctk.CTkFont(family="Consolas", size=14),
                                          fg_color="#ffffff", border_color="#c1c6d5", text_color="#0b1c30")
        self.entry_station.pack(fill="x", pady=(0, 15))
        self.entry_station.insert(0, "WAAA")
        
        # API Key
        lbl_api = ctk.CTkLabel(body_frame, text="API KEY DATA TRANSMISSION", font=ctk.CTkFont(size=11, weight="bold"), text_color="#727784")
        lbl_api.pack(anchor="w", pady=(0, 5))
        
        self.entry_api = ctk.CTkEntry(body_frame, placeholder_text="API Key", show="*", font=ctk.CTkFont(family="Consolas", size=14),
                                      fg_color="#ffffff", border_color="#c1c6d5", text_color="#0b1c30")
        self.entry_api.pack(fill="x", pady=(0, 15))
        self.entry_api.insert(0, "dummy-api-key-12345")
        
        # Bahasa
        lbl_lang = ctk.CTkLabel(body_frame, text="BAHASA ANTARMUKA", font=ctk.CTkFont(size=11, weight="bold"), text_color="#727784")
        lbl_lang.pack(anchor="w", pady=(0, 5))
        
        self.opt_lang = ctk.CTkOptionMenu(body_frame, values=["Bahasa Indonesia", "English (International)"],
                                          fg_color="#ffffff", button_color="#eff4ff", button_hover_color="#e5eeff",
                                          text_color="#0b1c30")
        self.opt_lang.pack(fill="x")
        
        # Footer
        footer_frame = ctk.CTkFrame(self, fg_color="#eff4ff", corner_radius=0, height=60)
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)
        
        # Separator above footer
        ctk.CTkFrame(self, height=1, fg_color="#c1c6d5").pack(fill="x", side="bottom")
        
        btn_save = ctk.CTkButton(footer_frame, text="Simpan Perubahan", font=ctk.CTkFont(weight="bold"),
                                 fg_color="#0066cc", hover_color="#004e9f", text_color="#ffffff",
                                 command=self.destroy)
        btn_save.pack(side="right", padx=20, pady=15)
        
        btn_cancel = ctk.CTkButton(footer_frame, text="Batal", font=ctk.CTkFont(weight="bold"),
                                   fg_color="transparent", hover_color="#e5eeff", text_color="#414753",
                                   command=self.destroy)
        btn_cancel.pack(side="right", padx=(0, 10), pady=15)
