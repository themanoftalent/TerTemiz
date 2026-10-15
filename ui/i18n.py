"""Live Turkish/English UI catalog; unknown external names remain unchanged."""
import re

_language = "tr"
# Original Turkish strings are stable keys; callbacks keep their original values.
EN = {
"Sistem Durumu": "System Status",
"🩺  Sağlık Kontrolü": "🩺  Health Check",
"🧹  Özel Temizleme": "🧹  Custom Clean",
"⚡  Performans İyileştirici": "⚡  Performance",
"🔄  Sürücü Güncelleyici": "🔄  Drivers",
"📦  Uygulama Güncelleyici": "📦  App Updates",
"📑  Kayıt Defteri": "📑  Registry",
"🛠️  Araçlar": "🛠️  Tools", "⚙️  Seçenekler": "⚙️  Settings",
"⚙️ Genel Ayarlar": "⚙️ General", "🧠 Akıllı Temizleme": "🧠 Smart Cleaning",
"ℹ️ Hakkında & Lisans": "ℹ️ About & License",
"Görünüm ve Arayüz Seçenekleri": "Appearance and Interface",
"Tema Tercihi:": "Theme:", "Uygulama Dili:": "Language:",
"Sistem Entegrasyonu": "System Integration",
"Otomatik Arka Plan Temizleme (Smart Cleaning)": "Automatic Background Cleaning",
"Çöp eşiği aşıldığında beni uyar:": "Notify me when junk exceeds:",
"Windows başladığında TerTemiz'i otomatik çalıştır": "Start TerTemiz when Windows starts",
"Geri Dönüşüm Kutusu sağ tık menüsüne 'TerTemiz ile Temizle' seçeneği ekle": "Add 'Clean with TerTemiz' to the Recycle Bin context menu",
"Temizleme işleminden sonra özet bildirim penceresi göster": "Show a summary after cleaning",
"Akıllı Temizlemeyi Etkinleştir": "Enable Smart Cleaning",
"Tarayıcılar kapandığında önbelleği otomatik temizle": "Clean the cache when browsers close",
"Sürüm 7.0.2 Pro (64-bit)": "Version 7.0.2 Pro (64-bit)",
"Modern Windows Sistem Temizleme ve Performans Paketi": "Windows System Cleaning and Performance Suite",
"👑 TerTemiz Professional Lisansı": "👑 TerTemiz Professional License",
"Durum: Süresiz Aktif (Ömür Boyu Pro)": "Status: Active (Lifetime Pro)",
"Lisans Sahibi: Sistem Yöneticisi (Pro User)": "License Owner: System Administrator (Pro User)",
"Bu uygulama TerTemiz modern arayüzünü ve Windows için optimize edilmiş\ngerçek sistem temizleme ve güncelleme motorunu sunar.": "TerTemiz provides a modern interface and a system cleaning\nand update engine optimized for Windows.",
"Bilgisayarınızın Sağlık Kontrolü Zamanı": "Time for a PC Health Check",
"Gereksiz sistem dosyalarını temizleyin, web izleyicilerini kaldırın,\narka plan süreçlerini optimize edin ve PC'nizin performansını zirveye taşıyın.": "Clean unnecessary files and web trackers,\nand optimize background processes to improve your PC's performance.",
"Taramayı Başlat": "Start Scan", "Bilgisayarınız İnceleniyor...": "Checking Your PC...",
"Sistem dosyaları ve önbellekler taranıyor...": "Scanning system files and caches...",
"İptal Et": "Cancel", "İptal": "Cancel", "PC'niz Biraz Halsiz Görünüyor!": "Your PC Could Use a Cleanup",
"✨ Daha İyi Hale Getir": "✨ Improve Performance",
"Bilgisayarınız Temizleniyor ve Hızlandırılıyor...": "Cleaning and Optimizing Your PC...",
"Gereksiz dosyalar kaldırılıyor...": "Removing unnecessary files...",
"Harika! Bilgisayarınız Artık Formda ve Tertemiz!": "Your PC Cleanup Is Complete!",
"🔄 Yeniden Tara": "🔄 Scan Again", "Yeniden Tara": "Scan Again",
"🧹 Özel Temizleme'ye Git": "🧹 Open Custom Clean",
"🔒 Gizlilik": "🔒 Privacy", "💾 Depolama Alanı": "💾 Storage",
"⚡ Hız & Performans": "⚡ Speed & Performance", "Bellek & Arka Plan": "Memory & Background Apps",
"🛡️ Güvenlik": "🛡️ Security", "Korumalı & Güncel": "Protected & Up to Date",
"Edge, Chrome ve tarayıcı oturum geçmişi, web izleme dosyaları.": "Edge, Chrome, browsing history and web tracking files.",
"RAM çalışma kümeleri optimize edilecek ve gereksiz bellek yükü kaldırılacak.": "Optimize RAM working sets and reduce memory usage.",
"Temel Windows sistem bileşenleri ve yüklü uygulamalar kontrol edildi.": "Windows components and installed applications were checked.",
"🔒 Gizlilik Koruması": "🔒 Privacy", "İzleyicileri ve çerezleri siler": "Remove trackers and cookies",
"💾 Alan Tasarrufu": "💾 Save Space", "Gigabaytlarca yer açar": "Free up disk space",
"⚡ Hız İyileştirme": "⚡ Performance", "Gereksiz uygulamaları durdurur": "Suspend unneeded apps",
"🛡️ Güvenlik Kontrolü": "🛡️ System Check", "Sistem durumunu inceler": "Check system status",
"Analiz Et": "Analyze", "Temizliğe Başla": "Start Cleaning", "Temizleme için hazır": "Ready to Clean",
"Özel temizlik yapmak için kuralları seçin ve 'Analiz Et' butonuna tıklayın.": "Select cleaning rules and click Analyze.",
"Analiz tamamlandı.": "Analysis complete.",
"Seçilen gereksiz dosyaları sisteminizden kalıcı olarak silmek için 'Temizliğe Başla' butonuna tıklayın.": "Click Start Cleaning to permanently remove the selected files.",
"Evet, Temizle": "Yes, Clean", "Temizleme tamamlandı!": "Cleaning Complete!",
"Seçilen gereksiz dosyalar başarıyla temizlendi.": "The selected files were cleaned successfully.",
"Seçilen kategorilerde temizlenecek dosya bulunamadı. Sisteminiz temiz!": "No files to clean in the selected categories.",
"Analiz sonuçları burada listelenecektir": "Analysis results will appear here",
"Sol taraftan temizlemek istediğiniz kategorileri seçin ve 'Analiz Et' butonuna tıklayın.": "Select categories on the left and click Analyze.",
"Windows ve uygulama önbellekleri tertemiz hale getirildi.": "Windows and application caches were cleaned.",
"🧠 Bellek (RAM) Kullanımı": "🧠 Memory (RAM) Usage", "⚡ Arka Plan Uygulamaları": "⚡ Background Apps",
"🚀 Hızlı Bellek Boşaltma": "🚀 Free Memory", "RAM'i Rahatlat": "Free RAM",
"🔍 Uygulama Ara...": "🔍 Search Apps...", "🔄 Yenile": "🔄 Refresh",
"Temizleniyor...": "Cleaning...", "✕ Sonlandır": "✕ End Task", "💤 Uyut": "💤 Suspend", "⚡ Uyandır": "⚡ Resume",
"Uygulama Adı (PID)": "Application (PID)", "RAM Kullanımı": "RAM Usage", "Sistem Etkisi": "System Impact", "Eylemler": "Actions",
"-- Uygulama": "-- Apps", "-- yüksek etki algılandı": "-- high-impact apps",
"📦 Uygulama Güncelleyici (Software)": "📦 App Updates", "⚙️ Donanım Sürücüleri (Drivers)": "⚙️ Drivers",
"Yüklü Uygulama Güncellemeleri Denetleniyor...": "Checking Application Updates...",
"Bilgisayarınızdaki programların güncel sürümleri Windows paket havuzundan taranıyor.": "Checking the Windows package repository for application updates.",
"🚀 Tümünü Güncelle": "🚀 Update All", "Tümünü Güncelle": "Update All",
"Yüklü Program Güncellemeleri Taranıyor...": "Scanning Installed Applications...",
"Yeni özellikler ve güvenlik yamaları için uygulamaları doğrudan buradan güncelleyebilirsiniz.": "Install new features and security patches from here.",
"Güncelleme Sürüyor...": "Updating...", "Donanım Aygıtları ve Sürücü Analizi": "Hardware and Driver Analysis",
"Ekran, ses, ağ ve sistem aygıt sürücülerinin donanım kimlikleri denetleniyor.": "Check display, audio, network and system device drivers.",
"🔄 Sürücüleri Tara": "🔄 Scan Drivers", "Tüm Programlarınız Güncel! 🎉": "No Available Updates Found 🎉",
"Sisteminizdeki yazılımlar en son sürümlerinde çalışıyor.": "WinGet found no available updates in the selected source.",
"Uygulama Adı / Kimlik": "Application / ID", "Kurulu Sürüm": "Installed", "Yeni Sürüm": "Available", "Eylem": "Action",
"✅ Güncellendi": "✅ Updated", "🚀 Güncelle": "🚀 Update", "Güncelle": "Update",
"Canlı Kurulum ve İndirme Günlüğü (Live Terminal Log):": "Installation and Download Log:",
"Aygıt Adı & Üretici": "Device & Manufacturer", "Kategori": "Category", "Sürüm / Tarih": "Version / Date", "Durum": "Status",
"Harika! Güncelleme Gerektiren Uygulama Yok": "No Available Updates Found",
"Tüm yüklü yazılımlar güncel ve güvenlik yamaları tam.": "Only applications recognized by WinGet are included.",
"✅ Güncelleme Başarıyla Tamamlandı!": "✅ Update Completed Successfully!", "Kapat": "Close",
"İşlem tamamlandı. Detayları yukarıdaki günlükten inceleyebilirsiniz.": "Update failed. Check the log for details.",
"Uygulamalar taranıyor...": "Scanning applications...",
"Windows Paket Yöneticisi (winget) ile güncellemeler denetleniyor...": "Checking updates with Windows Package Manager (WinGet)...",
"Güncelleme taraması başarısız": "Update Scan Failed", "WinGet Kurulumunu Aç": "Open WinGet Setup",
"🔍 Program Ara...": "🔍 Search Programs...", "Kaldır (Uninstall)": "Uninstall", "Girdiyi Sil": "Delete Entry",
"Diski Tara": "Scan Disk", "Taranıyor...": "Scanning...", "Çiftleri Ara": "Find Duplicates", "Klasörü Aç": "Open Folder",
"Arama yapmak istediğiniz klasörü seçin ve 'Çiftleri Ara' butonuna tıklayın.": "Select a folder and click Find Duplicates.",
"Program Adı": "Program", "Yayımcı": "Publisher", "Yükleme Tarihi": "Install Date", "Boyut": "Size",
"Windows Başlatıldığında Çalışan Programlar": "Windows Startup Programs", "Program / Girdi": "Program / Entry",
"Dosya Komutu": "Command", "Konum": "Location", "En Çok Alan Kaplayan Dosyalar": "Largest Files", "Sil": "Delete",
"💻 Donanım ve Sistem Özellikleri": "💻 Hardware and System Information",
"Klasörde aynı boyutta ve içerikte çift dosya bulunamadı.": "No duplicate files with identical content were found.",
"Kayıt Defteri Temizliği": "Registry Cleanup", "Sorunları Tara": "Scan for Issues", "Seçili Sorunları İncele": "Review Selected Issues",
"Kayıt Defteri Taraması için Hazır": "Ready for Registry Scan",
"Kayıt Defterinizdeki geçersiz, yetim ve artık kayıtları tespit etmek için 'Sorunları Tara'ya basın.": "Click Scan for Issues to find invalid and leftover registry entries.",
"Sorunları güvenle onarmak için 'Seçili Sorunları İncele' butonuna tıklayın.": "Click Review Selected Issues before repairing the registry.",
"Evet (Yedekle & Düzelt)": "Yes (Back Up & Repair)", "Hayır (Yedeklemeden)": "No (Without Backup)",
"Tüm Sorunlar Onarıldı! ✅": "All Issues Repaired! ✅", "Tebrikler! Hiçbir Kayıt Defteri Sorunu Bulunamadı. ✅": "No Registry Issues Found ✅",
"Kayıt defteriniz temiz ve optimize durumda.": "No registry issues were detected.", "Kayıt Defteri Sorunları Taranmadı": "Registry Has Not Been Scanned",
"Taramayı başlatmak için sol alt kısımdaki butona tıklayın.": "Click the button at the bottom left to start scanning.",
"Sorun Açıklaması": "Issue", "Veri / Dosya Yolu": "Data / File Path", "Kayıt Anahtarı": "Registry Key",
"Değişiklik yapmadan önce kayıt defterini yedeklemek istiyor musunuz?": "Back up the registry before making changes?",
"Güvenlik amacıyla, kaldırılacak girdilerin .reg formatında bir yedeği\nBelgeler klasörünüze kaydedilecektir.": "A .reg backup of the affected entries will be saved\nto your Documents folder.",
"Donanım Sürücüleri Taranıyor...": "Scanning Hardware Drivers...",
"Sisteminizdeki grafik, ses, ağ ve çevre birimi sürücüleri denetleniyor.": "Checking graphics, audio, network and peripheral drivers.",
"Sistem Donanım Sürücüleri Taranıyor...": "Scanning System Hardware Drivers...",
"Tümü": "All", "Grafik & Ekran": "Graphics & Display", "Ses & Medya": "Audio & Media",
"Ağ Bağdaştırıcısı": "Network", "Giriş & Bluetooth": "Input & Bluetooth", "Sistem Aygıtı": "System Device",
"Windows": "Windows", "Uygulamalar": "Applications", "Sistem": "System", "Gezgin": "Explorer",
"Yüksek": "High", "Orta": "Medium", "Düşük": "Low", "Güncel": "Up to Date",
"Güncelleme Mevcut": "Update Available", "Koyu (Dark)": "Dark", "Açık (Light)": "Light", "Sistem Teması": "System Theme",
"Kaldırıcı": "Uninstaller", "Başlangıç": "Startup", "Disk Analizörü": "Disk Analyzer",
"Çift Dosyalar": "Duplicate Files", "Sistem Bilgisi": "System Information",
}

EN.update({
"📦 Program Kaldırıcı": "📦 Uninstaller", "🚀 Başlangıç Yöneticisi": "🚀 Startup",
"📊 Disk Analizörü": "📊 Disk Analyzer", "📂 Çift Dosya Bulucu": "📂 Duplicates",
"💻 Sistem Bilgisi": "💻 System Info",
"Güncelleme durumunu Windows Update üzerinden denetleyin.": "Check driver updates through Windows Update.",
"Windows Update ile denetle": "Check Windows Update",
"Seçili uygulama güncellemeleri sırayla kurulacak. Devam edilsin mi?": "Install the available application updates one at a time?",
})

EN.update({'📊 Disk Alanı Analizi': '📊 Disk Analysis', '🔍 Çift Dosya Bulucu': '🔍 Duplicates', 'ℹ️ Sistem Özellikleri': 'ℹ️ System', '📦 Kaldırıcı': '📦 Uninstaller', '🚀 Başlangıç': '🚀 Startup', '📊 Disk Analizi': '📊 Disk Analysis', '🔍 Çift Dosya': '🔍 Duplicates', 'ℹ️ Sistem': 'ℹ️ System', 'İşletim Sistemi': 'Operating System', 'İşlemci (CPU)': 'Processor (CPU)', 'Grafik Kartı (GPU)': 'Graphics (GPU)', 'Geçici Dosyalar (Temp)': 'Temporary Files', 'Bellek Dökümleri (Minidump)': 'Memory Dumps (Minidump)', 'Font Önbelleği': 'Font Cache', 'Son Kullanılan Dosyalar': 'Recent Files', 'Küçük Resim (Thumbnail) Önbelleği': 'Thumbnail Cache', 'İnternet Önbelleği': 'Internet Cache', 'Çerezler ve Oturum Verileri': 'Cookies and Session Data', 'İnternet Geçmişi': 'Browsing History', 'Çerezler': 'Cookies', 'Discord Önbelleği': 'Discord Cache', 'Spotify Şarkı Önbelleği': 'Spotify Cache', 'Visual Studio Code Önbelleği': 'Visual Studio Code Cache', 'Paket Yöneticisi Önbellekleri (pip / npm)': 'Package Manager Caches (pip / npm)', 'Geliştirici Araçları': 'Developer Tools', 'Geri Dönüşüm Kutusu': 'Recycle Bin', 'DNS Çözücü Önbelleği': 'DNS Resolver Cache', 'Windows Pano İçeriği': 'Windows Clipboard', 'Çalıştır Geçmişi': 'Run History', 'Uygulama Yolları (App Paths)': 'Application Paths', "Eksik Paylaşılan DLL'ler": 'Missing Shared DLLs', 'Başlangıç Programları Hataları': 'Invalid Startup Entries', 'MUI Önbelleği Kalıntıları': 'MUI Cache Entries', 'Eksik Font Tanımlamaları': 'Missing Fonts', 'Kullanılmayan Dosya Uzantıları': 'Unused File Extensions', 'Artık girdiler ve eksik yollar sistemden güvenle temizlendi.': 'Leftover entries and invalid paths were removed.'})

# Dynamic messages retain their original text so language changes are reversible.
TEMPLATES = {
"RAM: %{value} Dolu": "RAM: {value}% Used",
"Disk (C:): {value} Boş": "Disk (C:): {value} Free",
"{count} Uygulama Güncellemesi Mevcut! ⚠️": "{count} Application Updates Available! ⚠️",
"{name} Güncelleniyor": "Updating {name}",
"{old}  ➔  {new} paketi indiriliyor ve kuruluyor...": "Downloading and installing {old} ➔ {new}...",
"Güncelleme: {name}": "Update: {name}",
"Taranıyor: {name} ({current}/{total})": "Scanning: {name} ({current}/{total})",
"Temizleniyor: {name} ({current}/{total})": "Cleaning: {name} ({current}/{total})",
"{count} Uygulama": "{count} Apps",
"{count} yüksek etki algılandı": "{count} high-impact apps",
"{value} Boşaltılacak": "{value} to Free",
"{count} adet geçici dosya, önbellek ve çöp kutusu öğesi.": "{count} temporary files, cache and recycle bin items.",
"Temizlenmeye hazır {size} gereksiz dosya ve optimize edilebilecek arka plan uygulamaları bulundu.": "Found {size} of unnecessary files and background apps to optimize.",
}

TEMPLATES.update({'{count} yüksek bellek tüketimi': '{count} high-memory apps',
 'Analiz Tamamlandı: {size} kaldırılabilir dosya ({count} Öğe)': 'Analysis Complete: {size} removable files '
                                                                 '({count} Items)',
 'Seçilen {size} boyutundaki gereksiz dosyalar\nkalıcı olarak silinecektir.\nDevam etmek istiyor musunuz?': 'Selected '
                                                                                                            'files '
                                                                                                            'totaling '
                                                                                                            '{size} '
                                                                                                            'will '
                                                                                                            'be '
                                                                                                            'permanently '
                                                                                                            'deleted.\n'
                                                                                                            'Continue?',
 'Temizleme Tamamlandı: {size} Alan Açıldı! 🎉': 'Cleanup Complete: {size} Freed! 🎉',
 '{count} dosya   ': '{count} files   ',
 'Örnek: {path}': 'Example: {path}',
 '{size} Boşaltıldı': '{size} Freed',
 'Analiz ediliyor: {name} ({current}/{total})': 'Analyzing: {name} ({current}/{total})',
 'Temizlenen Alan: {size}  •  Rahatlatılan RAM: {ram} MB\nWeb izleyicileri ve geçici sistem çöpleri başarıyla temizlendi.': 'Space '
                                                                                                                            'Freed: '
                                                                                                                            '{size}  '
                                                                                                                            '•  '
                                                                                                                            'RAM '
                                                                                                                            'Freed: '
                                                                                                                            '{ram} '
                                                                                                                            'MB\n'
                                                                                                                            'Web '
                                                                                                                            'trackers '
                                                                                                                            'and '
                                                                                                                            'temporary '
                                                                                                                            'files '
                                                                                                                            'were '
                                                                                                                            'cleaned.',
 '{count} dosya': '{count} files',
 'Dosya Boyutu: {size}  |  Gereksiz Kaplanan Alan: {waste}': 'File Size: {size}  |  Wasted Space: {waste}',
 'Tarama Tamamlandı: {count} Sorun Bulundu! ⚠️': 'Scan Complete: {count} Issues Found! ⚠️',
 '{count} sorun başarıyla çözüldü.': '{count} issues repaired.',
 '{count} Kayıt Defteri Sorunu Başarıyla Düzeltildi!': '{count} Registry Issues Repaired!',
 'Sürücü Taraması Tamamlandı: {count} Donanım Denetlendi': 'Driver Scan Complete: {count} Devices Checked',
 '● {status}': '● {status}',
 '[{category}] {name}': '[{category}] {name}'})

def set_language(language):
    global _language
    _language = language if language in ("tr", "en") else "tr"

def get_language():
    return _language

_patterns = []
for source, target in TEMPLATES.items():
    keys = re.findall(r"\{(\w+)\}", source)
    pattern = re.escape(source)
    for key in keys:
        pattern = pattern.replace(re.escape("{" + key + "}"), f"(?P<{key}>.+?)")
    _patterns.append((re.compile("^" + pattern + "$", re.DOTALL), target))

def tr(text):
    if _language != "en" or not isinstance(text, str):
        return text
    if text in EN:
        return EN[text]
    for pattern, target in _patterns:
        match = pattern.fullmatch(text)
        if match:
            return target.format(**{key: tr(value) for key, value in match.groupdict().items()})
    return text
