import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, close_cmd=None, **kwargs):
        super().__init__(
            master,
            fg_color="#ffffff",
            corner_radius=0,
            border_color="#e2e8f0",
            border_width=1,
            width=256,
            **kwargs
        )
        self.pack_propagate(False)
        self.grid_propagate(False)
        self.close_cmd = close_cmd

        # ── Navigation ───────────────────────────────────────────
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", padx=16, pady=(16, 0))
        
        lbl_nav = ctk.CTkLabel(nav, text="NAVIGATION", font=ctk.CTkFont(family="Inter", size=10, weight="bold"), text_color="#94a3b8")
        lbl_nav.pack(anchor="w", pady=(0, 8), padx=8)

        from PIL import Image
        from utils.path_helper import get_resource_path
        
        icon_antri = ctk.CTkImage(light_image=Image.open(get_resource_path("assets/icons/antri.png")), size=(18, 18))
        icon_riwayat = ctk.CTkImage(light_image=Image.open(get_resource_path("assets/icons/monitoring.png")), size=(18, 18))
        icon_settings = ctk.CTkImage(light_image=Image.open(get_resource_path("assets/icons/pengaturan.png")), size=(18, 18))
        icon_support = ctk.CTkImage(light_image=Image.open(get_resource_path("assets/icons/support.png")), size=(18, 18))

        self.btn_antri = ctk.CTkButton(
            nav, text=" Set up Credential", image=icon_antri,
            fg_color="#eef2ff", text_color="#004e9f", hover_color="#e0e7ff",
            font=ctk.CTkFont(family="Inter", size=13),
            anchor="w", height=40, corner_radius=6,
            command=self._show_setup
        )
        self.btn_antri.pack(fill="x", pady=2)

        self.btn_riwayat = ctk.CTkButton(
            nav, text=" User", image=icon_riwayat,
            fg_color="transparent", text_color="#414753", hover_color="#f1f5f9",
            font=ctk.CTkFont(family="Inter", size=13),
            anchor="w", height=40, corner_radius=6,
            command=self._show_user
        )
        self.btn_riwayat.pack(fill="x", pady=2)

        # ── Bottom ───────────────────────────────────────────────
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=16, pady=24)
        
        lbl_sys = ctk.CTkLabel(bottom, text="SYSTEM", font=ctk.CTkFont(family="Inter", size=10, weight="bold"), text_color="#94a3b8")
        lbl_sys.pack(anchor="w", pady=(0, 8), padx=8)

        self.btn_settings = ctk.CTkButton(
            bottom, text=" Settings", image=icon_settings,
            fg_color="transparent", text_color="#414753", hover_color="#f1f5f9",
            font=ctk.CTkFont(family="Inter", size=13),
            anchor="w", height=40, corner_radius=6, command=self._show_settings
        )
        self.btn_settings.pack(fill="x", pady=2)

        self.btn_support = ctk.CTkButton(
            bottom, text=" Support", image=icon_support,
            fg_color="transparent", text_color="#414753", hover_color="#f1f5f9",
            font=ctk.CTkFont(family="Inter", size=13),
            anchor="w", height=40, corner_radius=6, command=self._show_support
        )
        self.btn_support.pack(fill="x", pady=(2, 16))
        
        ctk.CTkFrame(bottom, height=1, fg_color="#e2e8f0").pack(fill="x", pady=(0, 16))
        
        footer_frame = ctk.CTkFrame(bottom, fg_color="transparent")
        footer_frame.pack(anchor="w", padx=8)
        ctk.CTkLabel(footer_frame, text="Autosender", font=ctk.CTkFont(family="Inter", size=12, weight="bold"), text_color="#7ba4d1").pack(anchor="w", pady=(0, 0))
        ctk.CTkLabel(footer_frame, text="v2.4.1-STABLE", font=ctk.CTkFont(family="Inter", size=10), text_color="#94a3b8").pack(anchor="w", pady=(0, 0))

    def _show_setup(self):
        from gui.setup_dialog import SetupDialog
        from core.sender import SenderFactory
        SetupDialog(self.master, SenderFactory)
        
    def _show_user(self):
        from gui.user_dialog import UserDialog
        UserDialog(self.master)
        
    def _show_settings(self):
        from gui.settings_modal import SettingsModal
        SettingsModal(self.master)
        
    def _show_support(self):
        from gui.support_modal import SupportModal
        SupportModal(self.master)
