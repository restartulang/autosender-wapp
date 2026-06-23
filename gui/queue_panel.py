import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import timedelta, datetime, timezone
from database import db_manager as db
from core.ntp_sync import NTPStatus

# Column positions as fractions of total width (left edge of each column)
# ID | TIPE | TARGET UTC | WAKTU KIRIM | STATUS | AKSI
COL_X    = [0.00, 0.08, 0.20, 0.36, 0.52, 0.82]
COL_W    = [0.08, 0.12, 0.16, 0.16, 0.30, 0.18]
PAD_LEFT = 20  # left padding inside rows

class QueuePanel(ctk.CTkFrame):
    def __init__(self, master, ntp_manager, scheduler, **kwargs):
        super().__init__(master, fg_color="#FFFFFF", border_color="#e2e8f0", border_width=1, corner_radius=12, **kwargs)
        self.ntp_manager = ntp_manager
        self.scheduler = scheduler
        self.current_tab = "ANTRI"

        # ── Tabs ──────────────────────────────────────────────────
        self.tab_container = ctk.CTkFrame(self, fg_color="#eff4ff", height=48, corner_radius=0)
        self.tab_container.pack(fill="x")
        self.tab_container.pack_propagate(False)

        # Tab buttons
        self.btn_tab_antri = ctk.CTkButton(self.tab_container, text="SEDANG ANTRE", fg_color="#ffffff",
                                           text_color="#004e9f", font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                                           hover_color="#f8f9ff", corner_radius=0, command=lambda: self._switch_tab("ANTRI"))
        self.btn_tab_antri.pack(side="left", fill="y", ipadx=10)
        
        # Manually add the bottom border line for active tab
        self.indicator_antri = ctk.CTkFrame(self.btn_tab_antri, fg_color="#004e9f", height=2)
        self.indicator_antri.place(relx=0, rely=1.0, anchor="sw", relwidth=1)

        self.btn_tab_riwayat = ctk.CTkButton(self.tab_container, text="RIWAYAT PENGIRIMAN", fg_color="transparent",
                                             text_color="#727784", font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                                             hover_color="#e5eeff", corner_radius=0, command=lambda: self._switch_tab("RIWAYAT"))
        self.btn_tab_riwayat.pack(side="left", fill="y", ipadx=10)
        
        self.indicator_riwayat = ctk.CTkFrame(self.btn_tab_riwayat, fg_color="transparent", height=2)
        self.indicator_riwayat.place(relx=0, rely=1.0, anchor="sw", relwidth=1)

        # Bottom Border of tab container
        ctk.CTkFrame(self.tab_container, fg_color="#e2e8f0", height=1).place(relx=0, rely=1.0, anchor="sw", relwidth=1)

        # ── Date Filter Bar (for RIWAYAT tab) ─────────────────────
        self.filter_bar = ctk.CTkFrame(self, fg_color="#ffffff", height=60, corner_radius=0)
        # Don't pack yet — only shown in RIWAYAT tab
        self.filter_bar.pack_propagate(False)

        filter_inner = ctk.CTkFrame(self.filter_bar, fg_color="transparent")
        filter_inner.pack(side="left", fill="both", expand=True)

        # Left side: Date navigation
        date_nav_frame = ctk.CTkFrame(filter_inner, fg_color="transparent")
        date_nav_frame.pack(side="left", padx=20, pady=12)

        # Tanggal badge
        lbl_tanggal_frame = ctk.CTkFrame(date_nav_frame, fg_color="#ffffff", border_width=1, border_color="#e2e8f0", corner_radius=6, height=36)
        lbl_tanggal_frame.pack(side="left", padx=(0, 10))
        lbl_tanggal_frame.pack_propagate(False)
        ctk.CTkLabel(lbl_tanggal_frame, text="📅", font=ctk.CTkFont(size=14)).pack(side="left", padx=(10, 4))
        ctk.CTkLabel(lbl_tanggal_frame, text="Tanggal:", font=ctk.CTkFont(family="Inter", size=12), text_color="#414753").pack(side="left", padx=(0, 10))

        # Date selector group
        date_sel_group = ctk.CTkFrame(date_nav_frame, fg_color="#ffffff", border_width=1, border_color="#e2e8f0", corner_radius=6, height=36)
        date_sel_group.pack(side="left")
        
        self.btn_prev_day = ctk.CTkButton(date_sel_group, text="<", width=36, height=34,
                                          fg_color="transparent", text_color="#414753",
                                          hover_color="#f8f9ff", corner_radius=0,
                                          font=ctk.CTkFont(family="Inter", size=12),
                                          command=self._prev_day)
        self.btn_prev_day.pack(side="left")

        ctk.CTkFrame(date_sel_group, width=1, fg_color="#e2e8f0").pack(side="left", fill="y")

        self.selected_date = datetime.now().strftime('%Y-%m-%d')
        self.btn_date_display = ctk.CTkButton(
            date_sel_group, text=self._format_display_date(self.selected_date),
            width=220, height=34, fg_color="transparent", text_color="#0b1c30",
            hover_color="#f8f9ff", corner_radius=0,
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            command=self._open_calendar
        )
        self.btn_date_display.pack(side="left")

        ctk.CTkFrame(date_sel_group, width=1, fg_color="#e2e8f0").pack(side="left", fill="y")

        self.btn_next_day = ctk.CTkButton(date_sel_group, text=">", width=36, height=34,
                                          fg_color="transparent", text_color="#414753",
                                          hover_color="#f8f9ff", corner_radius=0,
                                          font=ctk.CTkFont(family="Inter", size=12),
                                          command=self._next_day)
        self.btn_next_day.pack(side="left")

        # Right side: Semua / Hari Ini buttons
        right_btn_frame = ctk.CTkFrame(filter_inner, fg_color="transparent")
        right_btn_frame.pack(side="right", padx=20, pady=12)

        self.btn_clear_filter = ctk.CTkButton(
            right_btn_frame, text="Semua", width=70, height=36,
            fg_color="#ffffff", text_color="#727784",
            hover_color="#f8f9ff", corner_radius=6, border_width=1, border_color="#e2e8f0",
            font=ctk.CTkFont(family="Inter", size=12),
            command=self._clear_date_filter
        )
        self.btn_clear_filter.pack(side="left", padx=(0, 10))

        self.btn_today = ctk.CTkButton(
            right_btn_frame, text="Hari Ini", width=80, height=36,
            fg_color="#004e9f", text_color="#ffffff",
            hover_color="#003d7a", corner_radius=6,
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            command=self._go_today
        )
        self.btn_today.pack(side="left")

        ctk.CTkFrame(self.filter_bar, fg_color="#e2e8f0", height=1).place(relx=0, rely=1.0, anchor="sw", relwidth=1)

        self.date_filter_active = False  # False = show all, True = filter by date

        # ── Headers ───────────────────────────────────────────────
        self.header_frame = ctk.CTkFrame(self, fg_color="#f8f9ff", height=56, corner_radius=0)
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)
        ctk.CTkFrame(self.header_frame, fg_color="#e2e8f0", height=1).place(relx=0, rely=1.0, anchor="sw", relwidth=1)

        headers = ["ID", "TIPE", "TARGET\nUTC", "WAKTU\nKIRIM", "STATUS", "AKSI"]
        for i, txt in enumerate(headers):
            anchor_val = "e" if i == 5 else "w"
            lbl = ctk.CTkLabel(self.header_frame, text=txt, 
                               font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                               text_color="#727784", anchor=anchor_val, justify="left")
            lbl.place(relx=COL_X[i], rely=0.5, anchor="w" if i < 5 else "e",
                      x=PAD_LEFT if i == 0 else 0,
                      relwidth=COL_W[i])
            # For AKSI, anchor to right edge
            if i == 5:
                lbl.place_configure(relx=1.0, anchor="e", x=-20, relwidth=COL_W[i])

        # ── Footer ────────────────────────────────────────────────
        footer_frame = ctk.CTkFrame(self, fg_color="#f8f9ff", height=48, corner_radius=0)
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)
        ctk.CTkFrame(footer_frame, fg_color="#e2e8f0", height=1).place(relx=0, rely=0, anchor="nw", relwidth=1)

        self.lbl_footer = ctk.CTkLabel(footer_frame, text="Menampilkan 0 data transmisi", font=ctk.CTkFont(family="Inter", size=12), text_color="#727784", bg_color="transparent")
        self.lbl_footer.place(relx=0, rely=0.5, anchor="w", x=16)
        
        # Pagination frame removed as requested

        # ── Scrollable Body ───────────────────────────────────────
        self.content_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.content_frame.pack(fill="both", expand=True)

        self.antri_rows = []
        self.refresh_antri()
        self._update_countdown_loop()

    def _switch_tab(self, tab_name):
        self.current_tab = tab_name
        if tab_name == "ANTRI":
            self.btn_tab_antri.configure(fg_color="#ffffff", text_color="#004e9f")
            self.indicator_antri.configure(fg_color="#004e9f")
            self.btn_tab_riwayat.configure(fg_color="transparent", text_color="#727784")
            self.indicator_riwayat.configure(fg_color="transparent")
            self.filter_bar.pack_forget()
            self.refresh_antri()
            if hasattr(self, 'on_date_change'):
                self.on_date_change(None)
        else:
            self.btn_tab_antri.configure(fg_color="transparent", text_color="#727784")
            self.indicator_antri.configure(fg_color="transparent")
            self.btn_tab_riwayat.configure(fg_color="#ffffff", text_color="#004e9f")
            self.indicator_riwayat.configure(fg_color="#004e9f")
            # Show filter bar before the header
            self.filter_bar.pack(fill="x", before=self.header_frame)
            self.refresh_riwayat()
            if hasattr(self, 'on_date_change'):
                self.on_date_change(self.selected_date)

    def _create_row(self, item, is_antri=False):
        row_content = ctk.CTkFrame(self.content_frame, fg_color="#ffffff", height=60)
        row_content.pack(fill="x")
        row_content.pack_propagate(False)

        # Bottom border
        ctk.CTkFrame(row_content, fg_color="#f0f2f5", height=1).place(relx=0, rely=1.0, anchor="sw", relwidth=1)

        # Col 0: ID
        ctk.CTkLabel(row_content, text=f"#{item['id']}", text_color="#004e9f",
                     font=ctk.CTkFont(family="Inter", size=13, weight="bold"), anchor="w"
                     ).place(relx=COL_X[0], rely=0.5, anchor="w", x=PAD_LEFT, relwidth=COL_W[0])

        # Col 1: TIPE
        c1 = ctk.CTkFrame(row_content, fg_color="transparent")
        c1.place(relx=COL_X[1], rely=0.5, anchor="w", relwidth=COL_W[1], relheight=0.6)
        tipe = item.get('tipe_sandi', 'UNKNOWN')
        badge_tipe = ctk.CTkFrame(c1, fg_color="#e5eeff", corner_radius=4, height=26)
        badge_tipe.pack(side="left")
        ctk.CTkLabel(badge_tipe, text=tipe, text_color="#004e9f",
                     font=ctk.CTkFont(family="Inter", size=11, weight="bold")).pack(padx=10, pady=2)

        # Col 2: TARGET UTC
        target_utc_str = item.get('target_utc', '')
        dt = datetime.utcnow()
        if target_utc_str:
            dt = datetime.strptime(target_utc_str, '%Y-%m-%dT%H:%M:%SZ')
            fmt_utc = dt.strftime('%H:%M:%S')
        else:
            fmt_utc = "—"
        ctk.CTkLabel(row_content, text=fmt_utc, text_color="#0b1c30",
                     font=ctk.CTkFont(family="Inter", size=13), anchor="w"
                     ).place(relx=COL_X[2], rely=0.5, anchor="w", relwidth=COL_W[2])

        lbl_countdown = None
        # Col 3: WAKTU KIRIM / COUNTDOWN
        if is_antri:
            lbl_countdown = ctk.CTkLabel(row_content, text="—", text_color="#727784",
                                         font=ctk.CTkFont(family="Inter", size=13), anchor="w")
            lbl_countdown.place(relx=COL_X[3], rely=0.5, anchor="w", relwidth=COL_W[3])
        else:
            wk = item.get('waktu_kirim_utc')
            txt_kirim = datetime.strptime(wk, '%Y-%m-%dT%H:%M:%SZ').strftime('%H:%M:%S') if wk else "—"
            ctk.CTkLabel(row_content, text=txt_kirim, text_color="#0b1c30" if wk else "#727784",
                         font=ctk.CTkFont(family="Inter", size=13), anchor="w"
                         ).place(relx=COL_X[3], rely=0.5, anchor="w", relwidth=COL_W[3])

        # Col 4: STATUS
        c4 = ctk.CTkFrame(row_content, fg_color="transparent")
        c4.place(relx=COL_X[4], rely=0.5, anchor="w", relwidth=COL_W[4], relheight=0.6)

        status = "ANTRE" if is_antri else str(item.get('status', 'ANTRE')).upper()

        if status == "BERHASIL":
            bg_stat, fg_stat, icon = "#dcfce7", "#15803d", "✓"
        elif status == "GAGAL":
            bg_stat, fg_stat, icon = "#fee2e2", "#b91c1c", "✕"
        elif status == "DIBATALKAN":
            bg_stat, fg_stat, icon = "#fee2e2", "#b91c1c", "✕"
        else:
            bg_stat, fg_stat, icon = "#dbeafe", "#1d4ed8", "↻"

        badge_status = ctk.CTkFrame(c4, fg_color=bg_stat, corner_radius=8,
                                    width=120, height=28)
        badge_status.pack(side="left")
        badge_status.pack_propagate(False)
        ctk.CTkLabel(badge_status, text=f"{icon}  {status.capitalize()}",
                     text_color=fg_stat, anchor="center",
                     font=ctk.CTkFont(family="Inter", size=11, weight="bold")
                     ).pack(expand=True, fill="both", padx=4)

        # Col 5: AKSI
        c5 = ctk.CTkFrame(row_content, fg_color="transparent")
        c5.place(relx=COL_X[5], rely=0.5, anchor="w", relwidth=COL_W[5], relheight=0.7)

        action_frame = ctk.CTkFrame(c5, fg_color="transparent")
        action_frame.pack(side="right", padx=(0, 4))

        if not is_antri and status != "BERHASIL":
            btn_retry = ctk.CTkButton(action_frame, text="↻", width=28, height=28, fg_color="transparent",
                          text_color="#727784", hover_color="#e5eeff",
                          command=lambda id_=item['id']: self._retry_sandi(id_))
            btn_retry.pack(side="left", padx=2)

        btn_view = ctk.CTkButton(action_frame, text="👁", width=28, height=28,
                                 fg_color="transparent", text_color="#727784", hover_color="#e5eeff",
                                 command=lambda: self._view_item(item))
        btn_view.pack(side="left", padx=2)

        if is_antri:
            btn_action2 = ctk.CTkButton(action_frame, text="✕", width=28, height=28,
                                        fg_color="transparent", text_color="#727784", hover_color="#ffdad6",
                                        command=lambda id_=item['id']: self._cancel_sandi(id_))
            btn_action2.pack(side="left", padx=2)

        return lbl_countdown, dt

    def refresh_antri(self):
        if self.current_tab != "ANTRI": return
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.antri_rows.clear()
        
        try:
            items = db.get_antri()
            for item in items:
                lbl_countdown, dt = self._create_row(item, is_antri=True)
                self.antri_rows.append({'id': item['id'], 'target_utc': dt.replace(tzinfo=None), 'lbl_count': lbl_countdown})
            self.lbl_footer.configure(text=f"Menampilkan {len(items)} data transmisi")
        except Exception:
            pass

    def refresh_riwayat(self):
        if self.current_tab != "RIWAYAT": return
        
        # Hentikan proses render progresif sebelumnya jika ada
        if hasattr(self, '_render_after_id') and self._render_after_id:
            self.after_cancel(self._render_after_id)
            self._render_after_id = None
        self._render_queue = []
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.antri_rows.clear()
        
        try:
            if self.date_filter_active:
                items = db.get_riwayat_by_date(self.selected_date)
            else:
                items = db.get_riwayat(limit=50)
                
            # Gunakan progressive rendering untuk menghindari freeze pada antarmuka
            self._render_queue = items
            self._render_chunk_size = 8
            self._render_next_chunk_riwayat()
            
            if self.date_filter_active:
                date_display = self._format_display_date(self.selected_date)
                self.lbl_footer.configure(text=f"Menampilkan {len(items)} data transmisi — {date_display}")
            else:
                self.lbl_footer.configure(text=f"Menampilkan {len(items)} data transmisi (terbaru)")
        except Exception:
            pass
        
        self._update_filter_buttons()

    def _render_next_chunk_riwayat(self):
        if not hasattr(self, '_render_queue') or not self._render_queue:
            return
            
        if self.current_tab != "RIWAYAT":
            self._render_queue = []
            return
            
        chunk = self._render_queue[:self._render_chunk_size]
        self._render_queue = self._render_queue[self._render_chunk_size:]
        
        for item in chunk:
            self._create_row(item, is_antri=False)
            
        if self._render_queue:
            self._render_after_id = self.after(15, self._render_next_chunk_riwayat)
        else:
            self._render_after_id = None

    def _update_filter_buttons(self):
        today = datetime.now().strftime('%Y-%m-%d')
        is_today = self.date_filter_active and self.selected_date == today
        is_all = not self.date_filter_active

        # Style for "Semua"
        if is_all:
            self.btn_clear_filter.configure(
                fg_color="#004e9f", text_color="#ffffff",
                hover_color="#003d7a", border_width=0,
                font=ctk.CTkFont(family="Inter", size=12, weight="bold")
            )
        else:
            self.btn_clear_filter.configure(
                fg_color="#ffffff", text_color="#727784",
                hover_color="#f8f9ff", border_width=1, border_color="#e2e8f0",
                font=ctk.CTkFont(family="Inter", size=12, weight="normal")
            )

        # Style for "Hari Ini"
        if is_today:
            self.btn_today.configure(
                fg_color="#004e9f", text_color="#ffffff",
                hover_color="#003d7a", border_width=0,
                font=ctk.CTkFont(family="Inter", size=12, weight="bold")
            )
        else:
            self.btn_today.configure(
                fg_color="#ffffff", text_color="#727784",
                hover_color="#f8f9ff", border_width=1, border_color="#e2e8f0",
                font=ctk.CTkFont(family="Inter", size=12, weight="normal")
            )

    def _update_countdown_loop(self):
        if self.current_tab == "ANTRI" and self.antri_rows:
            try:
                now_utc = self.ntp_manager.get_accurate_utc().replace(tzinfo=None)
                for row in self.antri_rows:
                    lbl = row['lbl_count']
                    diff = (row['target_utc'] - now_utc).total_seconds()
                    
                    if diff > 0:
                        hours, rem = divmod(int(diff), 3600)
                        mins, secs = divmod(rem, 60)
                        if hours > 0:
                            lbl.configure(text=f"⏳ {hours:02d}:{mins:02d}:{secs:02d}", text_color="#727784")
                        else:
                            lbl.configure(text=f"⏳ {mins:02d}:{secs:02d}", text_color="#727784")
                    else:
                        lbl.configure(text="Memproses...", text_color="#006a61")
            except Exception:
                pass
        self.after(1000, self._update_countdown_loop)

    def _cancel_sandi(self, id_):
        if messagebox.askyesno("Konfirmasi", "Yakin ingin membatalkan pengiriman sandi ini?"):
            db.update_status(id_, 'Dibatalkan')
            self.refresh_antri()

    def _retry_sandi(self, id_):
        if messagebox.askyesno("Konfirmasi", f"Kirim ulang sandi #{id_}?"):
            try:
                db.update_status(id_, 'Antri', error_message='', waktu_kirim_utc='', durasi_kirim_ms=0, retry_count=0)
                self.refresh_riwayat()
                if hasattr(self, 'on_date_change'):
                    self.on_date_change(self.selected_date)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal mengulang sandi: {e}")

    def _view_item(self, item):
        detail_win = ctk.CTkToplevel(self)
        detail_win.title(f"Detail Sandi #{item['id']}")
        detail_win.geometry("500x480")
        detail_win.resizable(False, False)
        detail_win.configure(fg_color="#FFFFFF")
        
        detail_win.transient(self.winfo_toplevel())
        detail_win.grab_set()

        # Center the window
        detail_win.update_idletasks()
        if detail_win.master:
            x = detail_win.master.winfo_rootx() + (detail_win.master.winfo_width() // 2) - 250
            y = detail_win.master.winfo_rooty() + (detail_win.master.winfo_height() // 2) - 240
            detail_win.geometry(f"+{x}+{y}")
            
        main_frame = ctk.CTkFrame(detail_win, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkLabel(main_frame, text=f"Detail Sandi #{item['id']}", font=ctk.CTkFont(family="Inter", size=16, weight="bold"), text_color="#0b1c30")
        header.pack(anchor="w", pady=(0, 10))

        # Helper for key-value rows
        def add_row(parent, label_text, value_text, value_color="#0b1c30"):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=4)
            label_clean = label_text.rstrip(':')
            ctk.CTkLabel(row, text=label_clean, width=100, anchor="w", text_color="#727784", font=ctk.CTkFont(family="Inter", size=12)).pack(side="left")
            ctk.CTkLabel(row, text=":", width=20, anchor="center", text_color="#727784", font=ctk.CTkFont(family="Inter", size=12, weight="bold")).pack(side="left")
            ctk.CTkLabel(row, text=value_text, anchor="w", text_color=value_color, font=ctk.CTkFont(family="Inter", size=12, weight="bold")).pack(side="left", fill="x", expand=True, padx=(10, 0))

        add_row(main_frame, "Tipe Sandi:", item.get('tipe_sandi', '-'))
        add_row(main_frame, "Status:", item.get('status', '-').capitalize(), 
                value_color="#15803d" if item.get('status') == 'Berhasil' else ("#b91c1c" if item.get('status') in ['Gagal', 'Dibatalkan'] else "#004e9f"))
        
        target_utc = item.get('target_utc', '-')
        if target_utc and target_utc != '-':
            target_utc = datetime.strptime(target_utc, '%Y-%m-%dT%H:%M:%SZ').strftime('%d %b %Y %H:%M:%S UTC')
        add_row(main_frame, "Target UTC:", target_utc)
        
        waktu_kirim = item.get('waktu_kirim_utc', '-')
        if waktu_kirim and waktu_kirim != '-':
            waktu_kirim = datetime.strptime(waktu_kirim, '%Y-%m-%dT%H:%M:%SZ').strftime('%d %b %Y %H:%M:%S UTC')
        add_row(main_frame, "Waktu Kirim:", waktu_kirim)

        error_msg = item.get('error_message')
        if error_msg:
            add_row(main_frame, "Pesan Error:", error_msg, value_color="#b91c1c")

        # Isi Sandi
        ctk.CTkLabel(main_frame, text="Isi Sandi:", anchor="w", text_color="#727784", font=ctk.CTkFont(family="Inter", size=12)).pack(anchor="w", pady=(15, 4))
        
        textbox = ctk.CTkTextbox(main_frame, height=120, fg_color="#f8f9ff", border_width=1, border_color="#c1c6d5", text_color="#0b1c30", font=ctk.CTkFont(family="JetBrains Mono", size=12))
        textbox.pack(fill="x", pady=(0, 15))
        textbox.insert("1.0", item.get('isi_sandi', '-'))
        textbox.configure(state="disabled")

        # Close Button
        btn_close = ctk.CTkButton(main_frame, text="Tutup", width=100, height=36, fg_color="#e5eeff", text_color="#004e9f", hover_color="#dce9ff", command=detail_win.destroy)
        btn_close.pack(anchor="e")

    # ── Date Filter Methods ──────────────────────────────────────
    def _format_display_date(self, date_str):
        """Format YYYY-MM-DD to a user-friendly display."""
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            today = datetime.now().strftime('%Y-%m-%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            day_names = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
            month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
                          'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
            
            day_name = day_names[dt.weekday()]
            formatted = f"{day_name}, {dt.day} {month_names[dt.month]} {dt.year}"
            
            if date_str == today:
                return f"{formatted} (Hari Ini)"
            elif date_str == yesterday:
                return f"{formatted} (Kemarin)"
            return formatted
        except Exception:
            return date_str

    def _prev_day(self):
        """Go to previous day."""
        try:
            dt = datetime.strptime(self.selected_date, '%Y-%m-%d')
            dt -= timedelta(days=1)
            self.selected_date = dt.strftime('%Y-%m-%d')
            self.date_filter_active = True
            self.btn_date_display.configure(text=self._format_display_date(self.selected_date))
            self.refresh_riwayat()
            if hasattr(self, 'on_date_change'):
                self.on_date_change(self.selected_date)
        except Exception:
            pass

    def _next_day(self):
        """Go to next day."""
        try:
            dt = datetime.strptime(self.selected_date, '%Y-%m-%d')
            dt += timedelta(days=1)
            if dt.date() <= datetime.now().date():
                self.selected_date = dt.strftime('%Y-%m-%d')
                self.date_filter_active = True
                self.btn_date_display.configure(text=self._format_display_date(self.selected_date))
                self.refresh_riwayat()
                if hasattr(self, 'on_date_change'):
                    self.on_date_change(self.selected_date)
        except Exception:
            pass

    def _go_today(self):
        self.selected_date = datetime.now().strftime('%Y-%m-%d')
        self.date_filter_active = True
        self.btn_date_display.configure(text=self._format_display_date(self.selected_date))
        self.refresh_riwayat()
        if hasattr(self, 'on_date_change'):
            self.on_date_change(self.selected_date)

    def _clear_date_filter(self):
        """Clear date filter — show all recent."""
        self.date_filter_active = False
        self.selected_date = datetime.now().strftime('%Y-%m-%d')
        self.btn_date_display.configure(text=self._format_display_date(self.selected_date))
        self.refresh_riwayat()
        if hasattr(self, 'on_date_change'):
            self.on_date_change(None)

    def _open_calendar(self):
        """Open a modern, borderless calendar popup for date selection."""
        import tkinter as tk

        cal_win = tk.Toplevel(self)
        cal_win.title("Pilih Tanggal")
        cal_win.geometry("260x300")
        cal_win.overrideredirect(True) # Remove OS window borders
        cal_win.attributes('-topmost', True)
        cal_win.configure(bg="#FFFFFF", highlightbackground="#cbd5e1", highlightthickness=1)

        # Center exactly below the button
        cal_win.update_idletasks()
        x = self.btn_date_display.winfo_rootx()
        y = self.btn_date_display.winfo_rooty() + self.btn_date_display.winfo_height() + 2
        cal_win.geometry(f"+{x}+{y}")
        
        # Parse current selected date
        current_dt = datetime.strptime(self.selected_date, '%Y-%m-%d')
        self._cal_year = current_dt.year
        self._cal_month = current_dt.month
        self._cal_selected = self.selected_date

        # Header with month/year navigation
        cal_header = tk.Frame(cal_win, bg="#004e9f", height=40)
        cal_header.pack(fill="x")
        cal_header.pack_propagate(False)

        self._cal_lbl = tk.Label(cal_header, text="", font=("Inter", 12, "bold"),
                                 fg="#ffffff", bg="#004e9f")
        self._cal_lbl.pack(side="left", padx=12)

        btn_next = tk.Button(cal_header, text="▶", font=("Inter", 10), fg="#ffffff", bg="#004e9f",
                             activebackground="#003d7a", activeforeground="#ffffff",
                             bd=0, cursor="hand2", padx=6, pady=2,
                             command=lambda: self._cal_nav(cal_win, 1))
        btn_next.pack(side="right", padx=4)
        btn_prev = tk.Button(cal_header, text="◀", font=("Inter", 10), fg="#ffffff", bg="#004e9f",
                             activebackground="#003d7a", activeforeground="#ffffff",
                             bd=0, cursor="hand2", padx=6, pady=2,
                             command=lambda: self._cal_nav(cal_win, -1))
        btn_prev.pack(side="right", padx=4)

        # Calendar grid container
        self._cal_body = tk.Frame(cal_win, bg="#FFFFFF")
        self._cal_body.pack(fill="both", expand=True, padx=5, pady=5)

        self._cal_win = cal_win
        self._render_calendar(cal_win)
        
        # Close popup if user clicks elsewhere
        cal_win.bind("<FocusOut>", lambda e: cal_win.destroy())
        cal_win.focus_set()

    def _cal_nav(self, cal_win, direction):
        self._cal_month += direction
        if self._cal_month > 12:
            self._cal_month = 1
            self._cal_year += 1
        elif self._cal_month < 1:
            self._cal_month = 12
            self._cal_year -= 1
        self._render_calendar(cal_win)

    def _render_calendar(self, cal_win):
        import tkinter as tk
        import calendar

        month_names_full = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                           'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

        self._cal_lbl.configure(text=f"{month_names_full[self._cal_month]} {self._cal_year}")

        # Clear previous grid
        for widget in self._cal_body.winfo_children():
            widget.destroy()

        day_headers = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min']
        for col, dh in enumerate(day_headers):
            lbl = tk.Label(self._cal_body, text=dh, font=("Inter", 9, "bold"),
                           fg="#727784", bg="#FFFFFF", width=3)
            lbl.grid(row=0, column=col, padx=1, pady=(0, 4))

        cal = calendar.monthcalendar(self._cal_year, self._cal_month)
        today_str = datetime.now().strftime('%Y-%m-%d')

        for row_idx, week in enumerate(cal):
            for col_idx, day in enumerate(week):
                if day == 0:
                    tk.Label(self._cal_body, text="", width=3, bg="#FFFFFF").grid(
                        row=row_idx+1, column=col_idx, padx=1, pady=1)
                    continue

                date_str = f"{self._cal_year}-{self._cal_month:02d}-{day:02d}"

                if date_str == self._cal_selected:
                    bg_color = "#004e9f"
                    txt_color = "#ffffff"
                elif date_str == today_str:
                    bg_color = "#e5eeff"
                    txt_color = "#004e9f"
                else:
                    bg_color = "#FFFFFF"
                    txt_color = "#0b1c30"

                is_future = date_str > today_str

                btn = tk.Button(
                    self._cal_body, text=str(day), width=3, height=1,
                    font=("Inter", 10),
                    fg="#c1c6d5" if is_future else txt_color,
                    bg=bg_color,
                    activebackground="#dce9ff" if not is_future else bg_color,
                    activeforeground=txt_color,
                    bd=0, relief="flat", cursor="hand2" if not is_future else "arrow",
                    command=(lambda d=date_str: self._cal_pick(d)) if not is_future else None
                )
                btn.grid(row=row_idx+1, column=col_idx, padx=1, pady=1)

    def _cal_pick(self, date_str):
        self.selected_date = date_str
        self.date_filter_active = True
        self.btn_date_display.configure(text=self._format_display_date(self.selected_date))
        try:
            self._cal_win.destroy()
        except Exception:
            pass
        self.refresh_riwayat()
        if hasattr(self, 'on_date_change'):
            self.on_date_change(self.selected_date)


