import telebot
import numpy as np
import io

# 1. MASUKKAN TOKEN BOT TELEGRAM KAMU DI SINI
# Dapatkan token dari @BotFather di Telegram
TOKEN = '7831459396:AAFyd2uoJC-IMYauKzdU5lbXCgRJq5onYas'
bot = telebot.TeleBot(TOKEN)

# 2. PARAMETER BATAS IZIN (SNI 1726:2019 & FEMA 356)
BATAS_DRIFT = 0.020  # Batas izin inter-story drift (misal: 2%)
BATAS_DC = 1.00      # Batas aman Demand/Capacity Ratio kolom

# 3. HANDLER UNTUK PERINTAH /start
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    pesan_pembuka = (
        "🏛️ *Sistem Cerdas IKP (Indeks Kebutuhan Peredam)*\n"
        "🎓 *Tesis S2 Magister Teknik Sipil - Universitas Mercu Buana*\n"
        "👨‍💻 Oleh: Bagus Karunia Ananda\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Halo! Sistem siap menerima data. Silakan unggah file database hasil analisis ETABS (.csv) untuk dievaluasi secara otomatis.\n\n"
        "📌 *Panduan Format Kolom (Tanpa Header):*\n"
        "`Lantai, Drift, DC_Ratio`"
    )
    bot.reply_to(message, pesan_pembuka, parse_mode='Markdown')

# 4. HANDLER UNTUK MEMBACA FILE DOKUMEN YANG DIUNGGAH
@bot.message_handler(content_types=['document'])
def handle_docs(message):
    try:
        bot.reply_to(message, "⏳ Memproses data matriks ETABS dengan Numpy...")

        # Mengunduh file dari Telegram
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Membaca data menggunakan Numpy (Asumsi format CSV dipisahkan koma)
        # Melewati baris pertama (skip_header=1) jika ada judul kolom
        data_string = downloaded_file.decode('utf-8')
        data = np.genfromtxt(io.StringIO(data_string), delimiter=',', skip_header=1)

        # Ekstraksi Array (Persamaan 2.12)
        lantai = data[:, 0]
        drift = data[:, 1]
        dc_ratio = data[:, 2]

        max_drift = np.max(drift)
        max_dc = np.max(dc_ratio)

        # 5. ALGORITMA KEPUTUSAN / DECISION LOGIC (Persamaan 2.13)
        status = ""
        rekomendasi = ""

        if np.any(drift > BATAS_DRIFT) or np.any(dc_ratio > BATAS_DC):
            status = "🔴 TIDAK AMAN"
            # Mencari lantai berapa saja yang gagal
            lantai_kritis = lantai[(drift > BATAS_DRIFT) | (dc_ratio > BATAS_DC)]
            lantai_str = ", ".join(str(int(l)) for l in lantai_kritis)
            rekomendasi = f"Perbesar diameter atau tambah jumlah kawat SMA pada Lantai: {lantai_str}."
            
        elif np.all(drift <= 0.5 * BATAS_DRIFT) and np.all(dc_ratio < 0.5):
            status = "🟡 OVERKILL (BOROS)"
            rekomendasi = "Dimensi kawat SMA terlalu masif. Kurangi diameter untuk efisiensi biaya (Life-Cycle Cost)."
            
        else:
            status = "🟢 OPTIMAL"
            rekomendasi = "Desain sudah memenuhi kriteria SNI 1726:2019 dan FEMA 356. Struktur asimetris aman terhadap torsi. Siap dieksekusi!"

        # 6. MENYUSUN OUTPUT LAPORAN
        report = (
            f"📊 *[DSS-SMA REPORT: ANALISIS KINERJA STRUKTUR]*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📂 File: `{message.document.file_name}`\n"
            f"🏢 Jumlah Lantai: {len(lantai)} Lantai\n"
            f"📋 Acuan: SNI 1726:2019 & FEMA 356\n\n"
            f"🔍 *HASIL EVALUASI MAKSIMUM:*\n"
            f"• Max Inter-story Drift: `{max_drift:.4f}` (Batas: {BATAS_DRIFT})\n"
            f"• Max D/C Ratio Kolom: `{max_dc:.2f}` (Batas: {BATAS_DC:.2f})\n\n"
            f"💡 *STATUS KELAYAKAN DESAIN:*\n"
            f"{status}\n\n"
            f"🛠️ *REKOMENDASI TEKNIS:*\n"
            f"_{rekomendasi}_"
        )

        bot.reply_to(message, report, parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"❌ Terjadi kesalahan komputasi matriks. Pastikan format CSV sudah benar!\nDetail: {e}")

# Memulai loop agar bot terus berjalan
if __name__ == '__main__':
    print("Bot DSS-SMA sedang berjalan...")
    bot.polling(none_stop=True)