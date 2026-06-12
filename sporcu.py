"""
models/sporcu.py - Abstract Sporcu sınıfı ve alt sınıflar
Kapsülleme, Kalıtım, Polimorfizm, Soyutlama
"""

from abc import ABC, abstractmethod


class OzelYetenek(ABC):
    """Özel yetenek interface'i"""
    @abstractmethod
    def uygula(self, kart, rakip_kart, tur_sayisi, toplam_tur):
        pass

    @abstractmethod
    def aciklama(self):
        pass


class Legend(OzelYetenek):
    def __init__(self):
        self.kullanildi = False

    def uygula(self, kart, rakip_kart, tur_sayisi, toplam_tur):
        if not self.kullanildi:
            self.kullanildi = True
            return 20  # Bir maçta bir kez seçilen özelliği iki kat etkiler (bonus)
        return 0

    def aciklama(self):
        return "Legend: Maçta bir kez +20 bonus (tek kullanım)"


class Captain(OzelYetenek):
    def uygula(self, kart, rakip_kart, tur_sayisi, toplam_tur):
        return 5  # Pasif: Aynı branştan takım kartlarına moral etkisi; burada +5 bonus

    def aciklama(self):
        return "Captain: Her turda +5 moral bonusu"


class ClutchPlayer(OzelYetenek):
    def uygula(self, kart, rakip_kart, tur_sayisi, toplam_tur):
        if toplam_tur > 0 and tur_sayisi >= toplam_tur - 3:
            return 10  # Son 3 turda +10 bonus
        return 0

    def aciklama(self):
        return "Clutch Player: Son 3 turda +10 bonus"


class Defender(OzelYetenek):
    def uygula(self, kart, rakip_kart, tur_sayisi, toplam_tur):
        return 0  # Rakibin özel yetenek bonusunu yarıya düşürür (rakip üzerinde etki)

    def aciklama(self):
        return "Defender: Rakibin özel yetenek bonusunu yarıya düşürür"


class Veteran(OzelYetenek):
    def uygula(self, kart, rakip_kart, tur_sayisi, toplam_tur):
        return 3  # Enerji kaybını azaltır; burada küçük bonus

    def aciklama(self):
        return "Veteran: Enerji kaybı %50 azalır"


class Finisher(OzelYetenek):
    def uygula(self, kart, rakip_kart, tur_sayisi, toplam_tur):
        if kart.enerji < 40:
            return 8  # Enerjisi düşükken +8 ek bonus
        return 0

    def aciklama(self):
        return "Finisher: Enerji < 40 iken +8 bonus"


class NoYetenek(OzelYetenek):
    def uygula(self, kart, rakip_kart, tur_sayisi, toplam_tur):
        return 0

    def aciklama(self):
        return "Özel yetenek yok"


def yetenek_olustur(yetenek_adi: str) -> OzelYetenek:
    yetenek_map = {
        "Legend": Legend,
        "Captain": Captain,
        "ClutchPlayer": ClutchPlayer,
        "Defender": Defender,
        "Veteran": Veteran,
        "Finisher": Finisher,
        "None": NoYetenek,
    }
    cls = yetenek_map.get(yetenek_adi, NoYetenek)
    return cls()


# ─────────────────────────────────────────
# Abstract Sporcu
# ─────────────────────────────────────────

class Sporcu(ABC):
    """Soyut sporcu sınıfı"""

    def __init__(self, sporcu_id, ad, takim, dayaniklilik, enerji, max_enerji,
                 seviye, deneyim_puani, ozel_yetenek_adi):
        self._sporcu_id = sporcu_id
        self._ad = ad
        self._takim = takim
        self._dayaniklilik = dayaniklilik
        self._enerji = enerji
        self._max_enerji = max_enerji
        self._seviye = seviye
        self._deneyim_puani = deneyim_puani
        self._ozel_yetenek = yetenek_olustur(ozel_yetenek_adi)
        self._ozel_yetenek_adi = ozel_yetenek_adi
        self._kart_kullanildi_mi = False
        self._kullanim_sayisi = 0
        self._galibiyet = 0
        self._maglubiyet = 0
        self._moral = 75  # 0-100 arası

    # ── Property'ler ──────────────────────
    @property
    def sporcu_id(self): return self._sporcu_id
    @property
    def ad(self): return self._ad
    @property
    def takim(self): return self._takim
    @property
    def dayaniklilik(self): return self._dayaniklilik
    @property
    def enerji(self): return self._enerji
    @property
    def max_enerji(self): return self._max_enerji
    @property
    def seviye(self): return self._seviye
    @property
    def deneyim_puani(self): return self._deneyim_puani
    @property
    def ozel_yetenek_adi(self): return self._ozel_yetenek_adi
    @property
    def kart_kullanildi_mi(self): return self._kart_kullanildi_mi
    @property
    def galibiyet(self): return self._galibiyet
    @property
    def maglubiyet(self): return self._maglubiyet
    @property
    def moral(self): return self._moral
    @property
    def kullanim_sayisi(self): return self._kullanim_sayisi

    @abstractmethod
    def brans(self) -> str:
        pass

    @abstractmethod
    def ozellikler(self) -> dict:
        pass

    @abstractmethod
    def performans_hesapla(self, ozellik_adi: str, tur_sayisi: int, toplam_tur: int,
                           rakip=None) -> float:
        pass

    def moral_bonusu(self) -> int:
        if self._moral >= 80:
            return 10
        elif self._moral >= 50:
            return 5
        else:
            return -5

    def enerji_cezasi(self, temel_puan: float) -> float:
        if self._enerji > 70:
            return 0
        elif 40 <= self._enerji <= 70:
            return temel_puan * 0.10
        elif 0 < self._enerji < 40:
            return temel_puan * 0.20
        else:
            return temel_puan  # enerji 0: kart oynanamaz

    def seviye_bonusu(self) -> int:
        return (self._seviye - 1) * 5

    def ozel_yetenek_bonusu(self, rakip=None, tur_sayisi=0, toplam_tur=0) -> int:
        return self._ozel_yetenek.uygula(self, rakip, tur_sayisi, toplam_tur)

    def ozel_yetenek_aciklama(self) -> str:
        return self._ozel_yetenek.aciklama()

    def enerji_guncelle(self, sonuc: str, ozel_yetenek_kullanildi: bool = False):
        if sonuc == "galibiyet":
            kayip = 5
        elif sonuc == "maglubiyet":
            kayip = 10
        else:  # beraberlik
            kayip = 3
        if ozel_yetenek_kullanildi:
            kayip += 5
        # Veteran yeteneği enerji kaybını %50 azaltır
        if self._ozel_yetenek_adi == "Veteran":
            kayip = kayip // 2
        self._enerji = max(0, self._enerji - kayip)

    def deneyim_guncelle(self, sonuc: str):
        if sonuc == "galibiyet":
            self._deneyim_puani += 2
            self._galibiyet += 1
        elif sonuc == "beraberlik":
            self._deneyim_puani += 1
        else:
            self._maglubiyet += 1

    def seviye_atla_kontrol(self) -> bool:
        """Seviye atladıysa True döner"""
        eski_seviye = self._seviye
        if self._seviye < 3:
            if self._galibiyet >= 4 or self._deneyim_puani >= 8:
                self._seviye = 3
            elif self._galibiyet >= 2 or self._deneyim_puani >= 4:
                self._seviye = max(self._seviye, 2)
        if self._seviye > eski_seviye:
            self._seviye_atla_etki()
            return True
        return False

    def _seviye_atla_etki(self):
        self._max_enerji = min(130, self._max_enerji + 10)
        self._dayaniklilik = min(100, self._dayaniklilik + 5)

    def kart_kullan(self):
        self._kart_kullanildi_mi = True
        self._kullanim_sayisi += 1

    def moral_guncelle(self, deger: int):
        self._moral = max(0, min(100, self._moral + deger))

    def sporcu_puani_goster(self) -> str:
        ozlk = self.ozellikler()
        satirlar = [f"🏅 {self._ad} | {self.brans()} | {self._takim}"]
        for k, v in ozlk.items():
            satirlar.append(f"  {k}: {v}")
        satirlar.append(f"  Enerji: {self._enerji}/{self._max_enerji}")
        satirlar.append(f"  Moral: {self._moral} | Seviye: {self._seviye}")
        return "\n".join(satirlar)

    def kart_bilgisi_yazdir(self) -> dict:
        return {
            "id": self._sporcu_id,
            "ad": self._ad,
            "takim": self._takim,
            "brans": self.brans(),
            "ozellikler": self.ozellikler(),
            "dayaniklilik": self._dayaniklilik,
            "enerji": self._enerji,
            "max_enerji": self._max_enerji,
            "seviye": self._seviye,
            "deneyim": self._deneyim_puani,
            "ozel_yetenek": self._ozel_yetenek_adi,
            "galibiyet": self._galibiyet,
            "maglubiyet": self._maglubiyet,
            "moral": self._moral,
        }


# ─────────────────────────────────────────
# Futbolcu
# ─────────────────────────────────────────

class Futbolcu(Sporcu):
    def __init__(self, sporcu_id, ad, takim, penalti, serbest_vurus,
                 kaleci_karsi_karsiya, dayaniklilik, enerji, max_enerji,
                 seviye, deneyim, ozel_yetenek):
        super().__init__(sporcu_id, ad, takim, dayaniklilik, enerji,
                         max_enerji, seviye, deneyim, ozel_yetenek)
        self._penalti = penalti
        self._serbest_vurus = serbest_vurus
        self._kaleci_karsi_karsiya = kaleci_karsi_karsiya

    def brans(self): return "Futbol"

    def ozellikler(self):
        return {
            "Penaltı": self._penalti,
            "Serbest Vuruş": self._serbest_vurus,
            "Kaleci Karşı Karşıya": self._kaleci_karsi_karsiya,
        }

    def _seviye_atla_etki(self):
        super()._seviye_atla_etki()
        self._penalti = min(99, self._penalti + 5)
        self._serbest_vurus = min(99, self._serbest_vurus + 5)
        self._kaleci_karsi_karsiya = min(99, self._kaleci_karsi_karsiya + 5)

    def performans_hesapla(self, ozellik_adi, tur_sayisi=0, toplam_tur=12, rakip=None):
        oz_map = {
            "Penaltı": self._penalti,
            "Serbest Vuruş": self._serbest_vurus,
            "Kaleci Karşı Karşıya": self._kaleci_karsi_karsiya,
        }
        temel = oz_map.get(ozellik_adi, self._penalti)
        ceza = self.enerji_cezasi(temel)
        oz_bonus = self.ozel_yetenek_bonusu(rakip, tur_sayisi, toplam_tur)
        # Defender rakibin özel yetenek bonusunu yarıya düşürür
        if rakip and rakip.ozel_yetenek_adi == "Defender":
            oz_bonus = oz_bonus // 2
        puan = temel + self.moral_bonusu() + oz_bonus - ceza + self.seviye_bonusu()
        return max(0, puan)


# ─────────────────────────────────────────
# Basketbolcu
# ─────────────────────────────────────────

class Basketbolcu(Sporcu):
    def __init__(self, sporcu_id, ad, takim, ikilik, ucluk, serbest_atis,
                 dayaniklilik, enerji, max_enerji, seviye, deneyim, ozel_yetenek):
        super().__init__(sporcu_id, ad, takim, dayaniklilik, enerji,
                         max_enerji, seviye, deneyim, ozel_yetenek)
        self._ikilik = ikilik
        self._ucluk = ucluk
        self._serbest_atis = serbest_atis

    def brans(self): return "Basketbol"

    def ozellikler(self):
        return {
            "İkilik": self._ikilik,
            "Üçlük": self._ucluk,
            "Serbest Atış": self._serbest_atis,
        }

    def _seviye_atla_etki(self):
        super()._seviye_atla_etki()
        self._ikilik = min(99, self._ikilik + 5)
        self._ucluk = min(99, self._ucluk + 5)
        self._serbest_atis = min(99, self._serbest_atis + 5)

    def performans_hesapla(self, ozellik_adi, tur_sayisi=0, toplam_tur=12, rakip=None):
        oz_map = {
            "İkilik": self._ikilik,
            "Üçlük": self._ucluk,
            "Serbest Atış": self._serbest_atis,
        }
        temel = oz_map.get(ozellik_adi, self._ikilik)
        ceza = self.enerji_cezasi(temel)
        oz_bonus = self.ozel_yetenek_bonusu(rakip, tur_sayisi, toplam_tur)
        if rakip and rakip.ozel_yetenek_adi == "Defender":
            oz_bonus = oz_bonus // 2
        puan = temel + self.moral_bonusu() + oz_bonus - ceza + self.seviye_bonusu()
        return max(0, puan)


# ─────────────────────────────────────────
# Voleybolcu
# ─────────────────────────────────────────

class Voleybolcu(Sporcu):
    def __init__(self, sporcu_id, ad, takim, servis, blok, smac,
                 dayaniklilik, enerji, max_enerji, seviye, deneyim, ozel_yetenek):
        super().__init__(sporcu_id, ad, takim, dayaniklilik, enerji,
                         max_enerji, seviye, deneyim, ozel_yetenek)
        self._servis = servis
        self._blok = blok
        self._smac = smac

    def brans(self): return "Voleybol"

    def ozellikler(self):
        return {
            "Servis": self._servis,
            "Blok": self._blok,
            "Smaç": self._smac,
        }

    def _seviye_atla_etki(self):
        super()._seviye_atla_etki()
        self._servis = min(99, self._servis + 5)
        self._blok = min(99, self._blok + 5)
        self._smac = min(99, self._smac + 5)

    def performans_hesapla(self, ozellik_adi, tur_sayisi=0, toplam_tur=12, rakip=None):
        oz_map = {
            "Servis": self._servis,
            "Blok": self._blok,
            "Smaç": self._smac,
        }
        temel = oz_map.get(ozellik_adi, self._servis)
        ceza = self.enerji_cezasi(temel)
        oz_bonus = self.ozel_yetenek_bonusu(rakip, tur_sayisi, toplam_tur)
        if rakip and rakip.ozel_yetenek_adi == "Defender":
            oz_bonus = oz_bonus // 2
        puan = temel + self.moral_bonusu() + oz_bonus - ceza + self.seviye_bonusu()
        return max(0, puan)
