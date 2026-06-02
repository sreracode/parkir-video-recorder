# Parkir Video Recorder

Merekam video dari RTSP camera untuk SMARTPARK. Dipicu via HTTP endpoint saat kendaraan keluar.

## API Endpoints

- `GET /status` — Status kamera & session aktif
- `GET /start?notrans=TRX001` — Mulai rekam
- `GET /stop?notrans=<session_id>&delay=5` — Stop rekam
- `GET /stopall` — Stop semua

## Instalasi

Jalankan `install.bat` sebagai Administrator.

## Konfigurasi

Edit `config.yaml` untuk mengubah:
- Port service
- RTSP URL kamera
- Folder output video
