"""
game/oyun_yonetici.py - Oyun akışını yöneten merkezi sınıf
"""

import random
from models.sporcu import Sporcu
from models.oyuncu import Kullanici, Bilgisayar
from utils.mac_istatistik import MacIstatistik, TurKaydi
from utils.veri_okuyucu import VeriOkuyucu


BRANS_SIRASI = ["Futbol", "Basketbol", "Voleybol"]
BRANS_OZELLIKLER = {
    "Futbol": ["Penaltı", "Serbest Vuruş", "Kaleci Karşı Karşıya"],
    "Basketbol": ["İkilik", "Üçlük", "Serbest Atış"],
    "Voleybol": ["Servis", "Blok", "Smaç"],
}


class OyunYonetici:
    def __init__(self, veri_dosyasi: str):
        self._veri_dosyasi = veri_dosyasi
        self._kullanici = Kullanici()
        self._bilgisayar = Bilgisayar()
        self._istatistik = MacIstatistik()
        self._tur_no = 0
        self._toplam_tur = 12
        self._oyun_bitti = False
        self._tum_sporcular: list[Sporcu] = []
        self._mevcut_brans = ""
        self._mevcut_ozellik = ""
        self._son_tur_sonucu = {}
        self._seviye_atlayan_kartlar = []
        self._kullanici_son_secim: Sporcu = None
        self._bilgisayar_son_secim: Sporcu = None

    # ── Property'ler ──────────────────────
    @property
    def kullanici(self): return self._kullanici
    @property
    def bilgisayar(self): return self._bilgisayar
    @property
    def tur_no(self): return self._tur_no
    @property
    def toplam_tur(self): return self._toplam_tur
    @property
    def oyun_bitti(self): return self._oyun_bitti
    @property
    def istatistik(self): return self._istatistik
    @property
    def mevcut_brans(self): return self._mevcut_brans
    @property
    def mevcut_ozellik(self): return self._mevcut_ozellik
    @property
    def son_tur_sonucu(self): return self._son_tur_sonucu
    @property
    def seviye_atlayan_kartlar(self): return self._seviye_atlayan_kartlar
    @property
    def kullanici_son_secim(self): return self._kullanici_son_secim
    @property
    def bilgisayar_son_secim(self): return self._bilgisayar_son_secim

    # ── Oyun Başlatma ─────────────────────

    def oyunu_baslat(self, zorluk: str = "Kolay", oyuncu_adi: str = "Oyuncu") -> dict:
        """Oyunu sıfırlar ve başlatır"""
        okuyucu = VeriOkuyucu(self._veri_dosyasi)
        self._tum_sporcular = okuyucu.oku()

        if okuyucu.hatalar:
            return {"hata": okuyucu.hatalar}

        self._kullanici = Kullanici(oyuncu_adi)
        self._bilgisayar = Bilgisayar(zorluk)
        self._istatistik = MacIstatistik()
        self._tur_no = 0
        self._oyun_bitti = False
        self._son_tur_sonucu = {}
        self._seviye_atlayan_kartlar = []

        self._kartlari_dagit()
        self._mevcut_brans = BRANS_SIRASI[0]
        return {"basarili": True, "hatalar": okuyucu.hatalar}

    def _kartlari_dagit(self):
        """24 kartı ikiye böl; her oyuncuya her branştan 4 kart"""
        futbol = [s for s in self._tum_sporcular if s.brans() == "Futbol"]
        basketbol = [s for s in self._tum_sporcular if s.brans() == "Basketbol"]
        voleybol = [s for s in self._tum_sporcular if s.brans() == "Voleybol"]

        for grup in [futbol, basketbol, voleybol]:
            random.shuffle(grup)

        # Her branştan 4'er kart kullanıcıya, 4'er kart bilgisayara
        for kart in futbol[:4] + basketbol[:4] + voleybol[:4]:
            self._kullanici.kart_ekle(kart)
        for kart in futbol[4:] + basketbol[4:] + voleybol[4:]:
            self._bilgisayar.kart_ekle(kart)

    # ── Tur Yönetimi ──────────────────────

    def tur_bransini_belirle(self) -> str:
        brans = BRANS_SIRASI[self._tur_no % 3]
        self._mevcut_brans = brans
        return brans

    def ozellik_belirle(self, kullanici_secimi: str = None) -> str:
        """Sistem rastgele veya kullanıcı seçimi"""
        if kullanici_secimi and kullanici_secimi in BRANS_OZELLIKLER.get(self._mevcut_brans, []):
            self._mevcut_ozellik = kullanici_secimi
        else:
            self._mevcut_ozellik = random.choice(BRANS_OZELLIKLER[self._mevcut_brans])
        return self._mevcut_ozellik

    def hukmen_kontrol(self) -> dict:
        """
        Her iki tarafta da uygun kart yoksa → atla
        Sadece birinde yoksa → diğeri hükmen kazanır
        """
        k_uygun = self._kullanici.uygun_kartlar(self._mevcut_brans)
        b_uygun = self._bilgisayar.uygun_kartlar(self._mevcut_brans)

        if not k_uygun and not b_uygun:
            return {"durum": "atla", "mesaj": f"{self._mevcut_brans} turunda her iki tarafta da kart yok. Tur atlandı."}
        if not k_uygun:
            return {"durum": "hukmen_bilgisayar", "mesaj": f"Kullanıcının {self._mevcut_brans} kartı kalmadı. Bilgisayar hükmen kazandı."}
        if not b_uygun:
            return {"durum": "hukmen_kullanici", "mesaj": f"Bilgisayarın {self._mevcut_brans} kartı kalmadı. Kullanıcı hükmen kazandı."}
        return {"durum": "normal"}

    def hukmen_tur_isle(self, durum: str) -> dict:
        """Hükmen galibiyet işle"""
        if durum == "hukmen_kullanici":
            puan = 8
            self._kullanici.skor_ekle(puan)
            self._kullanici.sonuc_guncelle("galibiyet", hukmen=True)
            self._bilgisayar.sonuc_guncelle("maglubiyet")
            self._kullanici.moral_guncelle()
            self._bilgisayar.moral_guncelle()
            self._istatistik.tur_ekle(TurKaydi(
                self._tur_no + 1, self._mevcut_brans,
                "—", "—", "—", 0, 0,
                "kullanici", False, True, puan
            ))
            return {"kazanan": "kullanici", "puan": puan, "mesaj": "Kullanıcı hükmen kazandı! +8 puan"}
        else:
            puan = 8
            self._bilgisayar.skor_ekle(puan)
            self._bilgisayar.sonuc_guncelle("galibiyet", hukmen=True)
            self._kullanici.sonuc_guncelle("maglubiyet")
            self._kullanici.moral_guncelle()
            self._bilgisayar.moral_guncelle()
            self._istatistik.tur_ekle(TurKaydi(
                self._tur_no + 1, self._mevcut_brans,
                "—", "—", "—", 0, 0,
                "bilgisayar", False, True, puan
            ))
            return {"kazanan": "bilgisayar", "puan": puan, "mesaj": "Bilgisayar hükmen kazandı! +8 puan"}

    def bilgisayar_kart_sec(self) -> Sporcu:
        oyun_durumu = {
            "brans": self._mevcut_brans,
            "tur_sayisi": self._tur_no,
            "toplam_tur": self._toplam_tur,
        }
        kart = self._bilgisayar.kart_sec(self._mevcut_brans, oyun_durumu)
        self._bilgisayar_son_secim = kart
        return kart

    def turu_oyna(self, kullanici_kart: Sporcu, ozellik: str = None) -> dict:
        """Turu hesapla ve sonuçları döndür"""
        if ozellik is None:
            ozellik = self._mevcut_ozellik

        bilgisayar_kart = self._bilgisayar_son_secim
        self._kullanici_son_secim = kullanici_kart

        # Performans hesapla
        k_puan = kullanici_kart.performans_hesapla(ozellik, self._tur_no, self._toplam_tur, bilgisayar_kart)
        b_puan = bilgisayar_kart.performans_hesapla(ozellik, self._tur_no, self._toplam_tur, kullanici_kart)

        # Detaylı puan breakdown
        k_breakdown = self._puan_breakdown(kullanici_kart, ozellik, bilgisayar_kart)
        b_breakdown = self._puan_breakdown(bilgisayar_kart, ozellik, kullanici_kart)

        # Kazananı belirle
        kazanan, ozel_yetenek_etkili = self._kazanan_belirle(
            kullanici_kart, bilgisayar_kart, ozellik, k_puan, b_puan
        )

        # Puanlama
        puan_sonuc = self._puan_hesapla(kazanan, ozel_yetenek_etkili, kullanici_kart, bilgisayar_kart)

        # Kart durumları güncelle
        self._kartlari_guncelle(kullanici_kart, bilgisayar_kart, kazanan, ozel_yetenek_etkili)

        # Oyuncu durumları güncelle
        self._oyuncular_guncelle(kazanan, ozel_yetenek_etkili, puan_sonuc)

        # Seviye kontrolü
        self._seviye_atlayan_kartlar = []
        for kart in [kullanici_kart, bilgisayar_kart]:
            if kart.seviye_atla_kontrol():
                self._seviye_atlayan_kartlar.append(kart.ad)

        # İstatistik kaydet
        self._istatistik.tur_ekle(TurKaydi(
            self._tur_no + 1, self._mevcut_brans,
            kullanici_kart.ad, bilgisayar_kart.ad, ozellik,
            k_puan, b_puan, kazanan, ozel_yetenek_etkili, False,
            puan_sonuc.get("kullanici_puan", 0)
        ))

        self._tur_no += 1

        # Oyun bitti mi?
        if self._tur_no >= self._toplam_tur or (
            not self._kullanici.kalan_kartlar() and not self._bilgisayar.kalan_kartlar()
        ):
            self._oyun_bitti = True

        self._son_tur_sonucu = {
            "tur_no": self._tur_no,
            "brans": self._mevcut_brans,
            "ozellik": ozellik,
            "kullanici_kart": kullanici_kart.ad,
            "bilgisayar_kart": bilgisayar_kart.ad,
            "kullanici_puan": k_puan,
            "bilgisayar_puan": b_puan,
            "kullanici_breakdown": k_breakdown,
            "bilgisayar_breakdown": b_breakdown,
            "kazanan": kazanan,
            "ozel_yetenek_etkili": ozel_yetenek_etkili,
            "puan_sonuc": puan_sonuc,
            "seviye_atlayan": self._seviye_atlayan_kartlar,
            "oyun_bitti": self._oyun_bitti,
        }

        # Sonraki branşı ayarla
        if not self._oyun_bitti:
            self._mevcut_brans = BRANS_SIRASI[self._tur_no % 3]

        return self._son_tur_sonucu

    def _puan_breakdown(self, kart: Sporcu, ozellik: str, rakip: Sporcu) -> dict:
        temel = kart.ozellikler().get(ozellik, 0)
        moral_b = kart.moral_bonusu()
        oz_b = kart.ozel_yetenek_bonusu(rakip, self._tur_no, self._toplam_tur)
        if rakip.ozel_yetenek_adi == "Defender":
            oz_b = oz_b // 2
        enerji_c = kart.enerji_cezasi(temel)
        seviye_b = kart.seviye_bonusu()
        return {
            "temel": temel,
            "moral": moral_b,
            "ozel_yetenek": oz_b,
            "enerji_cezasi": -enerji_c,
            "seviye": seviye_b,
            "toplam": temel + moral_b + oz_b - enerji_c + seviye_b,
        }

    def _kazanan_belirle(self, k_kart, b_kart, ozellik, k_puan, b_puan):
        """7 aşamalı kazanan belirleme mekanizması"""
        ozel_yetenek_etkili = (
            k_kart.ozel_yetenek_adi != "None" or b_kart.ozel_yetenek_adi != "None"
        )

        if k_puan > b_puan:
            return "kullanici", ozel_yetenek_etkili
        elif b_puan > k_puan:
            return "bilgisayar", ozel_yetenek_etkili

        # Eşitlik: branş içi yedek özellik
        tum_ozellikler = BRANS_OZELLIKLER[self._mevcut_brans]
        for yedek in tum_ozellikler:
            if yedek == ozellik:
                continue
            ky = k_kart.performans_hesapla(yedek, self._tur_no, self._toplam_tur, b_kart)
            by = b_kart.performans_hesapla(yedek, self._tur_no, self._toplam_tur, k_kart)
            if ky > by:
                return "kullanici", ozel_yetenek_etkili
            elif by > ky:
                return "bilgisayar", ozel_yetenek_etkili

        # Dayanıklılık
        if k_kart.dayaniklilik > b_kart.dayaniklilik:
            return "kullanici", False
        elif b_kart.dayaniklilik > k_kart.dayaniklilik:
            return "bilgisayar", False

        # Enerji
        if k_kart.enerji > b_kart.enerji:
            return "kullanici", False
        elif b_kart.enerji > k_kart.enerji:
            return "bilgisayar", False

        # Seviye
        if k_kart.seviye > b_kart.seviye:
            return "kullanici", False
        elif b_kart.seviye > k_kart.seviye:
            return "bilgisayar", False

        return "beraberlik", False

    def _puan_hesapla(self, kazanan, ozel_yetenek_etkili, k_kart, b_kart) -> dict:
        sonuc = {"kullanici_puan": 0, "bilgisayar_puan": 0, "mesajlar": []}

        if kazanan == "beraberlik":
            sonuc["mesajlar"].append("Beraberlik! Puan yok.")
            return sonuc

        if kazanan == "kullanici":
            temel = 15 if ozel_yetenek_etkili else 10
            toplam = temel
            sonuc["mesajlar"].append(f"Kullanıcı kazandı! +{temel} puan")

            # Ek bonuslar
            if k_kart.enerji < 30:
                toplam += 5
                sonuc["mesajlar"].append("+5 (Düşük enerjiyle galibiyet)")
            if self._kullanici.galibiyet_serisi >= 5:
                toplam += 20
                sonuc["mesajlar"].append("+20 (5 galip serisi!)")
            elif self._kullanici.galibiyet_serisi >= 3:
                toplam += 10
                sonuc["mesajlar"].append("+10 (3 galip serisi!)")
            if k_kart.ozel_yetenek_adi == "ClutchPlayer" and ozel_yetenek_etkili:
                toplam += 5
                sonuc["mesajlar"].append("+5 (Clutch Player!)")

            sonuc["kullanici_puan"] = toplam
        else:  # bilgisayar
            temel = 15 if ozel_yetenek_etkili else 10
            toplam = temel
            sonuc["mesajlar"].append(f"Bilgisayar kazandı! +{temel} puan")

            if b_kart.enerji < 30:
                toplam += 5
            if self._bilgisayar.galibiyet_serisi >= 5:
                toplam += 20
            elif self._bilgisayar.galibiyet_serisi >= 3:
                toplam += 10

            sonuc["bilgisayar_puan"] = toplam

        return sonuc

    def _kartlari_guncelle(self, k_kart, b_kart, kazanan, ozel_yetenek_etkili):
        k_sonuc = "galibiyet" if kazanan == "kullanici" else ("maglubiyet" if kazanan == "bilgisayar" else "beraberlik")
        b_sonuc = "galibiyet" if kazanan == "bilgisayar" else ("maglubiyet" if kazanan == "kullanici" else "beraberlik")

        k_kart.enerji_guncelle(k_sonuc, ozel_yetenek_etkili and k_kart.ozel_yetenek_adi != "None")
        b_kart.enerji_guncelle(b_sonuc, ozel_yetenek_etkili and b_kart.ozel_yetenek_adi != "None")
        k_kart.deneyim_guncelle(k_sonuc)
        b_kart.deneyim_guncelle(b_sonuc)
        k_kart.kart_kullan()
        b_kart.kart_kullan()

    def _oyuncular_guncelle(self, kazanan, ozel_yetenek_etkili, puan_sonuc):
        k_sonuc = "galibiyet" if kazanan == "kullanici" else ("maglubiyet" if kazanan == "bilgisayar" else "beraberlik")
        b_sonuc = "galibiyet" if kazanan == "bilgisayar" else ("maglubiyet" if kazanan == "kullanici" else "beraberlik")

        self._kullanici.sonuc_guncelle(k_sonuc, ozel_yetenek_etkili)
        self._bilgisayar.sonuc_guncelle(b_sonuc, ozel_yetenek_etkili)
        self._kullanici.skor_ekle(puan_sonuc["kullanici_puan"])
        self._bilgisayar.skor_ekle(puan_sonuc["bilgisayar_puan"])
        self._kullanici.moral_guncelle()
        self._bilgisayar.moral_guncelle()

    # ── Oyun Sonu ────────────────────────

    def kazanani_belirle(self) -> dict:
        k = self._kullanici
        b = self._bilgisayar

        if k.skor > b.skor:
            return {"kazanan": "kullanici", "sebep": "Yüksek puan"}
        elif b.skor > k.skor:
            return {"kazanan": "bilgisayar", "sebep": "Yüksek puan"}

        # Eşitlik kriterleri
        if k.toplam_galibiyet != b.toplam_galibiyet:
            kaz = "kullanici" if k.toplam_galibiyet > b.toplam_galibiyet else "bilgisayar"
            return {"kazanan": kaz, "sebep": "Daha fazla galibiyet"}

        if k.kalan_enerji_toplami() != b.kalan_enerji_toplami():
            kaz = "kullanici" if k.kalan_enerji_toplami() > b.kalan_enerji_toplami() else "bilgisayar"
            return {"kazanan": kaz, "sebep": "Kalan enerji"}

        if k.en_yuksek_seviyeli_kart_sayisi() != b.en_yuksek_seviyeli_kart_sayisi():
            kaz = "kullanici" if k.en_yuksek_seviyeli_kart_sayisi() > b.en_yuksek_seviyeli_kart_sayisi() else "bilgisayar"
            return {"kazanan": kaz, "sebep": "Daha fazla Level 3 kart"}

        if k.ozel_yetenek_galibiyeti != b.ozel_yetenek_galibiyeti:
            kaz = "kullanici" if k.ozel_yetenek_galibiyeti > b.ozel_yetenek_galibiyeti else "bilgisayar"
            return {"kazanan": kaz, "sebep": "Özel yetenek galibiyeti"}

        if k.toplam_beraberlik != b.toplam_beraberlik:
            kaz = "kullanici" if k.toplam_beraberlik < b.toplam_beraberlik else "bilgisayar"
            return {"kazanan": kaz, "sebep": "Daha az beraberlik"}

        return {"kazanan": "beraberlik", "sebep": "Tüm kriterler eşit"}
