
import gradio as gr
import json
import re
from pathlib import Path
from datetime import datetime, timezone

APP_NAME = "Kids Animation Studio AI"

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def buat_storyboard(judul, tema, durasi, bahasa, karakter, tujuan):
    if not judul.strip() or not tema.strip():
        raise gr.Error("Judul dan tema cerita wajib diisi.")

    durasi = int(durasi)
    total = durasi * 60

    adegan = [
        ("Pembukaan", 0.10, "Perkenalkan karakter dan tempat cerita."),
        ("Rasa ingin tahu", 0.12, "Karakter menemukan sesuatu yang menarik."),
        ("Eksplorasi pertama", 0.15, "Karakter mulai belajar tema episode."),
        ("Belajar bersama", 0.16, "Semua karakter saling membantu."),
        ("Lagu anak", 0.20, "Masukkan lagu ceria dengan lirik berulang."),
        ("Permainan", 0.17, "Ajak penonton ikut bermain dan belajar."),
        ("Penutup", 0.10, "Ulangi pelajaran dan tutup cerita.")
    ]

    daftar_karakter = [
        x.strip() for x in karakter.split(",") if x.strip()
    ]

    scenes = []
    waktu = 0

    for nomor, (nama, bobot, deskripsi) in enumerate(adegan, 1):
        panjang = round(total * bobot)
        akhir = total if nomor == len(adegan) else waktu + panjang

        scenes.append({
            "nomor": nomor,
            "nama": nama,
            "mulai_detik": waktu,
            "selesai_detik": akhir,
            "deskripsi": deskripsi + " Tema: " + tema,
            "karakter": daftar_karakter
        })

        waktu = akhir

    project = {
        "judul": judul,
        "tema": tema,
        "durasi_menit": durasi,
        "bahasa": bahasa,
        "karakter": daftar_karakter,
        "tujuan_edukasi": tujuan,
        "tanggal": datetime.now(timezone.utc).isoformat(),
        "status": "Menunggu persetujuan",
        "adegan": scenes
    }

    return project


def buat_episode(judul, tema, durasi, bahasa, karakter, tujuan):
    project = buat_storyboard(
        judul, tema, durasi, bahasa, karakter, tujuan
    )

    preview = ""

    for scene in project["adegan"]:
        mulai = scene["mulai_detik"]
        selesai = scene["selesai_detik"]

        preview += (
            f"\nADEGAN {scene['nomor']}: {scene['nama']}\n"
            f"Waktu: {mulai} - {selesai} detik\n"
            f"{scene['deskripsi']}\n"
        )

    return project, preview, "Storyboard berhasil dibuat!"


def setujui_episode(project):
    if not project:
        raise gr.Error("Buat storyboard terlebih dahulu.")

    project["status"] = "Disetujui untuk tahap produksi"

    nama = re.sub(
        r"[^a-zA-Z0-9]+",
        "-",
        project["judul"]
    ).strip("-").lower()

    path = OUTPUT_DIR / f"{nama or 'episode'}.json"

    path.write_text(
        json.dumps(project, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return project, "Konsep disetujui!", str(path)


with gr.Blocks(
    title=APP_NAME,
    theme=gr.themes.Soft()
) as app:

    gr.Markdown(
        """
        # 🎬 KIDS ANIMATION STUDIO AI

        ### Studio produksi animasi anak 3D

        Buat cerita, susun storyboard, dan periksa
        konsep sebelum produksi animasi.
        """
    )

    state = gr.State(None)

    with gr.Row():

        with gr.Column():

            gr.Markdown("## INFORMASI EPISODE")

            judul = gr.Textbox(
                label="Judul Episode",
                placeholder="Bimo dan Sahabat Belajar Warna"
            )

            tema = gr.Textbox(
                label="Tema Cerita",
                placeholder="Belajar mengenal warna"
            )

            durasi = gr.Dropdown(
                choices=["3", "4", "5"],
                value="4",
                label="Durasi Video"
            )

            bahasa = gr.Dropdown(
                choices=["Bahasa Indonesia", "English"],
                value="Bahasa Indonesia",
                label="Bahasa"
            )

            karakter = gr.Textbox(
                label="Karakter",
                value="Bimo, Lala, Bubu, Milo"
            )

            tujuan = gr.Textbox(
                label="Tujuan Edukasi",
                placeholder="Mengenal warna dasar"
            )

            tombol = gr.Button(
                "BUAT STORYBOARD",
                variant="primary"
            )

        with gr.Column():

            gr.Markdown("## HASIL STORYBOARD")

            status = gr.Markdown("Belum ada episode.")

            preview = gr.Textbox(
                label="Rancangan Adegan",
                lines=20,
                interactive=False
            )

            setuju = gr.Button(
                "SETUJUI KONSEP EPISODE",
                variant="secondary"
            )

            hasil = gr.Markdown()
            download = gr.File(label="Download Proyek JSON")

    tombol.click(
        buat_episode,
        inputs=[
            judul,
            tema,
            durasi,
            bahasa,
            karakter,
            tujuan
        ],
        outputs=[state, preview, status]
    )

    setuju.click(
        setujui_episode,
        inputs=[state],
        outputs=[state, hasil, download]
    )

    gr.Markdown(
        """
        ---
        **KIDS ANIMATION STUDIO AI**

        Tahap 1: Perencanaan dan storyboard.

        Mesin animasi 3D akan ditambahkan pada tahap berikutnya.
        """
    )


if __name__ == "__main__":
    app.launch()
