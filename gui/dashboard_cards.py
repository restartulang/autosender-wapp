import customtkinter as ctk
import threading
from database import db_manager as db

class DashboardCards(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=0)
        
        from PIL import Image
        from utils.path_helper import get_resource_path
        
        self.img_antri = ctk.CTkImage(light_image=Image.open(get_resource_path("assets/icons/antri.png")), size=(18, 18))
        self.img_berhasil = ctk.CTkImage(light_image=Image.open(get_resource_path("assets/icons/berhasil.png")), size=(18, 18))
        self.img_gagal = ctk.CTkImage(light_image=Image.open(get_resource_path("assets/icons/gagal.png")), size=(18, 18))

        self.card_antri = self._create_card(0, "SEDANG ANTRE", 
                                            num_color="#0b1c30", 
                                            icon_bg="#e5eeff", 
                                            icon_image=self.img_antri)
        
        self.card_berhasil = self._create_card(1, "BERHASIL", 
                                               num_color="#006a61", 
                                               icon_bg="#86f2e4", 
                                               icon_image=self.img_berhasil)
        
        self.card_gagal = self._create_card(2, "GAGAL", 
                                            num_color="#ba1a1a", 
                                            icon_bg="#ffdad6", 
                                            icon_image=self.img_gagal)

        self.current_date = None
        self.refresh()
        self._start_periodic_refresh()

    def _start_periodic_refresh(self):
        self.refresh()
        self.after(5000, self._start_periodic_refresh)

    def _create_card(self, col, title, num_color, icon_bg, icon_image):
        card = ctk.CTkFrame(self, fg_color="#FFFFFF", border_color="#e2e8f0",
                            border_width=1, corner_radius=4, height=100)
        card.grid(row=0, column=col, sticky="ew", padx=(0, 16) if col < 2 else 0, pady=0)
        card.pack_propagate(False)
        card.grid_propagate(False)

        # Top frame (Title + Icon)
        top_frame = ctk.CTkFrame(card, fg_color="transparent")
        top_frame.pack(fill="x", padx=(20, 20), pady=(16, 0))

        title_label = ctk.CTkLabel(top_frame, text=title,
                                   font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                                   text_color="#64748b")
        title_label.pack(side="left", anchor="n", pady=5)

        icon_frame = ctk.CTkFrame(top_frame, fg_color=icon_bg, width=32, height=32, corner_radius=16)
        icon_frame.pack(side="right", anchor="n")
        icon_frame.pack_propagate(False)
        
        icon_label = ctk.CTkLabel(icon_frame, text="", image=icon_image)
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Bottom frame (Number)
        bottom_frame = ctk.CTkFrame(card, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=(20, 20), side="bottom", pady=(0, 16))

        value_label = ctk.CTkLabel(bottom_frame, text="0",
                                   font=ctk.CTkFont(family="Inter", size=28, weight="bold"),
                                   text_color=num_color)
        value_label.pack(side="left", anchor="sw")

        return value_label

    def refresh(self, date_str=None):
        if date_str is not None:
            self.current_date = date_str
            
        def _fetch():
            try:
                counts = db.get_dashboard_counts(self.current_date)
                self.after(0, lambda: self._update_labels(counts))
            except Exception as e:
                pass
        threading.Thread(target=_fetch, daemon=True).start()

    def _update_labels(self, counts):
        self.card_antri.configure(text=str(counts.get('antri', 0)))
        self.card_berhasil.configure(text=str(counts.get('berhasil_hari_ini', 0)))
        self.card_gagal.configure(text=str(counts.get('gagal_batal_hari_ini', 0)))
