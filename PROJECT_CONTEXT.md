# PROJECT_CONTEXT — parkir-video-recorder

## Fungsi Utama
Merekam video dari IP camera untuk dokumentasi/keamanan.

## Teknologi
- **Bahasa:** Python 3.11
- **Framework:** Flask
- **Video:** OpenCV, NumPy
- **Config:** YAML

## Entry Point

Koreksi hasil scan source 2026-06-10:

- **File:** `src/recording_service.py`
- **Port:** `5050`
- **Host:** `127.0.0.1`
- **Run:** `python src/recording_service.py`
- Catatan: info lama "Perlu dikonfirmasi" di bawah adalah status sebelum source ini dibaca.

## API Endpoint

| Method | Path | Fungsi |
|---|---|---|
| GET | `/status` | Status kamera, buffer, dan recording aktif |
| GET | `/snapshot?notrans=<notrans>` | Ambil snapshot JPG |
| GET | `/start?notrans=<notrans>` | Mulai rekam video untuk transaksi |
| GET | `/stop?notrans=<session>&delay=5` | Stop recording dengan delay opsional |
| GET | `/stopall` | Stop semua recording aktif |

## Konfigurasi Source

- RTSP aktif di `config.yaml`: `rtsp://admin:akatsuki86@192.168.1.81:554/Streaming/Channels/102`.
- Output video aktif: `Z:\Video_Keluar`.
- Snapshot memakai `foto_dir` jika ada di config; jika tidak, default ke `output_dir`.
- Struktur folder dari `notrans`: `20YYMM/DD`.
- Format video: `.avi` dengan codec XVID.

Source utama sudah ditemukan di `src/recording_service.py`; catatan lama tentang `src/main.py` tidak berlaku.

## File/Folder Penting
| Path | Fungsi |
|---|---|
| `src/recording_service.py` | Service Flask video recorder |
| `config.yaml` | RTSP, port, output_dir, buffer, resolusi |
| `requirements.txt` | Dependencies Python |
| `venv/` | Virtual environment |
| `install.bat` / `install.ps1` | Install script |

## Dependencies (dari venv)
- Flask 3.1.3 — web framework
- OpenCV 4.13.0 — video capture/processing
- NumPy 2.4.6 — array processing
- PyYAML 6.0.3 — config parsing

## Relasi
- **IP Camera:** Capture video stream dari kamera parkir
- **parkir-auto-cleanup:** File video yang direkam dibersihkan service ini

## Risiko Jika Mati/Diubah
- Tidak ada rekaman video
- Tidak kritis untuk transaksi parkir

## Catatan Debugging
- Cek status: `curl http://127.0.0.1:5050/status`
- Snapshot manual: `curl "http://127.0.0.1:5050/snapshot?notrans=<notrans>"`
- Start/stop manual: `/start?notrans=<notrans>` lalu `/stop?notrans=<notrans>&delay=5`.
- Cek folder output `Z:\Video_Keluar` dan pastikan service punya akses tulis.
- Perlu dikonfirmasi apakah `foto_dir` di-set pada config produksi; config yang discan tidak memuatnya.

## Status Dokumentasi

Catatan 2026-06-10: source utama sudah ditemukan. Yang masih perlu dikonfirmasi hanya deployment service aktif, apakah `foto_dir` diset di config produksi, dan apakah cleanup sudah mengarah ke `Z:\Video_Keluar`.
