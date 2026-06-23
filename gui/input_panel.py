import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import timedelta
from PIL import Image
import os
import config
from core.parser import parse
from database import db_manager as db
from core.ntp_sync import NTPStatus

class InputPanel(ctk.CTkFrame):
    def __init__(self, master, ntp_manager, queue_panel, dashboard, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.ntp_manager = ntp_manager
        self.queue_panel = queue_panel
        self.dashboard = dashboard
        
        # ── Frame Config ─────────────────────────────────────
        self.configure(fg_color="#FFFFFF", border_color="#e2e8f0", border_width=1, corner_radius=4)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1) # Textbox row expands
        self.grid_rowconfigure(4, weight=0)
        self.grid_rowconfigure(5, weight=0)
        self.grid_rowconfigure(6, weight=0)
        
        # Header (Icon + Title)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 12))
        
        from utils.path_helper import get_resource_path
        icon_input = ctk.CTkImage(light_image=Image.open(get_resource_path("assets/icons/input_data.png")), size=(24, 24))
        icon_lbl = ctk.CTkLabel(header_frame, text="", image=icon_input)
        icon_lbl.pack(side="left", padx=(0, 8))
        
        title_lbl = ctk.CTkLabel(header_frame, text="Input Data", font=ctk.CTkFont(family="Inter", size=20, weight="bold"), text_color="#0b1c30")
        title_lbl.pack(side="left")
        
        # Subtitle Label
        lbl_subtitle = ctk.CTkLabel(self, text="Masukkan kode sandi cuaca untuk diproses ke jaringan transmisi.", font=ctk.CTkFont(family="Inter", size=14), text_color="#414753", wraplength=400, justify="left")
        lbl_subtitle.grid(row=1, column=0, sticky="w", padx=24, pady=(0, 24))
        
        # Input Data Label
        lbl_input = ctk.CTkLabel(self, text="SANDI CUACA (SYNOP/TAFOR/METAR)", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color="#727784")
        lbl_input.grid(row=2, column=0, sticky="w", padx=24, pady=(0, 4))
        
        # Textbox (expands to fill middle)
        self.textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(family="JetBrains Mono", size=14),
                                      fg_color="#ffffff", text_color="#0b1c30",
                                      border_color="#e2e8f0", border_width=1, corner_radius=4,
                                      wrap="word")
        self.textbox.grid(row=3, column=0, sticky="nsew", padx=24, pady=(0, 12))
        self.textbox.bind("<KeyRelease>", self._on_text_change)
        
        self.placeholder_text = "AAXX 12124 97502 11502 82205 10284 20246\n39905 40118 57014..."
        self.textbox.insert("0.0", self.placeholder_text)
        self.textbox.configure(text_color="#c1c6d5")
        self.textbox.bind("<FocusIn>", self._clear_placeholder)
        self.textbox.bind("<FocusOut>", self._add_placeholder)
        self._is_placeholder = True

        self._debounce_timer = None
        self._current_parse_result = None
        
        # Error Label
        self.lbl_error = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11), text_color="#ba1a1a", wraplength=300, justify="left")
        self.lbl_error.grid(row=4, column=0, sticky="ew", padx=24, pady=(0, 6))

        # Preview Frame
        self.preview_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.preview_frame.grid(row=5, column=0, sticky="ew", padx=24, pady=(0, 16))
        
        self.lbl_tipe = ctk.CTkLabel(self.preview_frame, text="", font=ctk.CTkFont(size=12, weight="bold"), text_color="#0066cc")
        self.lbl_tipe.pack(side="left")
        self.lbl_target = ctk.CTkLabel(self.preview_frame, text="", font=ctk.CTkFont(size=12, weight="bold"), text_color="#0b1c30")
        self.lbl_target.pack(side="right")
        
        # Bottom Area
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=6, column=0, sticky="ew", padx=24, pady=24)
        
        icon_send = ctk.CTkImage(light_image=Image.open(get_resource_path("assets/icons/send.png")), size=(18, 18))
        self.btn_proses = ctk.CTkButton(bottom_frame, text=" Proses & Jadwalkan", image=icon_send,
                                        font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
                                        fg_color="#004e9f", hover_color="#003d7c", text_color="#FFFFFF",
                                        height=48, corner_radius=4, command=self._on_proses)
        self.btn_proses.pack(fill="x", side="top")

    def _clear_placeholder(self, event):
        if self._is_placeholder:
            self.textbox.delete("0.0", "end")
            self.textbox.configure(text_color="#0b1c30")
            self._is_placeholder = False

    def _add_placeholder(self, event):
        text = self.textbox.get("0.0", "end-1c").strip()
        if not text:
            self.textbox.insert("0.0", self.placeholder_text)
            self.textbox.configure(text_color="#c1c6d5")
            self._is_placeholder = True

    def _on_text_change(self, event):
        if self._debounce_timer:
            self.after_cancel(self._debounce_timer)
        self._debounce_timer = self.after(500, self._do_preview)

    def _do_preview(self):
        text = self.textbox.get("0.0", "end-1c").strip()
        if not text or self._is_placeholder:
            self._clear_preview()
            return

        try:
            now_utc = self.ntp_manager.get_accurate_utc()
            res = parse(text, now_utc)
            self._current_parse_result = res
        except Exception as e:
            self.lbl_tipe.configure(text="Tipe: Error", text_color="#ba1a1a")
            self.lbl_target.configure(text="", text_color="#64748B")
            self.lbl_error.configure(text=str(e))
            return

        if res.is_valid:
            self.lbl_tipe.configure(text=f"Tipe: {res.tipe}", text_color="#0066cc")
            target = res.target_utc
            if target.hour == 0 and target.minute == 0 and target.second == 0:
                formatted_utc = (target - timedelta(days=1)).strftime('%d / 24:00')
            else:
                formatted_utc = target.strftime('%d / %H:%M')
            self.lbl_target.configure(text=f"Target UTC: {formatted_utc}Z", text_color="#0b1c30")
            self.lbl_error.configure(text="")
        else:
            self.lbl_tipe.configure(text="Tipe: Invalid", text_color="#ba1a1a")
            self.lbl_target.configure(text="", text_color="#64748B")
            self.lbl_error.configure(text=res.error_msg)

    def _clear_preview(self):
        self._current_parse_result = None
        self.lbl_tipe.configure(text="")
        self.lbl_target.configure(text="")
        self.lbl_error.configure(text="")

    def _on_proses(self):
        self.btn_proses.configure(state="disabled")

        if self.ntp_manager.state.status == NTPStatus.HOLD:
            messagebox.showwarning("Peringatan", "NTP HOLD. Tidak dapat menjadwalkan sandi saat ini.")
            self.btn_proses.configure(state="normal")
            return

        if not self._current_parse_result or not self._current_parse_result.is_valid:
            messagebox.showerror("Error", "Sandi tidak valid atau belum diparsing.")
            self.btn_proses.configure(state="normal")
            return

        res = self._current_parse_result
        now_utc = self.ntp_manager.get_accurate_utc()

        try:
            can, msg = db.can_schedule(res.tipe, res.target_utc)
            if not can:
                messagebox.showwarning("Duplikat", msg)
                self.btn_proses.configure(state="normal")
                return

            db.insert_sandi(res, now_utc)
            messagebox.showinfo("Sukses", "Sandi berhasil dijadwalkan!")
            self.textbox.delete("0.0", "end")
            self._add_placeholder(None)
            self._clear_preview()
            self.queue_panel.refresh_antri()
            self.dashboard.refresh()

        except db.DuplicateSandiError as e:
            messagebox.showwarning("Duplikat", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {e}")

        self.btn_proses.configure(state="normal")
