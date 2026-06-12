"""
main.py - Akıllı Sporcu Kart Ligi Simülasyonu - Giriş Noktası
"""

import sys
import os

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from ui.ana_pencere import AnaPencere
from game.oyun_yonetici import OyunYonetici


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Akıllı Sporcu Kart Ligi")

    # Genel font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Veri dosyası yolu
    veri_dosyasi = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "data", "sporcular.csv")

    oyun = OyunYonetici(veri_dosyasi)
    pencere = AnaPencere(oyun)
    pencere.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
