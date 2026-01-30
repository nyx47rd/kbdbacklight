#!/usr/bin/env python3
import config

# Simple i18n logic
translations = {
    "en": {
        "app_title": "Keyboard Backlight Panel",
        "tab_control": "Control",
        "tab_effects": "Effects",
        "tab_about": "About",
        "brightness_level": "Brightness Level",
        "current_brightness": "Current Brightness",
        "autostart": "Start automatically at login",
        "temp_light": "Light up on touch (Systemwide)",
        "burn_duration_label": "Duration (Seconds)",
        "reset_app": "Reset Application",
        "eff_desc": "Click the boxes below to create a rhythm.\n\nEach box represents a 1-second step. Brightness cycles on click. Press 'Start' to loop.",
        "start_rhythm": "Start Rhythm ▶",
        "stop": "Stop ⏹",
        "sos_mode": "SOS Mode 🆘",
        "about_text": "Universal keyboard backlight management tool for Linux laptops.\n\nOptimized for Linux Mint and ASUS laptops.",
        "version": "Version",
        "developer": "Developer",
        "reset_q": "Do you want to completely reset the application and settings?",
        "reset_desc": "This will clear all settings and uninstall packages. Password may be required.",
        "welcome": "Next Gen Keyboard Panel",
        "welcome_desc": "The most stylish way to control your backlight. Setup in seconds!",
        "compat_systems": "<b>Compatible Systems:</b>\nAll ASUS Laptops, Some MSI & HP Models\n(Optimized for Linux Mint)",
        "lets_start": "Let's Start ➜",
        "os_check": "Scanning System Compatibility...",
        "mint_ready": "✔ Linux Mint Ready!",
        "os_warn": "⚠ Optimized for Linux Mint. Continue?",
        "continue": "Continue",
        "cancel": "Cancel",
        "configuring": "Configuring System...",
        "start_config": "Start Configuration",
        "auto_config": "Auto Configuration",
        "hardware_tool": "Hardware Control Tool",
        "keyboard_driver": "Keyboard Tracking Driver",
        "tray_support": "System Tray Support",
        "permissions": "Device Access Permissions",
        "all_ready": "Everything is Ready!",
        "final_desc": "Keyboard Backlight Panel successfully installed. Enjoy your light show.",
        "launch_app": "Launch Application ✨",
        "config_fail": "Configuration failed!",
        "language": "Language",
        "restart_msg": "Application will restart for language change."
    },
    "tr": {
        "app_title": "Klavye Işığı Paneli",
        "tab_control": "Kontrol",
        "tab_effects": "Efektler",
        "tab_about": "Hakkında",
        "brightness_level": "Parlaklık Seviyesi",
        "current_brightness": "Mevcut Parlaklık",
        "autostart": "Oturumda otomatik başlat",
        "temp_light": "Dokununca yansın (Sistem Geneli)",
        "burn_duration_label": "Yanma Süresi (Saniye)",
        "reset_app": "Uygulamayı Sıfırla",
        "eff_desc": "Klavye ışığı ritmini oluşturmak için aşağıdaki kutucuklara tıklayın.\n\nHer bir kutucuk 1 saniyelik bir adımı temsil eder. Tıkladıkça ışık seviyesi değişir.",
        "start_rhythm": "Ritmi Başlat ▶",
        "stop": "Durdur ⏹",
        "sos_mode": "SOS Modu 🆘",
        "about_text": "Linux laptoplar için geliştirilmiş evrensel klavye ışığı yönetim aracı.\n\nLinux Mint ve ASUS laptoplar için optimize edilmiştir.",
        "version": "Sürüm",
        "developer": "Geliştirici",
        "reset_q": "Uygulamayı ve ayarları tamamen sıfırlamak istiyor musunuz?",
        "reset_desc": "Bu işlem tüm ayarları ve paketleri temizler. Şifreniz istenebilir.",
        "welcome": "Yeni Nesil Klavye Paneli",
        "welcome_desc": "Klavye ışığınızı kontrol etmenin en şık yolu. Saniyeler içinde kurun!",
        "compat_systems": "<b>Uyumlu Sistemler:</b>\nTüm ASUS Laptoplar, Bazı MSI ve HP Modelleri\n(Linux Mint için Optimize Edildi)",
        "lets_start": "Hemen Başlayalım ➜",
        "os_check": "Sistem Uyumluluğu Taranıyor...",
        "mint_ready": "✔ Linux Mint Hazır!",
        "os_warn": "⚠ Linux Mint için optimize edilmiştir. Devam edilsin mi?",
        "continue": "Devam Et",
        "cancel": "İptal",
        "configuring": "Sistemi Yapılandırılıyor...",
        "start_config": "Yapılandırmayı Başlat",
        "auto_config": "Sistemi Otomatik Yapılandır",
        "hardware_tool": "Donanım Kontrol Aracı",
        "keyboard_driver": "Klavye Takip Sürücüsü",
        "tray_support": "Sistem Çekmeci Desteği",
        "permissions": "Cihaz Erişim Yetkileri",
        "all_ready": "Her Şey Hazır!",
        "final_desc": "Klavye Işığı Paneli kuruldu. Işık şovunun tadını çıkarın.",
        "launch_app": "Uygulamayı Başlat ✨",
        "config_fail": "Yapılandırma başarısız oldu!",
        "language": "Dil / Language",
        "restart_msg": "Dil değişikliği için uygulama yeniden başlatılacak."
    }
}

_lang_override = None

def set_lang_override(lang):
    global _lang_override
    _lang_override = lang

def get_string(key):
    if _lang_override:
        lang = _lang_override
    else:
        settings = config.load_settings()
        lang = settings.get("language", "tr")
    
    if lang not in translations:
        lang = "tr"
    return translations[lang].get(key, key)

_ = get_string
