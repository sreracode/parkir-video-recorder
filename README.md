# Parkir Camera Service

Layanan kamera RTSP untuk SMARTPARK — mendukung **snapshot** (foto) dan **video recording**.

## API Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `GET` | `/status` | Status koneksi kamera & session aktif |
| `GET` | `/snapshot?notrans=012602180026` | Capture 1 frame → JPEG |
| `GET` | `/start?notrans=012602180026` | Mulai rekam video |
| `GET` | `/stop?notrans=012602180026&delay=5` | Stop rekam (delay opsional) |
| `GET` | `/stopall` | Stop semua recording |

## Struktur Output

File disimpan berdasarkan tanggal dari **notrans** (format: `01{gate}{YYMMDD}{counter}`).

```
{foto_dir}/
└── 202602/
    └── 18/
        └── 012602180026.jpg          ← Snapshot

{video_dir}/
└── 202602/
    └── 18/
        └── 012602180026.avi          ← Video
```

## Konfigurasi (`config.yaml`)

```yaml
server:
  port: 5050
  host: 127.0.0.1
camera:
  rtsp_url: rtsp://admin:pass@192.168.1.81:554/Streaming/Channels/102
  fps: 25
  width: 1280
  height: 720
  buffer_seconds: 10       # Pre-roll buffer (detik)
paths:
  foto_dir: Z:\Foto_Masuk         # Folder snapshot
  output_dir: Z:\Video_Keluar     # Folder video
```

## Fitur

- **Pre-roll buffer**: 10 detik frame sebelum rekam dimulai ikut tersimpan
- **Overwrite**: File lama ditimpa jika notrans sama
- **Subfolder otomatis**: `YYYYMM/DD` dari notrans
- **Delayed stop**: Delay detik untuk rekam gerbang keluar

## Instalasi

Jalankan `install.ps1` sebagai Administrator. Atau via master installer:

```powershell
..\parkir-installer\install.ps1
```

## Teknologi

- **Flask** — HTTP server
- **OpenCV** — RTSP stream & video encoding (XVID/AVI)
- **NSSM** — Windows service wrapper

---

Dikembangkan untuk **SMARTPARK** — Situsindo Prima.
