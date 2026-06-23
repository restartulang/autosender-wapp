import customtkinter as ctk
import queue
from core.ntp_sync import NTPManager
from core.scheduler import Scheduler
from core.sender import SenderFactory
from database import db_manager as db
from gui.header_bar import HeaderBar
from gui.dashboard_cards import DashboardCards
from gui.input_panel import InputPanel
from gui.queue_panel import QueuePanel

SIDEBAR_W = 260
SLIDE_STEP = 26      # pixels per frame
FRAME_MS   = 12      # ~83 fps

class AutosenderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("Autosender WAPP — Stasiun Meteorologi Pattimura Ambon")
        from utils.path_helper import set_window_icon
        set_window_icon(self)
        self.geometry("1280x720")
        self.minsize(1100, 600)
        self.configure(fg_color="#f8f9ff")

        self.gui_queue       = queue.Queue()
        self.sidebar_visible = False
        self._animating      = False
        self.current_sidebar_x = -SIDEBAR_W

        self.ntp_manager = NTPManager()
        self.sender      = SenderFactory.create()
        self.scheduler   = Scheduler(self.ntp_manager, self.sender, self.gui_queue)

        # ── Root layout ────────────────────────────────────────────
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Main Body
        self.grid_columnconfigure(0, weight=0) # Sidebar
        self.grid_columnconfigure(1, weight=1) # Main Content

        # ── Header ─────────────────────────────────────────────────
        self.header_bar = HeaderBar(self, self.ntp_manager, toggle_sidebar_cmd=self.toggle_sidebar)
        self.header_bar.grid(row=0, column=0, columnspan=2, sticky="ew")

        # ── Sidebar ────────────────────────────────────────────────
        from gui.sidebar import Sidebar
        self.sidebar = Sidebar(self)

        # ── Main area ──────────────────────────────────────────────
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(0, weight=0)
        self.main_area.grid_rowconfigure(1, weight=1)
        self.main_area.grid_rowconfigure(2, weight=0)

        # Top padding spacer
        self.top_spacer = ctk.CTkFrame(self.main_area, height=20, fg_color="transparent")
        self.top_spacer.grid(row=0, column=0, sticky="ew")

        # Content frame
        self.content_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        self.content_frame.grid_rowconfigure(0, weight=0)
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=0, minsize=440)
        self.content_frame.grid_columnconfigure(1, weight=1)

        self.dashboard = DashboardCards(self.content_frame)
        self.dashboard.grid(row=0, column=1, sticky="ew", pady=(0, 20))

        self.queue_panel = QueuePanel(self.content_frame, self.ntp_manager, self.scheduler)
        self.queue_panel.grid(row=1, column=1, sticky="nsew")

        self.queue_panel.on_date_change = lambda dt: self.dashboard.refresh(date_str=dt)

        self.input_panel = InputPanel(
            self.content_frame, self.ntp_manager, self.queue_panel, self.dashboard
        )
        self.input_panel.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 20))

        footer = ctk.CTkLabel(
            self.main_area,
            text="© 2026 AUTOSENDER V.2.1 — BMKG STASIUN METEOROLOGI PATTIMURA AMBON",
            font=ctk.CTkFont(size=10, weight="bold"), text_color="#727784"
        )
        footer.grid(row=2, column=0, sticky="s", pady=(10, 20))

        self.ntp_manager.register_callback(self.header_bar.update_ntp_status)
        
        def _on_send_complete():
            self.queue_panel.refresh_antri()
            self.queue_panel.refresh_riwayat()
            self.dashboard.refresh()
            
        self.scheduler.on_send_complete = _on_send_complete
        
        self.ntp_manager.start()
        self.scheduler.start()
        self.bind("<Configure>", self._on_resize)
        self.bind_all("<Button-1>", self._on_root_click, add="+")
        self.process_gui_queue()

    # ── Sidebar Toggle & Animation ────────────────────────────────
    def toggle_sidebar(self):
        if self._animating: return
        self._animating = True
        
        if self.sidebar_visible:
            self._animate_sidebar(-SIDEBAR_W, hide=True)
        else:
            self.sidebar.lift()
            self.sidebar.place(in_=self.main_area, x=self.current_sidebar_x, y=0, relheight=1.0)
            self._animate_sidebar(0, hide=False)

    def _animate_sidebar(self, target_x, hide):
        if self.current_sidebar_x == target_x:
            self.sidebar_visible = not hide
            self._animating = False
            if hide:
                self.sidebar.place_forget()
            return
            
        step = SLIDE_STEP if not hide else -SLIDE_STEP
        self.current_sidebar_x += step
        
        if not hide and self.current_sidebar_x > 0:
            self.current_sidebar_x = 0
        elif hide and self.current_sidebar_x < -SIDEBAR_W:
            self.current_sidebar_x = -SIDEBAR_W
            
        self.sidebar.place(in_=self.main_area, x=self.current_sidebar_x, y=0, relheight=1.0)
        self.after(FRAME_MS, lambda: self._animate_sidebar(target_x, hide))
        
    def _on_root_click(self, event):
        if self.sidebar_visible and not self._animating:
            x_relative = event.x_root - self.winfo_rootx()
            # If clicked outside the sidebar, close it
            if x_relative > SIDEBAR_W:
                self.toggle_sidebar()
                
    def _on_resize(self, event):
        if event.widget == self and self.sidebar_visible and not self._animating:
            self.sidebar.place(in_=self.main_area, x=0, y=0, relheight=1.0)

    # ── GUI queue ──────────────────────────────────────────────────
    def process_gui_queue(self):
        try:
            while True:
                task = self.gui_queue.get_nowait()
                task()
        except queue.Empty:
            pass
        self.after(200, self.process_gui_queue)
