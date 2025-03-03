import requests
from django.shortcuts import render, redirect
import os 
from datetime import datetime  

# URL Pocketbase
POCKETBASE_URL = "http://127.0.0.1:8090/api/collections/guestsbook/records"

# Halaman utama form izin
def index(request):
    return render(request, 'izin/index.html')

# Submit izin berdasarkan NISN
def submit_izin(request):
    if request.method == 'POST':
        nisn = request.POST['nisn']
        nama = request.POST['nama']
        kelas = request.POST['kelas']
        category = request.POST['category']
        reason = request.POST['reason']
        date = request.POST['date']  # Ambil tanggal

        # Jika kategori adalah "izin_keluar", ambil waktu izin keluar
        start_time = request.POST.get('start_time', None)
        end_time = request.POST.get('end_time', None)

        # Validasi NISN hanya angka
        if not nisn.isdigit():
            return render(request, 'izin/index.html', {'error': 'NISN hanya boleh berisi angka'})

        # Validasi input lain
        if not all([nisn, nama, kelas, category, reason, date]):
            return render(request, 'izin/index.html', {'error': 'Semua field wajib diisi'})

        # Kirim data ke Pocketbase
        data = {
            "nisn": nisn,
            "nama": nama,
            "kelas": kelas,
            "category": category,
            "reason": reason,
            "tanggal": date,  # Tambahkan tanggal ke data
        }

        # Tambahkan waktu jika kategori izin_keluar
        if category == "izin_keluar":
            if not (start_time and end_time):
                return render(request, 'izin/index.html', {'error': 'Waktu mulai dan selesai wajib diisi untuk izin keluar'})

            try:
                # Parsing waktu dengan format HH:MM
                fmt = '%H:%M'
                start = datetime.strptime(start_time, fmt)
                end = datetime.strptime(end_time, fmt)

                # Hitung selisih waktu dalam menit
                duration = int((end - start).total_seconds() / 60)

                data["start_time"] = start_time
                data["end_time"] = end_time
                data["duration_minutes"] = duration  # Simpan durasi dalam hitungan menit
                data["jam"] = f"{start_time} - {end_time} ({duration})" 

            except ValueError:
                return render(request, 'izin/index.html', {'error': 'Format waktu harus HH:MM'})

        # Authorization token (ambil dari environment variable)
        token = os.getenv('POCKETBASE_TOKEN', 'default_token')
        headers = {
            "authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb2xsZWN0aW9uSWQiOiJwYmNfMzE0MjYzNTgyMyIsImV4cCI6MTgwNDA0NzQ1MywiaWQiOiJ1dWczNTJmaTZlazY0ZTciLCJyZWZyZXNoYWJsZSI6ZmFsc2UsInR5cGUiOiJhdXRoIn0.jAh-ypZx4q28V-jVdlQoO6BICJcQJwIxp1ZDm55dIS4"
        }

        try:
            response = requests.post(POCKETBASE_URL, json=data, headers=headers)
            response.raise_for_status()  # Raise exception jika status code tidak 200
        except requests.exceptions.HTTPError as http_err:
            return render(request, 'izin/index.html', {'error': f'HTTP error occurred: {http_err}'})
        except Exception as err:
            return render(request, 'izin/index.html', {'error': f'Error occurred: {err}'})

        # Jika berhasil
        if response.status_code == 200:
            return redirect('success')
        else:
            return render(request, 'izin/index.html', {'error': 'Gagal mengirim data'})

    return redirect('index')

# Halaman success setelah data berhasil dikirim
def success(request):
    return render(request, 'izin/success.html')
