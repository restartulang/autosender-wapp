import customtkinter as ctk
import os
from PIL import Image
from datetime import datetime, timezone, timedelta
from core.ntp_sync import NTPState, NTPStatus
import config

class HeaderBar(ctk.CTkFrame):
    def __init__(self, master, ntp_manager, toggle_sidebar_cmd=None, **kwargs):
        super().__init__(
            master, 
            fg_color="#ffffff", 
            border_width=1, 
            border_color="#e2e8f0", 
            corner_radius=0, 
            **kwargs
        )
        self.ntp_manager = ntp_manager
        self.toggle_sidebar_cmd = toggle_sidebar_cmd
        
        # ── Left Side ─────────────────────────────────────────────
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.pack(side="left", fill="y", padx=16, pady=8)
        
        if self.toggle_sidebar_cmd:
            btn_menu = ctk.CTkButton(
                left_frame, text="≡", width=36, height=36,
                fg_color="transparent", text_color="#004e9f",
                hover_color="#e2e8f0",
                font=ctk.CTkFont(size=28),
                command=self.toggle_sidebar_cmd,
                corner_radius=8
            )
            btn_menu.pack(side="left", padx=(0, 12))
        
        title_label = ctk.CTkLabel(
            left_frame, text="Autosender",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color="#004e9f"
        )
        title_label.pack(side="left")
        
        separator_left = ctk.CTkFrame(left_frame, width=2, height=28, fg_color="#cbd5e1")
        separator_left.pack(side="left", padx=16)
        
        station_label = ctk.CTkLabel(
            left_frame, text=config.STATION_NAME,
            font=ctk.CTkFont(family="Inter", size=16),
            text_color="#414753"
        )
        station_label.pack(side="left")
        
        # ── Right Side ────────────────────────────────────────────
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.pack(side="right", fill="y", padx=24, pady=8)
        
        # NTP & Clocks Container
        info_container = ctk.CTkFrame(right_frame, fg_color="transparent")
        info_container.pack(side="left", padx=(0, 24))
        
        # NTP Status
        self.ntp_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        self.ntp_frame.pack(anchor="e", pady=(0, 4))
        self.ntp_icon = ctk.CTkLabel(self.ntp_frame, text="↻", font=ctk.CTkFont(size=14, weight="bold"), text_color="#006a61")
        self.ntp_icon.pack(side="left", padx=(0, 4))
        self.ntp_lbl = ctk.CTkLabel(self.ntp_frame, text="NTP SYNCED", font=ctk.CTkFont(family="Inter", size=10, weight="bold"), text_color="#414753")
        self.ntp_lbl.pack(side="left")
        
        # Clocks Row
        clocks_row = ctk.CTkFrame(info_container, fg_color="transparent")
        clocks_row.pack(anchor="e")
        
        # WIT Clock
        wit_col = ctk.CTkFrame(clocks_row, fg_color="transparent")
        wit_col.pack(side="left", padx=(0, 16))
        ctk.CTkLabel(wit_col, text="WIT", font=ctk.CTkFont(family="Inter", size=12, weight="bold"), text_color="#414753").pack(anchor="e")
        self.wit_clock = ctk.CTkLabel(wit_col, text="--:--:--", font=ctk.CTkFont(family="Inter", size=18, weight="bold"), text_color="#0b1c30")
        self.wit_clock.pack(anchor="e")
        
        # UTC Clock
        utc_col = ctk.CTkFrame(clocks_row, fg_color="transparent")
        utc_col.pack(side="left")
        ctk.CTkLabel(utc_col, text="UTC", font=ctk.CTkFont(family="Inter", size=12, weight="bold"), text_color="#414753").pack(anchor="e")
        self.utc_clock = ctk.CTkLabel(utc_col, text="--:--:--", font=ctk.CTkFont(family="Inter", size=18, weight="bold"), text_color="#0b1c30")
        self.utc_clock.pack(anchor="e")
        
        # Date Label
        self.date_lbl = ctk.CTkLabel(info_container, text="", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color="#727784")
        self.date_lbl.pack(anchor="e")
        
        # Icons separator
        separator_right = ctk.CTkFrame(right_frame, width=2, height=28, fg_color="#cbd5e1")
        separator_right.pack(side="left", padx=(0, 16))
        
        # Icon buttons
        icons_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        icons_frame.pack(side="left")
        
        try:
            from utils.path_helper import get_resource_path
            icon_key = ctk.CTkImage(light_image=Image.open(get_resource_path("assets/icons/pengaturan.png")), size=(18, 18))
            icon_user = ctk.CTkImage(light_image=Image.open(get_resource_path("assets/icons/support.png")), size=(18, 18))
            icons_data = [(icon_key, self._ganti_credentials), (icon_user, self._show_user_manual)]
        except Exception as e:
            import logging
            logging.error(f"Failed to load icons: {e}")
            icons_data = []
            
        for img, cmd in icons_data:
            b = ctk.CTkButton(
                icons_frame, text="", image=img, width=32, height=32,
                fg_color="transparent", hover_color="#eff4ff",
                command=cmd, corner_radius=16
            )
            b.pack(side="left", padx=4)
        
        self.update_clocks()
    
    def _ganti_credentials(self):
        from gui.setup_dialog import SetupDialog
        from core.sender import SenderFactory
        SetupDialog(self.master, SenderFactory)
        
    def _show_user_manual(self):
        from gui.user_manual_modal import UserManualModal
        UserManualModal(self.master)
    
    def update_clocks(self):
        try:
            accurate_utc = self.ntp_manager.get_accurate_utc()
            wit_time = accurate_utc + timedelta(hours=config.TIMEZONE_OFFSET_H)
            
            self.wit_clock.configure(text=wit_time.strftime("%H:%M:%S"))
            self.utc_clock.configure(text=accurate_utc.strftime("%H:%M:%S"))
            
            day_names = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
            month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
            
            day_idx = accurate_utc.weekday()
            day_name = day_names[day_idx]
            month_name = month_names[accurate_utc.month]
            
            date_str = f"{day_name}, {accurate_utc.day:02d} {month_name} {accurate_utc.year}"
            self.date_lbl.configure(text=date_str)
        except Exception:
            pass
        self.after(1000, self.update_clocks)
    
    def update_ntp_status(self, state: NTPState):
        if state.status == NTPStatus.SYNCED:
            self.ntp_icon.configure(text_color="#006a61")
            self.ntp_lbl.configure(text="NTP SYNCED")
        elif state.status == NTPStatus.HOLD:
            self.ntp_icon.configure(text_color="#ba1a1a")
            self.ntp_lbl.configure(text="NTP ERROR")
        else:
            self.ntp_icon.configure(text_color="#d97706")
            self.ntp_lbl.configure(text="SYNCING...")
