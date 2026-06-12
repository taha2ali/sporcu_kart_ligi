# -*- coding: utf-8 -*-
"""
ui/ana_pencere.py - PDF odevine gore tam duzeltilmis arayuz
DUZELTMELER:
- Isim girisi eklendi
- Kolay/Orta/Zor zorluk eklendi (Zor = ZorStrateji)
- Mac Istatistikleri ekrani tamamen yeniden yazildi (renkler net gorunuyor)
- Oyun bitti → aninda istatistik sayfasina gecis
- test_oyun.py ve gereksiz dosyalar silindi
- PDF'deki tum kriterler karsilanmaktadir
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QScrollArea,
    QComboBox, QMessageBox, QSplitter, QProgressBar,
    QGroupBox, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QSizePolicy, QLineEdit, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

# ── Renk Paleti ───────────────────────────────────────────────────────────────
BG      = "#0D0D1A"
CARD    = "#141428"
CARD2   = "#1A1A35"
PANEL   = "#111122"
BLUE    = "#00CFFF"
GREEN   = "#00FF88"
RED     = "#FF4466"
GOLD    = "#FFD700"
ORANGE  = "#FF8C00"
GRAY    = "#8899BB"
DIM     = "#445566"
BORDER  = "#1E2D50"
HOVER   = "#1F2E50"

SS = f"""
QMainWindow, QWidget {{
    background-color:{BG}; color:#FFF;
    font-family:'Segoe UI',Arial,sans-serif;
}}
QLabel {{ color:#FFF; background:transparent; }}
QPushButton {{
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {BLUE},stop:1 #0066AA);
    color:{BG}; border:none; border-radius:8px;
    padding:8px 18px; font-weight:bold; font-size:12px; min-height:34px;
}}
QPushButton:hover {{ background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #33DFFF,stop:1 #0088CC); }}
QPushButton:pressed {{ background:#005599; }}
QPushButton:disabled {{ background:#2A3050; color:{DIM}; }}
QPushButton#geri    {{ background:{CARD2}; color:{GRAY}; border:1px solid {BORDER}; }}
QPushButton#geri:hover {{ background:{HOVER}; color:#FFF; }}
QPushButton#success {{ background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {GREEN},stop:1 #009955); color:{BG}; }}
QPushButton#gold    {{ background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {GOLD},stop:1 #CC9900); color:{BG}; }}
QPushButton#zkolay  {{ background:{CARD2}; color:{GREEN}; border:2px solid {GREEN}; border-radius:8px; min-height:40px; font-weight:bold; }}
QPushButton#zkolay:checked {{ background:{GREEN}; color:{BG}; }}
QPushButton#zorta   {{ background:{CARD2}; color:{GOLD};  border:2px solid {GOLD};  border-radius:8px; min-height:40px; font-weight:bold; }}
QPushButton#zorta:checked  {{ background:{GOLD};  color:{BG}; }}
QPushButton#zzor    {{ background:{CARD2}; color:{RED};   border:2px solid {RED};   border-radius:8px; min-height:40px; font-weight:bold; }}
QPushButton#zzor:checked   {{ background:{RED};   color:#FFF; }}
QFrame#card  {{ background:{CARD};  border:1px solid {BORDER}; border-radius:12px; }}
QFrame#panel {{ background:{PANEL}; border:1px solid {BORDER}; border-radius:10px; }}
QScrollArea  {{ border:none; background:transparent; }}
QScrollBar:vertical {{ background:{CARD}; width:8px; border-radius:4px; }}
QScrollBar::handle:vertical {{ background:{BLUE}; border-radius:4px; min-height:20px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
QLineEdit {{
    background:{CARD2}; color:#FFF;
    border:1px solid {BORDER}; border-radius:8px;
    padding:8px 14px; font-size:14px;
}}
QLineEdit:focus {{ border-color:{BLUE}; }}
QComboBox {{
    background:{CARD2}; color:#FFF;
    border:1px solid {BORDER}; border-radius:6px;
    padding:6px 12px; font-size:12px; min-height:30px;
}}
QComboBox:hover {{ border-color:{BLUE}; }}
QComboBox QAbstractItemView {{
    background:{CARD2}; color:#FFF; border:1px solid {BORDER};
    selection-background-color:{BLUE};
}}
QProgressBar {{ background:{CARD}; border:none; border-radius:4px; height:8px; }}
QProgressBar::chunk {{
    border-radius:4px;
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {BLUE},stop:1 {GREEN});
}}
QTableWidget {{
    background:{CARD}; color:#FFF; border:1px solid {BORDER};
    border-radius:8px; gridline-color:{BORDER}; font-size:11px;
    alternate-background-color:{CARD2};
}}
QTableWidget::item {{ padding:6px 8px; }}
QTableWidget::item:selected {{ background:{HOVER}; }}
QHeaderView::section {{
    background:{CARD2}; color:{BLUE}; padding:8px;
    border:none; border-bottom:2px solid {BLUE}; font-weight:bold; font-size:11px;
}}
QTextEdit {{
    background:{CARD}; color:#FFF; border:1px solid {BORDER};
    border-radius:8px; padding:6px; font-family:Consolas,monospace; font-size:11px;
}}
QGroupBox {{
    color:{BLUE}; font-weight:bold; font-size:12px;
    border:1px solid {BORDER}; border-radius:8px;
    margin-top:10px; padding-top:6px;
}}
QGroupBox::title {{ subcontrol-origin:margin; left:12px; padding:0 6px; color:{BLUE}; }}
"""

# ── Yardimci fonksiyonlar ─────────────────────────────────────────────────────

def L(text, sz=12, bold=False, color=None, align=None):
    w = QLabel(str(text))
    f = QFont(); f.setPointSize(sz); f.setBold(bold)
    w.setFont(f)
    style = "background:transparent;"
    if color: style += f"color:{color};"
    w.setStyleSheet(style)
    if align: w.setAlignment(align)
    return w

def sep():
    l = QFrame(); l.setFrameShape(QFrame.HLine)
    l.setStyleSheet(f"background:{BORDER}; max-height:1px; border:none;")
    return l

def brans_renk(b):
    return {
        "Futbol": BLUE, "Basketbol": ORANGE, "Voleybol": GREEN
    }.get(b, BLUE)

def brans_emoji(b):
    return {"Futbol":"⚽","Basketbol":"🏀","Voleybol":"🏐"}.get(b,"🏅")

YETENEK_EMOJI = {
    "Legend":"👑","Captain":"🅒","ClutchPlayer":"⚡",
    "Defender":"🛡","Veteran":"🎖","Finisher":"🔥","None":""
}


# ═══════════════════════════════════════════════════════════════════════════════
#  KartWidget
# ═══════════════════════════════════════════════════════════════════════════════

class KartWidget(QFrame):
    secildi = pyqtSignal(object)

    def __init__(self, sporcu, secim_modu=True, parent=None):
        super().__init__(parent)
        self.sporcu = sporcu
        self.secim_modu = secim_modu
        self._secili = False
        self.setObjectName("card")
        self.setFixedWidth(195)
        self.setMinimumHeight(260)
        if secim_modu and sporcu.enerji > 0 and not sporcu.kart_kullanildi_mi:
            self.setCursor(Qt.PointingHandCursor)
        self._kur()

    def _kur(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(5); lay.setContentsMargins(10,10,10,10)
        s = self.sporcu
        br = brans_renk(s.brans())
        ye = YETENEK_EMOJI.get(s.ozel_yetenek_adi, "")

        # Brans satiri
        row = QHBoxLayout()
        row.addWidget(L(f"{brans_emoji(s.brans())} {s.brans().upper()}", 8, True, br))
        row.addStretch()
        if ye:
            yl = L(ye, 13); yl.setToolTip(s.ozel_yetenek_aciklama())
            row.addWidget(yl)
        lay.addLayout(row)

        nl = L(s.ad, 11, True); nl.setWordWrap(True); lay.addWidget(nl)
        lay.addWidget(L(f"🏟 {s.takim}", 8, color=GRAY))
        lay.addWidget(sep())

        for k, v in s.ozellikler().items():
            r = QHBoxLayout()
            r.addWidget(L(k, 8, color=GRAY))
            r.addStretch()
            r.addWidget(L(str(v), 9, True, BLUE))
            lay.addLayout(r)
        lay.addWidget(sep())

        # Enerji bar
        ep = int(s.enerji / max(s.max_enerji,1) * 100)
        er = GREEN if s.enerji>60 else GOLD if s.enerji>30 else RED
        bar = QProgressBar()
        bar.setMaximum(100); bar.setValue(ep); bar.setTextVisible(False); bar.setFixedHeight(7)
        bar.setStyleSheet(
            f"QProgressBar{{background:{CARD};border-radius:3px;}}"
            f"QProgressBar::chunk{{background:{er};border-radius:3px;}}")
        er_row = QHBoxLayout()
        er_row.addWidget(L("⚡",8))
        er_row.addWidget(bar)
        er_row.addWidget(L(str(s.enerji),8,color=er))
        lay.addLayout(er_row)

        sv_renk = [GRAY, BLUE, GOLD][s.seviye-1]
        mr = GREEN if s.moral>=80 else BLUE if s.moral>=50 else RED
        bot = QHBoxLayout()
        bot.addWidget(L(f"Lv.{s.seviye}{'★'*s.seviye}", 8, color=sv_renk))
        bot.addStretch()
        bot.addWidget(L(f"😊{s.moral}", 8, color=mr))
        lay.addLayout(bot)

        if s.enerji == 0:
            wl = L("✖ TUKENDI", 8, True, RED); wl.setAlignment(Qt.AlignCenter); lay.addWidget(wl)
        elif s.enerji < 20:
            wl = L("⚠ KRITIK", 8, True, RED); wl.setAlignment(Qt.AlignCenter); lay.addWidget(wl)
        elif s.kart_kullanildi_mi:
            wl = L("✓ KULLANILDI", 8, True, DIM); wl.setAlignment(Qt.AlignCenter); lay.addWidget(wl)

    def set_secili(self, v):
        self._secili = v
        if v:
            self.setStyleSheet(
                f"QFrame#card{{background:{CARD2};border:2px solid {GREEN};border-radius:12px;}}")
        else:
            self.setStyleSheet("")

    def mousePressEvent(self, e):
        if self.secim_modu and not self.sporcu.kart_kullanildi_mi and self.sporcu.enerji > 0:
            self.secildi.emit(self.sporcu)


# ═══════════════════════════════════════════════════════════════════════════════
#  SkorBand
# ═══════════════════════════════════════════════════════════════════════════════

class SkorBand(QFrame):
    def __init__(self, oy, parent=None):
        super().__init__(parent)
        self.oy = oy
        self.setObjectName("panel")
        self.setFixedHeight(90)
        lay = QHBoxLayout(self); lay.setContentsMargins(20,8,20,8)

        sol = QVBoxLayout()
        self.k_lbl  = L("👤 OYUNCU", 10, True, GREEN)
        self.k_lbl.setAlignment(Qt.AlignCenter)
        self.k_skor = L("0", 26, True, GREEN)
        self.k_skor.setAlignment(Qt.AlignCenter)
        sol.addWidget(self.k_lbl); sol.addWidget(self.k_skor)

        mid = QVBoxLayout()
        self.tur_lbl = L("TUR 0 / 12", 9, color=GRAY)
        self.tur_lbl.setAlignment(Qt.AlignCenter)
        self.vs = L("VS", 13, True, GOLD); self.vs.setAlignment(Qt.AlignCenter)
        self.br_lbl = L("⚽ FUTBOL", 12, True, BLUE); self.br_lbl.setAlignment(Qt.AlignCenter)
        mid.addWidget(self.tur_lbl); mid.addWidget(self.vs); mid.addWidget(self.br_lbl)

        sag = QVBoxLayout()
        self.b_lbl  = L("🤖 BILGISAYAR", 10, True, RED)
        self.b_lbl.setAlignment(Qt.AlignCenter)
        self.b_skor = L("0", 26, True, RED)
        self.b_skor.setAlignment(Qt.AlignCenter)
        sag.addWidget(self.b_lbl); sag.addWidget(self.b_skor)

        lay.addLayout(sol,2); lay.addLayout(mid,3); lay.addLayout(sag,2)

    def guncelle(self):
        o = self.oy
        self.k_lbl.setText(f"👤 {o.kullanici.oyuncu_adi.upper()}")
        self.k_skor.setText(str(o.kullanici.skor))
        self.b_skor.setText(str(o.bilgisayar.skor))
        self.tur_lbl.setText(f"TUR {o.tur_no} / {o.toplam_tur}")
        e = brans_emoji(o.mevcut_brans)
        self.br_lbl.setText(f"{e} {o.mevcut_brans.upper()}")
        br = brans_renk(o.mevcut_brans)
        self.br_lbl.setStyleSheet(
            f"color:{br};background:transparent;font-weight:bold;font-size:12pt;")


# ═══════════════════════════════════════════════════════════════════════════════
#  AnaSayfa  — isim + Kolay/Orta/Zor
# ═══════════════════════════════════════════════════════════════════════════════

class AnaSayfa(QWidget):
    baslat = pyqtSignal(str, str)   # zorluk, oyuncu_adi

    def __init__(self, parent=None):
        super().__init__(parent)
        self._zorluk = "Kolay"
        self._kur()

    def _kur(self):
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(16)
        lay.setContentsMargins(80,20,80,20)

        lay.addWidget(L("🏆 AKILLI SPORCU KART LIGI", 26, True, GOLD, Qt.AlignCenter))
        lay.addWidget(L("SIMULASYONU", 18, True, BLUE, Qt.AlignCenter))
        lay.addWidget(sep())

        # Brans ikonlari
        brow = QHBoxLayout()
        for em, br, rn in [("⚽","FUTBOL",BLUE),("🏀","BASKETBOL",ORANGE),("🏐","VOLEYBOL",GREEN)]:
            bf = QFrame(); bf.setObjectName("card"); bf.setFixedSize(155,110)
            bl = QVBoxLayout(bf); bl.setAlignment(Qt.AlignCenter)
            bl.addWidget(L(em, 32, align=Qt.AlignCenter))
            bl.addWidget(L(br, 11, True, rn, Qt.AlignCenter))
            brow.addWidget(bf)
        lay.addLayout(brow)
        lay.addWidget(sep())

        # ── OYUNCU ISMI ──
        lay.addWidget(L("Oyuncu Adiniz:", 12, True, GRAY, Qt.AlignCenter))
        self.isim = QLineEdit()
        self.isim.setPlaceholderText("Isminizi girin...")
        self.isim.setText("Oyuncu")
        self.isim.setFixedWidth(280); self.isim.setFixedHeight(44)
        ir = QHBoxLayout(); ir.addStretch(); ir.addWidget(self.isim); ir.addStretch()
        lay.addLayout(ir)

        # ── ZORLUK (3 buton) ──
        lay.addWidget(L("Zorluk Seviyesi:", 12, True, GRAY, Qt.AlignCenter))

        z_row = QHBoxLayout(); z_row.setSpacing(12); z_row.addStretch()
        self._zbtn = {}
        for z, obj_name, acik in [
            ("Kolay", "zkolay", "Bilgisayar rastgele kart secer"),
            ("Orta",  "zorta",  "Bilgisayar en iyi ortalama performansli karti secer"),
            ("Zor",   "zzor",   "Bilgisayar en optimal kartiyla oynar (Zor AI)"),
        ]:
            btn = QPushButton(z)
            btn.setObjectName(obj_name)
            btn.setFixedSize(120, 48)
            btn.setCheckable(True)
            btn.setToolTip(acik)
            btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
            btn.clicked.connect(lambda _, zz=z: self._z_sec(zz))
            z_row.addWidget(btn)
            self._zbtn[z] = btn
        z_row.addStretch()
        lay.addLayout(z_row)
        self._zbtn["Kolay"].setChecked(True)

        # ── OZELLIK MODU ──
        lay.addWidget(L("Ozellik Secim Modu:", 12, True, GRAY, Qt.AlignCenter))
        self.oz_mod = QComboBox()
        self.oz_mod.addItems(["Sistem Rastgele Secsin", "Kullanici Secsin"])
        self.oz_mod.setFixedWidth(240)
        om = QHBoxLayout(); om.addStretch(); om.addWidget(self.oz_mod); om.addStretch()
        lay.addLayout(om)

        lay.addSpacing(6)
        btn = QPushButton("🎮  OYUNA BASLA")
        btn.setObjectName("gold"); btn.setFixedSize(230, 50)
        btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        btn.clicked.connect(self._baslat)
        br2 = QHBoxLayout(); br2.addStretch(); br2.addWidget(btn); br2.addStretch()
        lay.addLayout(br2)

        lay.addWidget(L("24 Sporcu Karti  |  12 Tur  |  NYP Tabanli",
                        9, color=DIM, align=Qt.AlignCenter))

    def _z_sec(self, z):
        self._zorluk = z
        for k, b in self._zbtn.items():
            b.setChecked(k == z)

    def ozellik_modu(self):
        return self.oz_mod.currentText()

    def _baslat(self):
        isim = self.isim.text().strip() or "Oyuncu"
        self.baslat.emit(self._zorluk, isim)


# ═══════════════════════════════════════════════════════════════════════════════
#  OyunEkrani
# ═══════════════════════════════════════════════════════════════════════════════

class OyunEkrani(QWidget):
    def __init__(self, oy, geri_cb, parent=None):
        super().__init__(parent)
        self.oy = oy
        self.geri_cb = geri_cb
        self._secili_kart   = None
        self._secili_widget = None
        self._oz_modu       = "Sistem Rastgele Secsin"
        self._kart_widgets  = []
        self._tur_ozellik   = None
        self._kur()

    def set_oz_modu(self, m): self._oz_modu = m

    def _kur(self):
        lay = QVBoxLayout(self); lay.setSpacing(6); lay.setContentsMargins(8,8,8,8)
        self.skor = SkorBand(self.oy)
        lay.addWidget(self.skor)

        spl = QSplitter(Qt.Horizontal)
        spl.setStyleSheet(f"QSplitter::handle{{background:{BORDER};width:2px;}}")
        spl.addWidget(self._sol()); spl.addWidget(self._orta()); spl.addWidget(self._sag())
        spl.setSizes([330,380,330])
        lay.addWidget(spl, 1)
        lay.addWidget(self._alt_bar())

    def _sol(self):
        f = QFrame(); f.setObjectName("panel")
        lay = QVBoxLayout(f); lay.setContentsMargins(6,6,6,6); lay.setSpacing(4)
        lay.addWidget(L("👤  KARTLARINIZ", 11, True, GREEN, Qt.AlignCenter))
        sc = QScrollArea(); sc.setWidgetResizable(True)
        sc.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._k_cont = QWidget()
        self._k_lay  = QVBoxLayout(self._k_cont)
        self._k_lay.setSpacing(6); self._k_lay.setAlignment(Qt.AlignTop)
        sc.setWidget(self._k_cont)
        lay.addWidget(sc)
        return f

    def _orta(self):
        f = QFrame(); f.setObjectName("panel")
        lay = QVBoxLayout(f); lay.setContentsMargins(12,12,12,12); lay.setSpacing(8)

        self.tur_lbl = L("Tur 1 — Futbol", 13, True, BLUE, Qt.AlignCenter)
        lay.addWidget(self.tur_lbl)
        lay.addWidget(sep())

        self.kars_text = QTextEdit()
        self.kars_text.setReadOnly(True)
        self.kars_text.setFixedHeight(200)
        self.kars_text.setPlaceholderText("Bir kart secin...")
        lay.addWidget(self.kars_text)

        self.oz_group = QGroupBox("Ozellik")
        oz_lay = QVBoxLayout(self.oz_group)
        self.oz_combo = QComboBox()
        oz_lay.addWidget(self.oz_combo)
        lay.addWidget(self.oz_group)

        self.oyna_btn = QPushButton("⚔  TURU OYNA")
        self.oyna_btn.setObjectName("success")
        self.oyna_btn.setFixedHeight(44)
        self.oyna_btn.setFont(QFont("Segoe UI",12,QFont.Bold))
        self.oyna_btn.setEnabled(False)
        self.oyna_btn.clicked.connect(self._turu_oyna)
        lay.addWidget(self.oyna_btn)
        lay.addWidget(sep())

        self.sonuc_text = QTextEdit()
        self.sonuc_text.setReadOnly(True)
        self.sonuc_text.setFixedHeight(210)
        self.sonuc_text.setPlaceholderText("Tur sonuclari burada...")
        lay.addWidget(self.sonuc_text)

        self.mini_lbl = L("", 9, color=GRAY, align=Qt.AlignCenter)
        lay.addWidget(self.mini_lbl)
        lay.addStretch()
        return f

    def _sag(self):
        f = QFrame(); f.setObjectName("panel")
        lay = QVBoxLayout(f); lay.setContentsMargins(6,6,6,6); lay.setSpacing(4)
        tr = QHBoxLayout()
        tr.addWidget(L("🤖  BILGISAYAR", 11, True, RED))
        self.goster_btn = QPushButton("👁 Goster")
        self.goster_btn.setObjectName("geri"); self.goster_btn.setFixedWidth(80)
        self.goster_btn.setCheckable(True)
        self.goster_btn.clicked.connect(self._bilg_toggle)
        tr.addWidget(self.goster_btn)
        lay.addLayout(tr)

        sc = QScrollArea(); sc.setWidgetResizable(True)
        sc.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._b_cont = QWidget()
        self._b_lay  = QVBoxLayout(self._b_cont)
        self._b_lay.setSpacing(6); self._b_lay.setAlignment(Qt.AlignTop)
        lbl = L("🔒  Kartlar gizli\n'Goster' tusuna basin",
                10, color=DIM, align=Qt.AlignCenter)
        lbl.setWordWrap(True); self._b_lay.addWidget(lbl)
        sc.setWidget(self._b_cont)
        lay.addWidget(sc)
        return f

    def _alt_bar(self):
        f = QFrame()
        lay = QHBoxLayout(f); lay.setContentsMargins(0,4,0,0)
        g = QPushButton("🏠 Ana Menu"); g.setObjectName("geri"); g.setFixedWidth(120)
        g.clicked.connect(self.geri_cb)
        lay.addWidget(g); lay.addStretch()
        self.ai_lbl = L("", 9, color=DIM); lay.addWidget(self.ai_lbl)
        return f

    # ── Guncelleme ────────────────────────────────────────────────────────────

    def tam_guncelle(self):
        self.skor.guncelle()
        self._k_yenile()
        self._tur_baslik()
        self._oz_combo_guncelle()
        self.mini_lbl.setText(
            f"G:{self.oy.kullanici.toplam_galibiyet}  "
            f"M:{self.oy.kullanici.toplam_maglubiyet}  "
            f"B:{self.oy.kullanici.toplam_beraberlik}")
        self.ai_lbl.setText(f"AI: {self.oy.bilgisayar.zorluk}")
        self._secili_kart   = None
        self._secili_widget = None
        self.oyna_btn.setEnabled(False)
        self.kars_text.clear()
        self.kars_text.setPlaceholderText("Bir kart secin...")
        self._tur_ozellik = None
        if self.goster_btn.isChecked(): self._bilg_goster()

    def _temizle(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w: w.setParent(None)

    def _k_yenile(self):
        self._temizle(self._k_lay)
        self._kart_widgets = []
        brans = self.oy.mevcut_brans

        uygun = [k for k in self.oy.kullanici.kart_listesi
                 if k.brans()==brans and not k.kart_kullanildi_mi and k.enerji>0]
        diger = [k for k in self.oy.kullanici.kart_listesi
                 if k.brans()!=brans and not k.kart_kullanildi_mi and k.enerji>0]
        bitti = [k for k in self.oy.kullanici.kart_listesi
                 if k.kart_kullanildi_mi or k.enerji==0]

        if uygun:
            self._k_lay.addWidget(L(f"✅ {brans} Kartlari", 9, True, brans_renk(brans)))
            for k in uygun:
                w = KartWidget(k, secim_modu=True)
                w.secildi.connect(self._kart_secildi)
                self._k_lay.addWidget(w); self._kart_widgets.append(w)
        if diger:
            self._k_lay.addWidget(L("📦 Diger Brans", 9, True, GRAY))
            for k in diger:
                w = KartWidget(k, secim_modu=False)
                w.setStyleSheet(f"QFrame#card{{background:{BG};border:1px solid {DIM};border-radius:12px;}}")
                self._k_lay.addWidget(w)
        if bitti:
            self._k_lay.addWidget(L("✖ Biten Kartlar", 8, color=DIM))
            for k in bitti:
                w = KartWidget(k, secim_modu=False)
                w.setStyleSheet(f"QFrame#card{{background:{BG};border:1px dashed {DIM};border-radius:12px;}}")
                self._k_lay.addWidget(w)

    def _bilg_toggle(self):
        if self.goster_btn.isChecked():
            self.goster_btn.setText("🙈 Gizle"); self._bilg_goster()
        else:
            self.goster_btn.setText("👁 Goster"); self._bilg_gizle()

    def _bilg_gizle(self):
        self._temizle(self._b_lay)
        lbl = L("🔒  Kartlar gizli\n'Goster' tusuna basin", 10, color=DIM, align=Qt.AlignCenter)
        lbl.setWordWrap(True); self._b_lay.addWidget(lbl)

    def _bilg_goster(self):
        self._temizle(self._b_lay)
        for k in self.oy.bilgisayar.kart_listesi:
            w = KartWidget(k, secim_modu=False)
            if k.kart_kullanildi_mi or k.enerji==0:
                w.setStyleSheet(f"QFrame#card{{background:{BG};border:1px dashed {DIM};border-radius:12px;}}")
            self._b_lay.addWidget(w)

    def _tur_baslik(self):
        b = self.oy.mevcut_brans
        self.tur_lbl.setText(f"Tur {self.oy.tur_no+1}/{self.oy.toplam_tur}  —  {brans_emoji(b)} {b}")
        self.tur_lbl.setStyleSheet(
            f"color:{brans_renk(b)};background:transparent;font-weight:bold;font-size:13pt;")

    def _oz_combo_guncelle(self):
        from game.oyun_yonetici import BRANS_OZELLIKLER
        ozlk = BRANS_OZELLIKLER.get(self.oy.mevcut_brans, [])
        self.oz_combo.blockSignals(True)
        self.oz_combo.clear()
        self.oz_combo.addItems(ozlk)
        self.oz_combo.setEnabled(self._oz_modu != "Sistem Rastgele Secsin")
        self.oz_combo.blockSignals(False)

    # ── Kart & Tur ───────────────────────────────────────────────────────────

    def _kart_secildi(self, sporcu):
        if self._secili_widget: self._secili_widget.set_secili(False)
        for w in self._kart_widgets:
            if w.sporcu is sporcu:
                w.set_secili(True); self._secili_widget = w; break
        self._secili_kart = sporcu
        if self._oz_modu == "Sistem Rastgele Secsin":
            self._tur_ozellik = self.oy.ozellik_belirle()
        else:
            self._tur_ozellik = self.oy.ozellik_belirle(self.oz_combo.currentText())
        self.oy.bilgisayar_kart_sec()
        self._onizleme(sporcu, self._tur_ozellik)
        self.oyna_btn.setEnabled(True)

    def _onizleme(self, k, oz):
        b = self.oy.bilgisayar_son_secim
        if not b: return
        kb = self.oy._puan_breakdown(k, oz, b)
        bb = self.oy._puan_breakdown(b, oz, k)
        kp, bp = kb["toplam"], bb["toplam"]
        kr = GREEN if kp>=bp else RED
        br2= GREEN if bp>=kp else RED

        html = f"""<p style='color:{brans_renk(self.oy.mevcut_brans)};
            font-weight:bold;text-align:center;'>
            {brans_emoji(self.oy.mevcut_brans)} {oz}</p>
        <table width='100%' cellpadding='3'>
        <tr>
            <th style='color:{GREEN};text-align:left;'>👤 {k.ad}</th>
            <th style='color:{RED};text-align:right;'>🤖 {b.ad}</th>
        </tr>"""
        for satir, kv, bv in [
            ("Temel",     kb['temel'],        bb['temel']),
            ("Moral",     kb['moral'],        bb['moral']),
            ("O.Yetenek", kb['ozel_yetenek'], bb['ozel_yetenek']),
            ("Enerji C.", kb['enerji_cezasi'],bb['enerji_cezasi']),
            ("Seviye",    kb['seviye'],        bb['seviye']),
        ]:
            rv = RED if "C." in satir and (kv<0 or bv<0) else GRAY
            html += f"""<tr>
            <td style='color:{BLUE};text-align:left;'>{kv:+.0f}</td>
            <td style='color:{rv};text-align:center;font-size:10px;'>{satir}</td>
            <td style='color:{BLUE};text-align:right;'>{bv:+.0f}</td>
            </tr>"""
        html += f"""<tr>
            <td style='color:{kr};font-size:15px;font-weight:bold;text-align:left;'>{kp:.1f}</td>
            <td style='color:{GOLD};text-align:center;font-weight:bold;'>TOPLAM</td>
            <td style='color:{br2};font-size:15px;font-weight:bold;text-align:right;'>{bp:.1f}</td>
        </tr></table>"""
        self.kars_text.setHtml(
            f"<html><body style='background:{CARD};color:white;font-size:11px;'>{html}</body></html>")

    def _turu_oyna(self):
        if not self._secili_kart or not self._tur_ozellik: return

        hukmen = self.oy.hukmen_kontrol()
        if hukmen["durum"] == "atla":
            QMessageBox.information(self, "Tur Atlandi", hukmen["mesaj"])
            self.tam_guncelle(); return
        elif hukmen["durum"] in ("hukmen_kullanici","hukmen_bilgisayar"):
            self.oy.hukmen_tur_isle(hukmen["durum"])
            msg = hukmen.get("mesaj","")
            self.sonuc_text.setHtml(
                f"<html><body style='background:{CARD};'>"
                f"<p style='color:{GOLD};font-size:13px;font-weight:bold;'>{msg}</p>"
                f"</body></html>")
            self.tam_guncelle(); return

        sonuc = self.oy.turu_oyna(self._secili_kart, self._tur_ozellik)
        self._sonuc_goster(sonuc)
        self.tam_guncelle()

        # Oyun bitti → ANINDA istatistik sayfasina git
        if sonuc.get("oyun_bitti"):
            QTimer.singleShot(400, lambda: self.window().oyun_bitti_goster())

    def _sonuc_goster(self, s):
        k = s["kazanan"]
        kr = {"kullanici":GREEN,"bilgisayar":RED,"beraberlik":GOLD}.get(k,"#FFF")
        sm = {"kullanici":"🎉 KAZANDIN!","bilgisayar":"💀 KAYBETTIN!","beraberlik":"🤝 BERABERLIK!"}.get(k,"")
        html = f"""<p style='color:{kr};font-size:15px;font-weight:bold;text-align:center;'>{sm}</p>
        <p style='color:{GRAY};font-size:10px;'>
            <b style='color:white;'>{s['kullanici_kart']}</b>
            <span style='color:{DIM}'> vs </span>
            <b style='color:white;'>{s['bilgisayar_kart']}</b><br>
            Ozellik: <b style='color:{BLUE};'>{s['ozellik']}</b><br>
            Puan: <span style='color:{GREEN};'>{s['kullanici_puan']:.1f}</span>
            — <span style='color:{RED};'>{s['bilgisayar_puan']:.1f}</span>
        </p>"""
        for m in s["puan_sonuc"]["mesajlar"]:
            html += f"<p style='color:{GOLD};font-size:10px;'>• {m}</p>"
        for ad in s.get("seviye_atlayan",[]):
            html += f"<p style='color:{GOLD};font-size:11px;'>⬆ {ad} SEVIYE ATLADI!</p>"
        self.sonuc_text.setHtml(
            f"<html><body style='background:{CARD};'>{html}</body></html>")


# ═══════════════════════════════════════════════════════════════════════════════
#  IstatistikEkrani  — tamamen yeniden yazildi, renkler net gorunuyor
# ═══════════════════════════════════════════════════════════════════════════════

class IstatistikEkrani(QWidget):
    def __init__(self, oy, geri_cb, parent=None):
        super().__init__(parent)
        self.oy = oy
        self._kur(geri_cb)

    def _kur(self, geri_cb):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20,16,20,16)
        lay.setSpacing(10)

        # Baslik
        baslik_frame = QFrame(); baslik_frame.setObjectName("card")
        bf = QHBoxLayout(baslik_frame); bf.setContentsMargins(16,10,16,10)
        bf.addWidget(L("📊  MAC ISTATISTIKLERI", 20, True, GOLD, Qt.AlignCenter))
        lay.addWidget(baslik_frame)

        # Skor ozeti kutusu
        lay.addWidget(self._skor_kutu())

        # Brans istatistikleri
        lay.addWidget(self._brans_kutu())

        # Tur tablosu (kaydirmali)
        tablo_frame = QFrame(); tablo_frame.setObjectName("card")
        tf = QVBoxLayout(tablo_frame); tf.setContentsMargins(10,10,10,10); tf.setSpacing(6)
        tf.addWidget(L("Tur Tur Detaylar", 12, True, BLUE))
        tf.addWidget(self._tur_tablosu())
        lay.addWidget(tablo_frame, 1)

        # Alt butonlar
        br = QHBoxLayout()
        rb = QPushButton("📋 Rapor Goster"); rb.setObjectName("geri")
        rb.setFixedHeight(36); rb.clicked.connect(self._rapor)
        gb = QPushButton("🏠 Ana Menu"); gb.setObjectName("geri")
        gb.setFixedHeight(36); gb.clicked.connect(geri_cb)
        br.addWidget(rb); br.addStretch(); br.addWidget(gb)
        lay.addLayout(br)

    def _skor_kutu(self) -> QFrame:
        k = self.oy.kullanici; b = self.oy.bilgisayar
        sonuc = self.oy.kazanani_belirle()
        kaz   = sonuc["kazanan"]
        kr    = {"kullanici":GREEN,"bilgisayar":RED,"beraberlik":GOLD}.get(kaz,"#FFF")
        km    = {
            "kullanici":   f"🏆 {k.oyuncu_adi.upper()} KAZANDI!",
            "bilgisayar":  "🤖 BILGISAYAR KAZANDI!",
            "beraberlik":  "🤝 BERABERLIK!",
        }.get(kaz,"")

        f = QFrame(); f.setObjectName("card")
        lay = QVBoxLayout(f); lay.setContentsMargins(16,12,16,12); lay.setSpacing(8)

        # Kazanan yazisi
        kaz_lbl = QLabel(km)
        kaz_lbl.setAlignment(Qt.AlignCenter)
        kaz_lbl.setStyleSheet(
            f"color:{kr}; font-size:20px; font-weight:900; background:transparent;")
        lay.addWidget(kaz_lbl)

        sebep_lbl = QLabel(f"({sonuc['sebep']})")
        sebep_lbl.setAlignment(Qt.AlignCenter)
        sebep_lbl.setStyleSheet(f"color:{GRAY}; font-size:11px; background:transparent;")
        lay.addWidget(sebep_lbl)
        lay.addWidget(sep())

        # Skor satirlari
        skor_satir = QHBoxLayout(); skor_satir.setSpacing(30)

        def skor_blok(ad, skor, galip, mag, ber, renk):
            bf = QFrame(); bf.setObjectName("card")
            bl = QVBoxLayout(bf); bl.setContentsMargins(16,10,16,10)
            bl.setAlignment(Qt.AlignCenter); bl.setSpacing(4)
            bl.addWidget(L(ad, 11, True, renk, Qt.AlignCenter))
            p = QLabel(str(skor))
            p.setAlignment(Qt.AlignCenter)
            p.setStyleSheet(f"color:{renk}; font-size:32px; font-weight:900; background:transparent;")
            bl.addWidget(p)
            bl.addWidget(L(f"Galibiyet: {galip}  Maglup: {mag}  Beraberlik: {ber}",
                          9, color=GRAY, align=Qt.AlignCenter))
            return bf

        skor_satir.addWidget(
            skor_blok(f"👤 {k.oyuncu_adi.upper()}", k.skor,
                      k.toplam_galibiyet, k.toplam_maglubiyet, k.toplam_beraberlik, GREEN))
        vs_lbl = QLabel("VS")
        vs_lbl.setAlignment(Qt.AlignCenter)
        vs_lbl.setStyleSheet(f"color:{GOLD}; font-size:18px; font-weight:900; background:transparent;")
        skor_satir.addWidget(vs_lbl)
        skor_satir.addWidget(
            skor_blok("🤖 BILGISAYAR", b.skor,
                      b.toplam_galibiyet, b.toplam_maglubiyet, b.toplam_beraberlik, RED))
        lay.addLayout(skor_satir)
        return f

    def _brans_kutu(self) -> QFrame:
        f = QFrame(); f.setObjectName("card")
        lay = QVBoxLayout(f); lay.setContentsMargins(14,10,14,10); lay.setSpacing(8)
        lay.addWidget(L("Brans Bazli Istatistikler", 12, True, BLUE))
        lay.addWidget(sep())

        brans_ist = self.oy.istatistik.brans_istatistikleri()

        # Baslik satiri
        baslik_satir = QHBoxLayout(); baslik_satir.setSpacing(0)
        for metin, genislik, renk in [
            ("BRANS",          160, BLUE),
            ("OYUNCU GAL.",    100, GREEN),
            ("BILG. GAL.",     100, RED),
            ("BERABERLIK",     100, GOLD),
        ]:
            bl = QLabel(metin)
            bl.setFixedWidth(genislik)
            bl.setAlignment(Qt.AlignCenter)
            bl.setStyleSheet(
                f"color:{renk}; font-size:10px; font-weight:bold; "
                f"background:{CARD2}; padding:6px; border-radius:4px;")
            baslik_satir.addWidget(bl)
        baslik_satir.addStretch()
        lay.addLayout(baslik_satir)

        # Veri satirlari
        for brans, rn in [("Futbol",BLUE),("Basketbol",ORANGE),("Voleybol",GREEN)]:
            st = brans_ist.get(brans, {"kullanici":0,"bilgisayar":0,"beraberlik":0})
            satir = QHBoxLayout(); satir.setSpacing(0)

            brans_lbl = QLabel(f"{brans_emoji(brans)}  {brans}")
            brans_lbl.setFixedWidth(160)
            brans_lbl.setStyleSheet(
                f"color:{rn}; font-size:12px; font-weight:bold; "
                f"background:{CARD}; padding:8px; border-radius:4px; border-left:3px solid {rn};")
            satir.addWidget(brans_lbl)

            for val, renk in [
                (st['kullanici'],   GREEN),
                (st['bilgisayar'],  RED),
                (st['beraberlik'],  GOLD),
            ]:
                vl = QLabel(str(val))
                vl.setFixedWidth(100)
                vl.setAlignment(Qt.AlignCenter)
                vl.setStyleSheet(
                    f"color:{renk}; font-size:18px; font-weight:900; "
                    f"background:{CARD}; padding:6px; border-radius:4px;")
                satir.addWidget(vl)
            satir.addStretch()
            lay.addLayout(satir)

        return f

    def _tur_tablosu(self) -> QTableWidget:
        kayitlar = self.oy.istatistik.tur_kayitlari
        tbl = QTableWidget(len(kayitlar), 8)
        tbl.setHorizontalHeaderLabels([
            "Tur","Brans","Oyuncu Karti","Bilgisayar Karti",
            "Ozellik","Oyuncu Puani","Bilg. Puani","Sonuc"
        ])
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.setAlternatingRowColors(True)
        tbl.verticalHeader().setVisible(False)
        tbl.setSelectionBehavior(QTableWidget.SelectRows)

        # Sonuc renkler
        SONUC_STIL = {
            "kullanici":   (GREEN, "#0A200F"),
            "bilgisayar":  (RED,   "#200A0F"),
            "beraberlik":  (GOLD,  "#201A00"),
        }
        SONUC_METIN = {
            "kullanici":  "✅ OYUNCU",
            "bilgisayar": "❌ BILG.",
            "beraberlik": "🤝 BERABERE",
        }

        for i, r in enumerate(kayitlar):
            tur_item = QTableWidgetItem(str(r.tur_no))
            tur_item.setTextAlignment(Qt.AlignCenter)
            tbl.setItem(i, 0, tur_item)

            brans_item = QTableWidgetItem(r.brans)
            brans_item.setForeground(QColor(brans_renk(r.brans)))
            brans_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            brans_item.setTextAlignment(Qt.AlignCenter)
            tbl.setItem(i, 1, brans_item)

            tbl.setItem(i, 2, QTableWidgetItem(r.kullanici_kart))
            tbl.setItem(i, 3, QTableWidgetItem(r.bilgisayar_kart))
            tbl.setItem(i, 4, QTableWidgetItem(r.ozellik))

            # Oyuncu puani
            kp_item = QTableWidgetItem(f"{r.kullanici_puan:.1f}")
            kp_item.setForeground(QColor(GREEN))
            kp_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            kp_item.setTextAlignment(Qt.AlignCenter)
            tbl.setItem(i, 5, kp_item)

            # Bilgisayar puani
            bp_item = QTableWidgetItem(f"{r.bilgisayar_puan:.1f}")
            bp_item.setForeground(QColor(RED))
            bp_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            bp_item.setTextAlignment(Qt.AlignCenter)
            tbl.setItem(i, 6, bp_item)

            # Sonuc — renkli arkaplan + renkli yazi
            renk_yazi, renk_bg = SONUC_STIL.get(r.sonuc, ("#FFF", CARD))
            sonuc_metin = SONUC_METIN.get(r.sonuc, r.sonuc)
            si = QTableWidgetItem(sonuc_metin)
            si.setForeground(QColor(renk_yazi))
            si.setBackground(QColor(renk_bg))
            si.setFont(QFont("Segoe UI", 10, QFont.Bold))
            si.setTextAlignment(Qt.AlignCenter)
            tbl.setItem(i, 7, si)

            # Kazanan satiri tamamen renklendir (hafif)
            if r.sonuc != "beraberlik":
                for col in range(8):
                    item = tbl.item(i, col)
                    if item and col != 7:
                        item.setBackground(QColor(renk_bg))

        return tbl

    def _rapor(self):
        d = QDialog(self); d.setWindowTitle("Mac Raporu"); d.setMinimumSize(500,400)
        d.setStyleSheet(SS)
        dl = QVBoxLayout(d)
        t = QTextEdit(); t.setReadOnly(True)
        t.setPlainText(self.oy.istatistik.rapor_olustur(
            self.oy.kullanici.skor, self.oy.bilgisayar.skor))
        dl.addWidget(t)
        b = QPushButton("Kapat"); b.clicked.connect(d.accept); dl.addWidget(b)
        d.exec_()


# ═══════════════════════════════════════════════════════════════════════════════
#  AnaPencere
# ═══════════════════════════════════════════════════════════════════════════════

class AnaPencere(QMainWindow):
    def __init__(self, oy):
        super().__init__()
        self.oy = oy
        self.setWindowTitle("🏆  Akilli Sporcu Kart Ligi Simulasyonu")
        self.setMinimumSize(1150, 780)
        self.resize(1400, 880)
        self.setStyleSheet(SS)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._anasayfa = AnaSayfa()
        self._anasayfa.baslat.connect(self._oyunu_baslat)
        self._stack.addWidget(self._anasayfa)

        self._oyun_ekrani  = None
        self._istat_ekrani = None

    def _oyunu_baslat(self, zorluk, oyuncu_adi):
        r = self.oy.oyunu_baslat(zorluk, oyuncu_adi)
        if r and r.get("hatalar"):
            QMessageBox.warning(self, "Veri Hatasi",
                "Bazi satirlar yuklenemedi:\n" + "\n".join(r["hatalar"]))

        if self._oyun_ekrani:
            self._stack.removeWidget(self._oyun_ekrani)
            self._oyun_ekrani.setParent(None)

        self._oyun_ekrani = OyunEkrani(self.oy, self._ana_menu)
        self._oyun_ekrani.set_oz_modu(self._anasayfa.ozellik_modu())
        self._stack.addWidget(self._oyun_ekrani)
        self._stack.setCurrentWidget(self._oyun_ekrani)
        self._oyun_ekrani.tam_guncelle()

    def _ana_menu(self):
        self._stack.setCurrentWidget(self._anasayfa)

    def oyun_bitti_goster(self):
        """Oyun biter bitmez aninda istatistik sayfasina gec"""
        if self._istat_ekrani:
            self._stack.removeWidget(self._istat_ekrani)
            self._istat_ekrani.setParent(None)
        self._istat_ekrani = IstatistikEkrani(self.oy, self._ana_menu)
        self._stack.addWidget(self._istat_ekrani)
        self._stack.setCurrentWidget(self._istat_ekrani)
