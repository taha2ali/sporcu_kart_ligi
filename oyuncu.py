# -*- coding: utf-8 -*-
"""models/oyuncu.py - Soyut Oyuncu, Kullanici, Bilgisayar siniflari"""

from abc import ABC, abstractmethod
import random
from models.sporcu import Sporcu


class KartSecmeStratejisi(ABC):
    @abstractmethod
    def kart_sec(self, kartlar: list, oyun_durumu: dict) -> Sporcu:
        pass


class KolayStrateji(KartSecmeStratejisi):
    """Uygun branstan rastgele kart secer"""
    def kart_sec(self, kartlar, oyun_durumu):
        uygun = [k for k in kartlar if not k.kart_kullanildi_mi and k.enerji > 0]
        brans = oyun_durumu.get("brans")
        if brans:
            bb = [k for k in uygun if k.brans() == brans]
            if bb: return random.choice(bb)
        return random.choice(uygun) if uygun else None


class OrtaStrateji(KartSecmeStratejisi):
    """Uygun branstaki en yuksek ortalama performansli karti secer"""
    def kart_sec(self, kartlar, oyun_durumu):
        uygun = [k for k in kartlar if not k.kart_kullanildi_mi and k.enerji > 0]
        brans = oyun_durumu.get("brans")
        if brans:
            bb = [k for k in uygun if k.brans() == brans]
            if bb: uygun = bb
        if not uygun: return None
        tur = oyun_durumu.get("tur_sayisi", 0)
        toplam = oyun_durumu.get("toplam_tur", 12)
        def ort(k):
            ozlk = list(k.ozellikler().keys())
            return sum(k.performans_hesapla(o, tur, toplam) for o in ozlk) / len(ozlk)
        return max(uygun, key=ort)


class ZorStrateji(KartSecmeStratejisi):
    """En iyi kartiyla oynar: performans + enerji + ozel yetenek agirlikli"""
    def kart_sec(self, kartlar, oyun_durumu):
        uygun = [k for k in kartlar if not k.kart_kullanildi_mi and k.enerji > 0]
        brans = oyun_durumu.get("brans")
        if brans:
            bb = [k for k in uygun if k.brans() == brans]
            if bb: uygun = bb
        if not uygun: return None
        tur = oyun_durumu.get("tur_sayisi", 0)
        toplam = oyun_durumu.get("toplam_tur", 12)
        def skor(k):
            ozlk = list(k.ozellikler().keys())
            max_perf = max(k.performans_hesapla(o, tur, toplam) for o in ozlk)
            enerji_b = k.enerji / 10
            seviye_b = (k.seviye - 1) * 8
            return max_perf + enerji_b + seviye_b
        return max(uygun, key=skor)


class Oyuncu(ABC):
    def __init__(self, oyuncu_id, oyuncu_adi):
        self._oyuncu_id   = oyuncu_id
        self._oyuncu_adi  = oyuncu_adi
        self._skor        = 0
        self._moral       = 75
        self._kart_listesi: list[Sporcu] = []
        self._galibiyet_serisi   = 0
        self._kaybetme_serisi    = 0
        self._toplam_galibiyet   = 0
        self._toplam_maglubiyet  = 0
        self._toplam_beraberlik  = 0
        self._ozel_yetenek_galibiyeti = 0
        self._hukmen_galibiyet   = 0

    @property
    def oyuncu_id(self):  return self._oyuncu_id
    @property
    def oyuncu_adi(self): return self._oyuncu_adi
    @oyuncu_adi.setter
    def oyuncu_adi(self, v): self._oyuncu_adi = v
    @property
    def skor(self):       return self._skor
    @property
    def moral(self):      return self._moral
    @property
    def kart_listesi(self): return self._kart_listesi
    @property
    def galibiyet_serisi(self): return self._galibiyet_serisi
    @property
    def toplam_galibiyet(self): return self._toplam_galibiyet
    @property
    def toplam_maglubiyet(self): return self._toplam_maglubiyet
    @property
    def toplam_beraberlik(self): return self._toplam_beraberlik
    @property
    def ozel_yetenek_galibiyeti(self): return self._ozel_yetenek_galibiyeti
    @property
    def hukmen_galibiyet(self): return self._hukmen_galibiyet

    def kart_ekle(self, kart):
        self._kart_listesi.append(kart)

    def uygun_kartlar(self, brans):
        return [k for k in self._kart_listesi
                if k.brans() == brans and not k.kart_kullanildi_mi and k.enerji > 0]

    def kalan_kartlar(self):
        return [k for k in self._kart_listesi
                if not k.kart_kullanildi_mi and k.enerji > 0]

    def skor_ekle(self, puan):
        self._skor += puan

    def sonuc_guncelle(self, sonuc, ozel_yetenek_etkili=False, hukmen=False):
        if sonuc == "galibiyet":
            self._toplam_galibiyet += 1
            self._galibiyet_serisi += 1
            self._kaybetme_serisi  = 0
            if ozel_yetenek_etkili: self._ozel_yetenek_galibiyeti += 1
            if hukmen:              self._hukmen_galibiyet += 1
        elif sonuc == "maglubiyet":
            self._toplam_maglubiyet += 1
            self._kaybetme_serisi  += 1
            self._galibiyet_serisi  = 0
        else:
            self._toplam_beraberlik += 1
            self._galibiyet_serisi  = 0
            self._kaybetme_serisi   = 0

    def moral_guncelle(self):
        if self._galibiyet_serisi >= 3:
            self._moral = min(100, self._moral + 15)
        elif self._galibiyet_serisi >= 2:
            self._moral = min(100, self._moral + 10)
        elif self._kaybetme_serisi >= 2:
            self._moral = max(0, self._moral - 10)

    def kalan_enerji_toplami(self):
        return sum(k.enerji for k in self._kart_listesi)

    def en_yuksek_seviyeli_kart_sayisi(self):
        return sum(1 for k in self._kart_listesi if k.seviye == 3)

    @abstractmethod
    def kart_sec(self, brans, oyun_durumu): pass


class Kullanici(Oyuncu):
    def __init__(self, ad="Oyuncu"):
        super().__init__("U001", ad)

    def kart_sec(self, brans, oyun_durumu):
        pass


class Bilgisayar(Oyuncu):
    def __init__(self, zorluk="Kolay"):
        super().__init__("C001", "Bilgisayar")
        self._zorluk = zorluk
        self._strateji_guncelle(zorluk)

    def _strateji_guncelle(self, z):
        if z == "Orta":
            self._strateji = OrtaStrateji()
        elif z == "Zor":
            self._strateji = ZorStrateji()
        else:
            self._strateji = KolayStrateji()

    @property
    def zorluk(self): return self._zorluk

    def zorluk_degistir(self, zorluk):
        self._zorluk = zorluk
        self._strateji_guncelle(zorluk)

    def kart_sec(self, brans, oyun_durumu):
        oyun_durumu["brans"] = brans
        return self._strateji.kart_sec(self._kart_listesi, oyun_durumu)
