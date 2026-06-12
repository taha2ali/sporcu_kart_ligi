"""
utils/veri_okuyucu.py - CSV dosyasından sporcu nesneleri oluşturur
"""

import csv
import os
from models.sporcu import Futbolcu, Basketbolcu, Voleybolcu


class VeriOkuyucu:
    def __init__(self, dosya_yolu: str):
        self._dosya_yolu = dosya_yolu
        self._hatalar = []

    @property
    def hatalar(self):
        return self._hatalar

    def oku(self) -> list:
        sporcular = []
        self._hatalar = []

        if not os.path.exists(self._dosya_yolu):
            raise FileNotFoundError(f"Dosya bulunamadı: {self._dosya_yolu}")

        try:
            with open(self._dosya_yolu, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for i, satir in enumerate(reader, 1):
                    try:
                        sporcu = self._satir_isle(satir)
                        if sporcu:
                            sporcular.append(sporcu)
                    except Exception as e:
                        self._hatalar.append(f"Satır {i}: {e}")
        except Exception as e:
            raise RuntimeError(f"Dosya okunurken hata: {e}")

        return sporcular

    def _satir_isle(self, satir: dict):
        tur = satir["tür"].strip()
        sporcu_id = satir["id"].strip()
        ad = satir["ad"].strip()
        takim = satir["takım"].strip()
        oz1 = int(satir["özellik1"])
        oz2 = int(satir["özellik2"])
        oz3 = int(satir["özellik3"])
        dayaniklilik = int(satir["dayanıklılık"])
        enerji = int(satir["enerji"])
        max_enerji = int(satir["maxEnerji"])
        seviye = int(satir["seviye"])
        deneyim = int(satir["deneyimPuanı"])
        ozel_yetenek = satir["özelYetenek"].strip()

        if tur == "Futbolcu":
            return Futbolcu(sporcu_id, ad, takim, oz1, oz2, oz3,
                            dayaniklilik, enerji, max_enerji, seviye, deneyim, ozel_yetenek)
        elif tur == "Basketbolcu":
            return Basketbolcu(sporcu_id, ad, takim, oz1, oz2, oz3,
                               dayaniklilik, enerji, max_enerji, seviye, deneyim, ozel_yetenek)
        elif tur == "Voleybolcu":
            return Voleybolcu(sporcu_id, ad, takim, oz1, oz2, oz3,
                              dayaniklilik, enerji, max_enerji, seviye, deneyim, ozel_yetenek)
        else:
            raise ValueError(f"Bilinmeyen sporcu türü: {tur}")
