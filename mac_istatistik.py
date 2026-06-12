"""
utils/mac_istatistik.py - Maç istatistiklerini tutar ve rapor oluşturur
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TurKaydi:
    tur_no: int
    brans: str
    kullanici_kart: str
    bilgisayar_kart: str
    ozellik: str
    kullanici_puan: float
    bilgisayar_puan: float
    sonuc: str  # "kullanici", "bilgisayar", "beraberlik"
    ozel_yetenek_etkili: bool
    hukmen: bool
    kazanilan_puan: int


class MacIstatistik:
    def __init__(self):
        self._tur_kayitlari: list[TurKaydi] = []
        self._baslangic_zamani = datetime.now()

    def tur_ekle(self, kayit: TurKaydi):
        self._tur_kayitlari.append(kayit)

    @property
    def tur_kayitlari(self):
        return self._tur_kayitlari

    def kullanici_galibiyet_sayisi(self):
        return sum(1 for t in self._tur_kayitlari if t.sonuc == "kullanici")

    def bilgisayar_galibiyet_sayisi(self):
        return sum(1 for t in self._tur_kayitlari if t.sonuc == "bilgisayar")

    def beraberlik_sayisi(self):
        return sum(1 for t in self._tur_kayitlari if t.sonuc == "beraberlik")

    def brans_istatistikleri(self) -> dict:
        branslar = {"Futbol": {"kullanici": 0, "bilgisayar": 0, "beraberlik": 0},
                    "Basketbol": {"kullanici": 0, "bilgisayar": 0, "beraberlik": 0},
                    "Voleybol": {"kullanici": 0, "bilgisayar": 0, "beraberlik": 0}}
        for t in self._tur_kayitlari:
            if t.brans in branslar:
                branslar[t.brans][t.sonuc if t.sonuc != "beraberlik" else "beraberlik"] += 1
        return branslar

    def rapor_olustur(self, kullanici_skor: int, bilgisayar_skor: int) -> str:
        sure = datetime.now() - self._baslangic_zamani
        satirlar = [
            "=" * 50,
            "         MAÇ SONU RAPORU",
            "=" * 50,
            f"Tarih: {self._baslangic_zamani.strftime('%d.%m.%Y %H:%M')}",
            f"Süre: {int(sure.total_seconds() // 60)} dk {int(sure.total_seconds() % 60)} sn",
            "",
            f"{'OYUNCU':<20} {'BİLGİSAYAR':>20}",
            f"{kullanici_skor:<20} {bilgisayar_skor:>20}",
            "",
            f"Tur Sayısı: {len(self._tur_kayitlari)}",
            f"Kullanıcı Galibiyeti: {self.kullanici_galibiyet_sayisi()}",
            f"Bilgisayar Galibiyeti: {self.bilgisayar_galibiyet_sayisi()}",
            f"Beraberlik: {self.beraberlik_sayisi()}",
            "",
            "BRANŞ İSTATİSTİKLERİ:",
        ]
        for brans, st in self.brans_istatistikleri().items():
            satirlar.append(f"  {brans}: K:{st['kullanici']} B:{st['bilgisayar']} "
                            f"Ber:{st['beraberlik']}")
        satirlar.append("=" * 50)
        return "\n".join(satirlar)
