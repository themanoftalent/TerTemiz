# TerTemiz Professional 7.0.2 (Windows)

**TerTemiz**, Windows için optimize edilmiş gerçek sistem temizleme motorunu sunan yerli ve gelişmiş masaüstü bakım uygulamasıdır.

![TerTemiz Logo](assets/tertemiz_logo.png)

---

## 🚀 Başlıca Özellikler

### 1. 🩺 Sağlık Kontrolü (Health Check)
* **Tek Tıkla Tarama**: Gizlilik, Depolama Alanı, Hız ve Güvenlik durumunu tek tuşla inceler.
* **Akıllı Analiz**: Web izleyicilerini, geçici sistem çöplerini ve arka plan yüklerini tespit eder.
* **Daha İyi Hale Getir**: Tek dokunuşla tüm gereksiz dosyaları temizler, RAM'i rahatlatır ve bilgisayarı hızlandırır.

### 2. 🧹 Özel Temizleme (Custom Clean)
* **Kategorik Seçim Ağacı**:
  * **Windows**: Sistem (Geri Dönüşüm Kutusu, Temp, WER, Minidump, DNS Önbelleği, Pano), Gezgin (Küçük Resim Önbelleği, Son Dosyalar, Çalıştır Geçmişi), Microsoft Edge.
  * **Uygulamalar**: Google Chrome, Mozilla Firefox, Brave, Discord, Spotify, VS Code, pip / npm paket önbellekleri.
* **Analiz ve Temizleme**: Dosya sayısını ve açılacak disk alanını tam olarak listeler, silmeden önce kullanıcı onayı alır.

### 3. ⚡ Performans İyileştirici (Performance Optimizer)
* **Canlı Süreç ve RAM İzleme**: Çalışan arka plan uygulamalarının bellek (RAM) ve CPU tüketimini izler.
* **Uyku Modu (Sleep / Suspend)**: Ağır arka plan uygulamalarını kapatmadan uyku moduna alarak sistem yükünü düşürür.
* **🚀 RAM'i Rahatlat**: Windows Working Set optimizasyonunu tetikleyerek çalışan süreçlerin gereksiz belleğini anında tahliye eder.

### 4. 🔄 Sürücü Güncelleyici (Driver Updater)
* **Donanım ve Sürücü Analizi**: Sistemdeki tüm ekran kartı, ses, ağ, bluetooth ve çevre birim sürücülerini (pnputil) denetler.
* **Sürücü Durumu**: Güncel ve güncelleme önerilen donanımları kategorilerine göre listeler.

### 5. 📑 Kayıt Defteri Temizleyici (Registry Cleaner)
* **Güvenli Kayıt Taraması**:
  * Eksik Paylaşılan DLL'ler
  * Uygulama Yolları Hataları (App Paths)
  * Başlangıç Programları Hataları
  * MUI Önbelleği Kalıntıları
  * Eksik Font Tanımlamaları
  * Kullanılmayan Dosya Uzantıları
* **Güvenli Yedekleme (.reg Export)**: Değişiklik yapmadan önce kullanıcıya kayıt defterini yedekleme seçeneği sunar (`TerTemiz_Registry_Backup_*.reg`).

### 6. 🛠️ Araçlar (Tools)
* **Uygulama Kaldırıcı (Uninstall Manager)**: Windows Registry'deki tüm yüklü programları listeler, filtreler, kaldırıcıyı başlatır veya artık kayıt girdisini siler.
* **Başlangıç Yöneticisi (Startup Manager)**: Windows açılışında başlayan programları yönetir ve devre dışı bırakır.
* **Disk Alanı Analizörü (Disk Analyzer)**: Disk veya klasörleri tarar, dosyaları türlerine göre (Medya, Resim, Müzik, Belge, Arşiv vb.) gruplar ve en büyük dosyaları gösterir.
* **Çift Dosya Bulucu (Duplicate Finder)**: Belirlenen klasördeki aynı boyutta ve içerikteki mükerrer dosyaları tespit eder.
* **Sistem Özellikleri**: Windows sürümü, CPU, RAM, GPU ve Disk durumunu detaylı görüntüler.

### 7. ⚙️ Seçenekler (Settings)
* **Koyu / Açık / Sistem Teması**: Dinamik arayüz renkleri.
* **Akıllı Temizleme**: Otomatik eşik uyarıları ve tarayıcı temizliği.
* **Lisans Durumu**: TerTemiz Professional v7.0.2 ömür boyu aktif lisans rozeti.

---

## ☕ Sponsor or Buy Me a Coffee

If you find this project helpful, consider supporting it or reaching out for collaboration:

[![Buy Me A Coffee](https://img.shields.io/badge/BUY%20ME%20A%20COFFEE-SUPPORT%20PROJECT-green?style=for-the-badge&logo=buymeacoffee)](https://buymeacoffee.com/themanoftalent) [![GitHub Sponsors](https://img.shields.io/badge/SPONSOR-GITHUB%20SPONSORS-ea4aaa?style=for-the-badge&logo=githubsponsors)](https://github.com/sponsors/themanoftalent) [![Let's Connect](https://img.shields.io/badge/LET%27S%20CONNECT-EMAIL-blue?style=for-the-badge&logo=gmail)](mailto:cs.akifcifci@gmail.com)


## Kurulum ve Geliştirme

Windows 10/11 ve Python 3.11 veya üzeri gerektirir. Kaynaktan çalıştırmak için:

```powershell
py -m pip install -r requirements.txt
py main.py
```

Çalıştırılabilir Windows paketi, GitHub **Actions → Windows tests and build** çalışmasının
**TerTemiz-Windows** çıktısından indirilebilir. ZIP dosyasının tamamını çıkartın;
`dist/TerTemiz/TerTemiz.exe` dosyasını çalıştırın veya `install.ps1` ile kurun.

Uygulama güncellemeleri için Microsoft **App Installer (WinGet)** gerekir.
WinGet kaynak sözleşmesi hatası varsa bir Windows terminalinde `winget upgrade --source winget`
çalıştırın ve gösterilen sözleşmeyi okuyup yanıtlayın. Uygulamadaki güncelleme işlemi,
lisans ve yönetici izinleri için ayrı bir WinGet penceresi açar.
Sürücü güncelleme düğmeleri Windows Update'in isteğe bağlı güncellemeler ekranını açar.

Türkçe/English ve Koyu/Açık/Sistem tema tercihleri anında uygulanır ve
`%LOCALAPPDATA%/TerTemiz/preferences.json` dosyasına kaydedilir.

```powershell
py -m unittest discover -s tests -v
py tests/windows_ui_smoke.py
py -m pip install -r requirements-dev.txt
py -m PyInstaller --noconfirm TerTemiz.spec
```

Arayüz testi otomatik taramaları sabit test verileriyle değiştirir; dosya temizlemez,
kayıt defterini değiştirmez ve gerçek program güncellemesi kurmaz.
