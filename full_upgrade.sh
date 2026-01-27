#!/bin/bash
export PATH=/usr/bin:/bin:/usr/local/bin:$PATH

# Ensure we are in the right directory
cd /home/ysr/Desktop/kbdbacklight

echo "--- Eski Kalıntıları Temizleme İşlemi Başlıyor ---"

# 1. Eski uygulama süreçlerini sonlandır
pkill -f main.py
pkill -f kbd_backlight_app.py

# 2. Menüde karışıklık yaratan yerel (local) dosyaları sil
echo "Eski lokal masaüstü dosyaları siliniyor..."
rm -f ~/.local/share/applications/kbd-backlight.desktop
rm -f ~/.local/share/applications/kbdbacklight-manager.desktop
rm -f ~/Desktop/kbd-backlight.desktop

# 3. Eski deb paketini (eğer varsa) kaldır
echo "Eski paket kaldırılıyor..."
sudo apt remove -y kbdbacklight-manager

# 4. Paketi yeniden inşa et
echo "Yeni paket (v2.6.0) inşa ediliyor..."
bash package_build.sh

# 5. Yeni paketi kur
echo "Yeni paket sisteme kuruluyor..."
sudo apt install -y ./build/kbdbacklight-manager_2.6.0.deb

# 6. Menü ve terminal yollarını tazele
echo "Sistem yolları güncelleniyor..."
sudo ldconfig
update-desktop-database ~/.local/share/applications || true
sudo update-desktop-database /usr/share/applications || true

echo "--- İŞLEM TAMAMLANDI! ---"
echo "Artık uygulamayı menüden ('Klavye Işığı Paneli') veya "
echo "terminalden direkt 'kbdbacklight' yazarak başlatabilirsin."
