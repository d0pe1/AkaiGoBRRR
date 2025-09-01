# MasteratorGui.py
import tkinter as tk
import math
from dataclasses import dataclass

# ---- Device map (Akai MIDImix) ----
CC_MAP = {
    "knob_row_1": [16, 20, 24, 28, 46, 50, 54, 58],
    "knob_row_2": [17, 21, 25, 29, 47, 51, 55, 59],
    "knob_row_3": [18, 22, 26, 30, 48, 52, 56, 60],
    "faders":     [19, 23, 27, 31, 49, 53, 57, 61],
    "master":     127,
}
NOTES = {
    "mute":   [1, 4, 7, 10, 13, 16, 19, 22],  # base
    "solo":   [2, 5, 8, 11, 14, 17, 20, 23],  # device sends while SOLO held
    "recarm": [3, 6, 9, 12, 15, 18, 21, 24],  # base; shifted = +32 (your hook)
}
SHIFT_OFFSET = 32

# ---- visuals ----
COL_BG       = "#111418"
COL_SURFACE  = "#1a1f24"
COL_GRID     = "#2c3137"
COL_TEXT     = "#d9dde3"
COL_OFF      = "#2a2f34"
COL_ON       = "#9be9a8"
COL_INACTIVE = "#5a7a62"
BANK_COLORS  = ["#6ee7b7", "#93c5fd", "#fca5a5", "#fcd34d"]  # A,B,C,D

@dataclass
class BankSnapshot:
    name: str
    toggle_states: dict[int, bool]   # note -> bool
    cc_values: dict[int, int]        # cc   -> 0..127
    note27_on: bool
    active_bank: int                 # 0..3 (A..D)

class MasteratorGUI:
    """Detailed view (current bank) + Micro view (all banks)."""
    def __init__(self, root: tk.Tk):
        self.root = root
        self.canvas = tk.Canvas(root, bg=COL_BG, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.root.title("MIDI Masterator — Bank Monitor")

        # Micro toggle
        self.toolbar = tk.Frame(root, bg=COL_BG)
        self.toolbar.place(x=8, y=8)
        self.micro_var = tk.IntVar(value=0)
        tk.Checkbutton(self.toolbar, text="Micro", variable=self.micro_var,
                       command=self._invalidate, bg=COL_BG, fg=COL_TEXT,
                       activebackground=COL_BG, activeforeground=COL_TEXT,
                       selectcolor=COL_BG, highlightthickness=0).pack(side="left")

        self.root.bind("<Configure>", lambda e: self._invalidate())

        self._latest_snapshot: BankSnapshot | None = None
        self._bank_snaps: list[BankSnapshot | None] = [None]*4
        self._dirty = True

    # ---------- producer API ----------
    def set_snapshot(self, snapshot: BankSnapshot):
        self._latest_snapshot = snapshot
        self._bank_snaps[snapshot.active_bank] = snapshot
        self._dirty = True

    def set_bank_snapshot(self, snapshot: BankSnapshot):
        self._bank_snaps[snapshot.active_bank] = snapshot
        self._dirty = True

    def start_render_loop(self, fps: int = 3):
        delay = max(1, int(1000 / max(1, fps)))
        def tick():
            if self._dirty:
                self._draw()
                self._dirty = False
            self.root.after(delay, tick)
        tick()

    # ---------- internals ----------
    def _invalidate(self): self._dirty = True
    def _accent_for(self, idx: int): return BANK_COLORS[idx]

    # Tk angle -> canvas point (y is down)
    def _tk_angle_to_point(self, cx, cy, r, angle_deg):
        theta = math.radians(angle_deg)
        return cx + r*math.cos(theta), cy - r*math.sin(theta)

    def _draw(self):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width() or 800
        h = c.winfo_height() or 600
        if self.micro_var.get():
            self._draw_micro(w, h)
        else:
            self._draw_detail(w, h)

    # ===== Detailed single-bank view =====
    def _draw_detail(self, w, h):
        s = self._latest_snapshot
        if not s:
            self.canvas.create_text(w//2, h//2, text="Waiting for MIDI…", fill=COL_TEXT, font=("Segoe UI", 14))
            return
        c = self.canvas
        accent = self._accent_for(s.active_bank)

        base_cell, base_gap, base_pad = 96, 12, 16
        needed_w = base_pad*2 + 8*base_cell + 7*base_gap + 160
        needed_h = base_pad*2 + 3*base_cell + 2*base_gap + 260
        S = max(0.6, min(w/needed_w, h/needed_h))

        PAD = base_pad * S; CELL = base_cell * S; GAP = base_gap * S
        KNOB_R = CELL * 0.33; FADER_W = 20 * S; FADER_H = 160 * S
        left = PAD; top = PAD + 28 * S

        # Header + bank squares
        c.create_text(PAD+60, 12, anchor="nw",
                      text=f"{s.name} | Shift(27)={'ON' if s.note27_on else 'OFF'}",
                      fill=COL_TEXT, font=("Segoe UI", int(14*S), "bold"))
        self._bank_selector(c, w - PAD - 4*50*S, 12, int(50*S), int(26*S), s.active_bank)

        # Knob rows
        for r_idx, key in enumerate(["knob_row_1","knob_row_2","knob_row_3"]):
            y = top + r_idx*(CELL+GAP)
            for i, cc in enumerate(CC_MAP[key]):
                x = left + i*(CELL+GAP)
                self._knob(c, x, y, CELL, KNOB_R, cc, s.cc_values.get(cc, 0), accent)

        # Buttons (MUTE uses SOLO for shift; REC uses +32)
        strip_top = top + 3*(CELL+GAP) + 10*S
        dx = CELL + GAP
        self._dual_row_buttons(c, left+8*S, strip_top, "MUTE",
                               base_notes=NOTES["mute"], shift_notes=NOTES["solo"],
                               s=s, dx=dx, cell=CELL, S=S, accent=accent)
        self._dual_row_buttons(c, left+8*S, strip_top+68*S, "REC",
                               base_notes=NOTES["recarm"], shift_notes=None, use_offset=True,
                               s=s, dx=dx, cell=CELL, S=S, accent=accent)

        # Faders + labels
        for i, cc in enumerate(CC_MAP["faders"]):
            x = left + i*dx
            val = s.cc_values.get(cc, 0)
            self._fader(c, x + (CELL/2 - FADER_W/2), strip_top+140*S, FADER_W, FADER_H, val, accent)
            c.create_text(x+CELL/2, strip_top+140*S+FADER_H+16*S,
                          text=str(i+1), fill=COL_TEXT, font=("Segoe UI", int(10*S)))

        # Master
        mx = left + 8*dx + 36*S; m_top = strip_top
        self._panel(c, mx-24*S, m_top-6*S, 88*S, FADER_H+100*S)
        c.create_text(mx+20*S, m_top-2*S, text="MASTER", fill=COL_TEXT, font=("Segoe UI", int(10*S), "bold"))
        self._fader(c, mx, m_top+24*S, FADER_W, FADER_H, s.cc_values.get(CC_MAP["master"], 0), accent)

    # ===== Micro ALL-banks view =====
    def _draw_micro(self, w, h):
        c = self.canvas
        PAD = 14; cols = 2; rows = 2
        tile_w = (w - PAD*(cols+1)) / cols
        tile_h = (h - PAD*(rows+1)) / rows
        for idx in range(4):
            r = idx // cols; col = idx % cols
            x0 = PAD + col*(tile_w + PAD); y0 = PAD + r*(tile_h + PAD)
            self._draw_bank_micro_tile(c, x0, y0, tile_w, tile_h, idx)

    def _draw_bank_micro_tile(self, c, x, y, w, h, idx):
        snap = self._bank_snaps[idx]
        accent = self._accent_for(idx)
        self._panel(c, x, y, w, h)

        label = "ABCD"[idx]
        c.create_text(x+10, y+8, anchor="nw", text=f"Bank {label}", fill=COL_TEXT, font=("Segoe UI", 11, "bold"))
        if snap:
            c.create_text(x+w-10, y+10, anchor="ne",
                          text=("Shift ON" if snap.note27_on else "Shift OFF"),
                          fill=COL_TEXT, font=("Segoe UI", 9))

        left = x + 12; top = y + 30
        width = w - 24; height = h - 42
        cols = 8; col_w = width / cols
        ccvals = snap.cc_values if snap else {}
        toggles = snap.toggle_states if snap else {}
        shift_on = snap.note27_on if snap else False

        for i in range(cols):
            cx = left + i*col_w
            gx = cx + col_w*0.1; gw = col_w*0.55; bx = cx + col_w*0.7
            self._bar_triplet(c, gx, top+8, gw, height*0.55, i, ccvals, accent)
            self._bar_single(c, bx, top+8, col_w*0.2, height*0.55,
                             self._cc_for("faders", i, ccvals), accent)

            sq = min(col_w*0.22, 14); gap = sq*0.25; by = top + 8 + height*0.62
            m_base = toggles.get(NOTES["mute"][i], False)
            m_sh   = toggles.get(NOTES["solo"][i], False)              # SOLO for MUTE shift
            r_base = toggles.get(NOTES["recarm"][i], False)
            r_sh   = toggles.get(NOTES["recarm"][i] + SHIFT_OFFSET, False)
            self._tiny_square(c, cx+col_w*0.12,        by,           sq, m_base, not shift_on, accent)
            self._tiny_square(c, cx+col_w*0.12+sq+gap, by,           sq, m_sh,    shift_on,    accent)
            self._tiny_square(c, cx+col_w*0.12,        by+sq+gap,    sq, r_base, not shift_on, accent)
            self._tiny_square(c, cx+col_w*0.12+sq+gap, by+sq+gap,    sq, r_sh,    shift_on,    accent)

    # ===== helpers =====
    def _cc_for(self, key, i, ccvals): return ccvals.get(CC_MAP[key][i], 0)

    def _bar_triplet(self, c, x, y, w, h, i, ccvals, accent):
        vals = [self._cc_for("knob_row_1", i, ccvals),
                self._cc_for("knob_row_2", i, ccvals),
                self._cc_for("knob_row_3", i, ccvals)]
        bw = w/3 - 2
        for k, v in enumerate(vals):
            vx = x + k*(bw+2)
            self._bar_single(c, vx, y, bw, h, v, accent)

    def _bar_single(self, c, x, y, w, h, value, accent):
        c.create_rectangle(x, y, x+w, y+h, outline=COL_GRID, fill=COL_SURFACE)
        t = (value or 0) / 127.0
        yy = y + (1.0 - t) * h
        c.create_rectangle(x+1, yy, x+w-1, y+h-1, outline="", fill=accent)

    def _tiny_square(self, c, x, y, s, on, active_layer, accent):
        c.create_rectangle(x, y, x+s, y+s, outline=COL_GRID, fill=COL_SURFACE)
        fill = COL_ON if on else COL_OFF
        if not active_layer:
            fill = COL_INACTIVE if on else COL_OFF
        c.create_rectangle(x+2, y+2, x+s-2, y+s-2,
                           outline=accent if active_layer else COL_GRID,
                           width=1, fill=fill)

    def _panel(self, c, x, y, w, h):
        c.create_rectangle(x, y, x+w, y+h, outline=COL_GRID, fill=COL_SURFACE)

    def _bank_selector(self, c, x, y, w, h, active_idx: int):
        labels = "ABCD"
        for i in range(4):
            bx = x + i*w; color = BANK_COLORS[i]
            self._panel(c, bx, y, w-6, h)
            self.canvas.create_rectangle(bx+6, y+6, bx+w-12, y+h-6,
                                         outline=color if i == active_idx else COL_GRID, width=2)
            self.canvas.create_text(bx+(w-6)/2, y+h/2, text=labels[i],
                                    fill=COL_TEXT, font=("Segoe UI", int(h*0.5), "bold"))

    def _knob(self, c, x, y, cell, r, cc, value, accent):
        self._panel(c, x, y, cell, cell)
        cx = x + cell/2; cy = y + cell/2
        c.create_oval(cx-r, cy-r, cx+r, cy+r, outline=COL_GRID, width=2, fill=COL_SURFACE)
        START_DEG = 210.0; t = float(value)/127.0; sweep = 300.0 * t
        c.create_arc(cx-r, cy-r, cx+r, cy+r, start=START_DEG, extent=-sweep,
                     style="arc", width=6, outline=accent)
        end_deg = (START_DEG - sweep) % 360.0
        px, py = self._tk_angle_to_point(cx, cy, r-6, end_deg)
        c.create_line(cx, cy, px, py, fill=accent, width=3)
        c.create_text(cx, y+cell-12, text=f"CC {cc} ({int(value)})", fill=COL_TEXT, font=("Segoe UI", 9))

    def _fader(self, c, x, y, fw, fh, value, accent):
        self._panel(c, x-10, y-8, fw+20, fh+16)
        c.create_rectangle(x, y, x+fw, y+fh, outline=COL_GRID, fill=COL_SURFACE)
        t = (value or 0)/127.0; knob_y = y + (1.0 - t) * (fh-14)
        c.create_rectangle(x-2, knob_y, x+fw+2, knob_y+14, outline="", fill=accent)


    def _dual_row_buttons(self, c, left, top, label, base_notes, shift_notes=None, use_offset=False, s=None, dx=0, cell=0, S=1, accent=COL_ON):
        """
        Draws two stacked button rows (base + shift layer).
        base_notes: list of note numbers for row 1
        shift_notes: list of note numbers for row 2 (if None, uses base+SHIFT_OFFSET if use_offset=True)
        use_offset: if True, second row note = base_note + SHIFT_OFFSET
        s: BankSnapshot
        """
        if not s:
            return

        for i, base_note in enumerate(base_notes):
            x = left + i * dx
            base_on = s.toggle_states.get(base_note, False)

            # Second row note numbers & states
            if shift_notes:
                shift_note = shift_notes[i]
            elif use_offset:
                shift_note = base_note + SHIFT_OFFSET
            else:
                shift_note = None

            if shift_note is not None:
                shift_on = s.toggle_states.get(shift_note, False)
            else:
                shift_on = False

            # Which layer is currently "active"
            active_layer_base = not s.note27_on
            active_layer_shift = s.note27_on

            # Base row
            self._panel(c, x, top, cell, 28 * S)
            fill_base = COL_ON if base_on else COL_OFF
            if not active_layer_base:
                fill_base = COL_INACTIVE if base_on else COL_OFF
            c.create_rectangle(x+4*S, top+4*S, x+cell-4*S, top+24*S,
                               outline=accent if active_layer_base else COL_GRID,
                               width=1, fill=fill_base)

            # Shift row
            self._panel(c, x, top + 32 * S, cell, 28 * S)
            fill_shift = COL_ON if shift_on else COL_OFF
            if not active_layer_shift:
                fill_shift = COL_INACTIVE if shift_on else COL_OFF
            c.create_rectangle(x+4*S, top+36*S, x+cell-4*S, top+56*S,
                               outline=accent if active_layer_shift else COL_GRID,
                               width=1, fill=fill_shift)

        # Group label
        c.create_text(left - 50*S, top + 14*S, text=label, fill=COL_TEXT,
                      font=("Segoe UI", int(10*S), "bold"), anchor="w")
