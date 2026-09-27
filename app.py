import os
import random
import streamlit as st
from dotenv import load_dotenv

from rag_chatbot import (
    KNOWLEDGE_DIR,
    SYSTEM_PROMPT_PATH,
    TOP_K,
    buat_model,
    muat_dokumen,
    bangun_vectorstore,
    muat_system_prompt,
    buat_rag_chain,
)


# ============================================================
# 1. PENGATURAN HALAMAN
# ============================================================
# Wajib jadi perintah Streamlit pertama: judul tab browser dan ikonnya.

st.set_page_config(
    page_title="Asisten Jakarta Travel Guide",
    page_icon="🧳",
)
AVATAR_USER = "🧑"
AVATAR_ASSISTANT = "🤖"

st.markdown("""
<style>
[data-testid="stChatMessage"]:has(.stChatMessageContent[data-testid="user"]) {
    flex-direction: row-reverse;
}
[data-testid="stChatMessage"]:has(.stChatMessageContent[data-testid="user"])
    div[data-testid="stChatMessageContent"] {
    background-color: #FFE3C2;
    border-radius: 16px 16px 2px 16px;
    padding: 10px 14px;
}
[data-testid="stChatMessage"]:has(.stChatMessageContent[data-testid="assistant"])
    div[data-testid="stChatMessageContent"] {
    background-color: #F0F0F0;
    border-radius: 16px 16px 16px 2px;
    padding: 10px 14px;
}
.st-emotion-cache-16z1uqk {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    width: 2.5rem !important;
    height: 2.5rem !important;
    font-size: 1.6rem !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. CEK API KEY
# ============================================================
# Di laptop, GROQ_API_KEY dibaca dari file .env.
# Di Streamlit Cloud, GROQ_API_KEY diisi lewat menu Secrets, dan Streamlit
# otomatis menjadikannya environment variable. Jadi kode yang sama ini
# jalan di dua tempat tanpa perlu diubah.

load_dotenv()
if not os.getenv("GROQ_API_KEY"):
    st.error(
        "GROQ_API_KEY belum diisi. Cek file .env (di laptop) "
        "atau menu Secrets (di Streamlit Cloud)."
    )
    st.stop()

# ============================================================
# 3. SIAPKAN MESIN CHATBOT (sekali saja, lalu disimpan)
# ============================================================
# Streamlit menjalankan ulang SELURUH file ini dari atas setiap kali
# pengguna berinteraksi (misalnya mengirim pertanyaan).
# @st.cache_resource membuat fungsi di bawah ini cukup dijalankan SEKALI.
# Hasilnya disimpan, lalu dipakai ulang, sehingga dokumen tidak dimuat
# ulang dan vector store tidak dibangun ulang di setiap pertanyaan.

PESAN_LOADING = [
    "Lagi nyiapin chatbot nih, tunggu sebentar ye...",
    "Lagi nyusun rute jalan-jalan terbaik di Jakarte...",
    "Ngecek tempat wisata paling hits dulu ye...",
    "Sabar ye, kite lagi packing info kuliner di Jakarte...",
]

@st.cache_resource(show_spinner=random.choice(PESAN_LOADING))
def siapkan_chatbot():
    model = buat_model()
    dokumen = muat_dokumen(KNOWLEDGE_DIR)
    vectorstore = bangun_vectorstore(dokumen)
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    system_prompt = muat_system_prompt(SYSTEM_PROMPT_PATH)
    chain = buat_rag_chain(retriever, model, system_prompt)
    # Retriever dan jumlah dokumen ikut dikembalikan supaya UI bisa
    # menampilkan sumber jawaban dan metrik kecil di sidebar.
    return {
        "chain": chain,
        "retriever": retriever,
        "jumlah_dokumen": len(dokumen),
    }


chatbot = siapkan_chatbot()
rag_chain = chatbot["chain"]
retriever = chatbot["retriever"]


# ============================================================
# 4. BUKU CATATAN PERCAKAPAN
# ============================================================
# st.session_state adalah tempat menyimpan data yang tidak ikut hilang
# saat file ini dijalankan ulang. Di sini dipakai untuk mencatat riwayat
# percakapan: siapa yang bicara ("user" atau "assistant") dan isinya.
# Sama saja dengan menjaga percakapan terus muncul di atas chat baru

if "riwayat" not in st.session_state:
    st.session_state.riwayat = []
    if "halaman" not in st.session_state:
        st.session_state.halaman = "landing"

# ============================================================
# 5. TAMPILAN
# ============================================================
if st.session_state.halaman == "landing":
    st.title("Jakarta Travel Guide Punyamu! 🧳")
    st.write("Tanyakan apa saja pada kami seputar Destinasi Wisata di Jakarta 😁👌")
    if st.button("Mulai", use_container_width=True, type="primary"):
        st.session_state.halaman = "chat"
        st.rerun()

else:
    with st.sidebar:
        st.header("Tentang chatbot ini")
        st.write(
            "Chatbot ini menjawab pertanyaan berdasarkan Jakarta Travel Guide Book "
            "tentang Destinasi Wisata yang ada di Kota Jakarta"
        )
        st.caption("Jawaban hanya diambil dari dokumen sumber, bukan dari internet. Dibuat oleh Dennis Fahriansyah")

        st.divider()
        st.metric("Dokumen sumber ter-load", chatbot["jumlah_dokumen"])
        st.badge("openai/gpt-oss-120b via Groq", icon=":material/bolt:", color="green")

        st.divider()
        if st.button("Mulai percakapan baru", use_container_width=True):
            st.session_state.riwayat = []
            st.rerun()

    kolom_atas = st.columns([5, 1])
    with kolom_atas[0]:
        st.title("Jakarta Travel Guide Punyamu!")
        st.caption("Tanyakan apa saja pada kami seputar Destinasi Wisata di Jakarta 😁👌")
    with kolom_atas[1]:
        if st.button("🚪 Keluar", use_container_width=True):
            st.session_state.halaman = "landing"
            st.session_state.riwayat = []
            st.rerun()

    # Salam pembuka + contoh pertanyaan (tombol), hanya tampil kalau
    # percakapan belum dimulai sama sekali.
    CONTOH_PERTANYAAN = [
        "Coba kasih 3 rekomendasi wisata di Jakarta",
        "Apa saja destinasi wisata di daerah Jakarta Barat",
        "Mau ke Jakarta Pusat, ada saran jalan-jalan kemana?",
    ]
    SARAN_LANJUTAN = [
    "Rekomendasi kuliner khas Betawi apa aja ya?",
    "Transportasi umum ke sana naik apa?",
    "Apa aja wisata museum di Jakarta?",
    "Cocok buat wisata keluarga nggak?",
    "Ada saran tempat liburan bersama teman di Jakarta?",
    "3 rekomendasi tempat wisata bareng keluarga!",
    ]

    def tampilkan_saran_lanjutan(index_unik):
        saran = random.sample(SARAN_LANJUTAN, k=3)
        st.caption("💡 Mungkin kamu juga mau tanya:")
        kolom = st.columns(len(saran))
        for kol, teks in zip(kolom, saran):
            if kol.button(teks, use_container_width=True, key=f"saran_{index_unik}_{teks}"):
                st.session_state.pertanyaan_terpilih = teks

    if not st.session_state.riwayat:
        with st.chat_message("assistant", avatar=AVATAR_ASSISTANT):
            st.markdown("Halo, silakan ajukan pertanyaan, atau coba salah satu contoh berikut:")
            kolom = st.columns(len(CONTOH_PERTANYAAN))
            for kol, teks in zip(kolom, CONTOH_PERTANYAAN):
                if kol.button(teks, use_container_width=True):
                    st.session_state.pertanyaan_terpilih = teks

    # Tampilkan ulang seluruh riwayat percakapan dari buku catatan.
    for i, pesan in enumerate(st.session_state.riwayat):
        avatar = AVATAR_USER if pesan["role"] == "user" else AVATAR_ASSISTANT
        with st.chat_message(pesan["role"], avatar=avatar):
            st.markdown(pesan["isi"])
            if pesan["role"] == "assistant":
                st.feedback("thumbs", key=f"feedback_{i}")
                if i == len(st.session_state.riwayat) - 1:
                    tampilkan_saran_lanjutan(f"riwayat_{i}")


# ============================================================
# 6. TANYA JAWAB
# ============================================================

    pertanyaan = st.chat_input("Tulis pertanyaan Anda di sini...")

    # Kalau user klik tombol contoh pertanyaan, itu dianggap sama seperti
    # mengetik pertanyaan lewat chat_input.
    if not pertanyaan and "pertanyaan_terpilih" in st.session_state:
        pertanyaan = st.session_state.pop("pertanyaan_terpilih")

    if pertanyaan:
        # Tampilkan pertanyaan, lalu catat ke buku catatan.
        with st.chat_message("user", avatar=AVATAR_USER):
            st.markdown(pertanyaan)
        st.session_state.riwayat.append({"role": "user", "isi": pertanyaan, "sumber": None})

        # Minta jawaban ke mesin RAG. st.status kasih label bertahap supaya
        # proses retrieval -> generation kelihatan transparan, bukan cuma
        # "loading" generik. .stream() + st.write_stream() membuat jawaban
        # muncul bertahap, kata demi kata, seperti sedang diketik.
        with st.chat_message("assistant", avatar=AVATAR_ASSISTANT):
            with st.status("Mencari dokumen relevan...", expanded=False) as status:
                dokumen_sumber = retriever.invoke(pertanyaan)
                status.update(label="Menyusun jawaban...")
                jawaban = st.write_stream(rag_chain.stream(pertanyaan))
                status.update(label="Selesai", state="complete")

            st.feedback("thumbs", key=f"feedback_{len(st.session_state.riwayat)}")
            tampilkan_saran_lanjutan(f"baru_{len(st.session_state.riwayat)}")

        st.session_state.riwayat.append(
            {"role": "assistant", "isi": jawaban, "sumber": None}
        )