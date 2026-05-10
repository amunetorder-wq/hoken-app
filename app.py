import streamlit as st
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import io

# --- 🎭 1. 究極のRPGデザイン（CSS） ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0a0a; color: #ffffff; }
    .stButton>button {
        width: 100%; border-radius: 10px; height: 4em;
        background-color: #111111; color: #22c55e;
        font-size: 20px; font-weight: bold; border: 2px solid #22c55e;
        box-shadow: 0 0 15px rgba(34, 197, 94, 0.2); transition: 0.3s;
    }
    .stButton>button:hover { background-color: #22c55e; color: #000000; box-shadow: 0 0 30px rgba(34, 197, 94, 0.5); }
    .scenario-card { background-color: #1a1a1a; padding: 30px; border-radius: 20px; border: 1px solid #333; margin-bottom: 20px; }
    .stProgress > div > div > div > div { background-color: #22c55e; }
    h1 { color: #ffffff !important; font-family: 'Poppins', sans-serif; }
    h2, h3 { color: #22c55e !important; }
    </style>
""", unsafe_allow_html=True)

# --- 📄 2. PDF診断書作成ロジック ---
try:
    pdfmetrics.registerFont(TTFont('MSMincho', 'C:/Windows/Fonts/msmincho.ttc'))
    font_name = 'MSMincho'
except:
    font_name = 'Helvetica'

def create_diagnosis_pdf(hp, choices):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont(font_name, 24)
    p.drawCentredString(width/2, height - 60, "STORE DEFENSE 戦略診断書")
    
    p.setFont(font_name, 14)
    p.drawString(50, height - 120, f"最終店舗生存耐久度（HP）: {hp:,} / 3,000,000")
    
    p.setFont(font_name, 18)
    if hp == 3000000:
        p.setFillColor(colors.green)
        result_text = "判定：鉄壁の守護神"
    elif hp > 1500000:
        p.setFillColor(colors.orange)
        result_text = "判定：要防衛力強化"
    else:
        p.setFillColor(colors.red)
        result_text = "判定：経営崩壊寸前"
    p.drawString(50, height - 150, result_text)
    
    p.setFillColor(colors.black)
    p.setFont(font_name, 12)
    scenarios = [
        ["リスク項目", "選択した装備", "損害（ダメージ）"],
        ["水漏れトラブル", "保険あり" if choices[0]=="A" else "未加入", "0円" if choices[0]=="A" else "1,100,000円"],
        ["食中毒リスク", "保険あり" if choices[1]=="A" else "未加入", "0円" if choices[1]=="A" else "1,500,000円"],
        ["SNS炎上・対人", "保険あり" if choices[2]=="A" else "未加入", "0円" if choices[2]=="A" else "300,000円"],
        ["ドタキャン(50名)", "保険あり" if choices[3]=="A" else "未加入", "0円" if choices[3]=="A" else "250,000円"]
    ]
    
    table = Table(scenarios, colWidths=[180, 150, 150])
    table.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), font_name, 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.black),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, height - 350)
    
    p.setFont(font_name, 14)
    p.drawString(50, height - 400, "【防衛戦略アドバイス】")
    p.setFont(font_name, 11)
    advice_y = height - 430
    advices = [
        "・今回のシミュレーション通り、突発的な事故は『確率』ではなく『いつか起きる事実』です。",
        "・特に食中毒や水漏れは、一度の発生で数百万円単位のキャッシュが流出します。",
        "・月々のわずかな保険料（MP）で、この数百万のダメージを無効化するのが賢い経営の盾です。"
    ]
    for line in advices:
        p.drawString(60, advice_y, line)
        advice_y -= 20

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- 🎮 3. ゲームメインエンジン ---
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.hp = 3000000
    st.session_state.choices = []

def next_step(damage, choice):
    st.session_state.hp -= damage
    st.session_state.choices.append(choice)
    st.session_state.step += 1

st.title("🛡️ ストア防衛RPG")

# HPゲージの表示
if st.session_state.step > 0 and st.session_state.step < 5:
    col_hp1, col_hp2 = st.columns([3, 1])
    with col_hp1:
        hp_ratio = st.session_state.hp / 3000000
        st.progress(max(0.0, hp_ratio))
    with col_hp2:
        st.write(f"**HP: {st.session_state.hp:,}**")

# --- ステージ分岐 ---
if st.session_state.step == 0:
    st.markdown('<div class="scenario-card">', unsafe_allow_html=True)
    st.subheader("序章：3年目の試練")
    st.write("開店から3年。順調だった経営に、予期せぬリスクが牙を剥く。")
    st.write("あなたの選択で、お店の未来を守り抜け！")
    if st.button("▶ ゲームを開始する"):
        st.session_state.step = 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.step == 1:
    st.subheader("STAGE 1：天井からの刺客")
    
    if os.path.exists("water_leak.mp4"):
        st.video("water_leak.mp4", autoplay=True, loop=True, muted=True)
    else:
        st.info("※水漏れの動画（water_leak.mp4）を準備中...")
        
    st.markdown('<div class="scenario-card">', unsafe_allow_html=True)
    st.write("金曜日のピーク時、2階の配管が破裂！汚水がPOSレジを直撃。")
    st.write("被害額：1,100,000円")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("【A】保険という盾で防ぐ"): next_step(0, "A"); st.rerun()
    with col2:
        if st.button("【B】気合で耐える（自腹）"): next_step(1100000, "B"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.step == 2:
    st.subheader("STAGE 2：見えない猛毒")
    
    if os.path.exists("health_inspector.mp4"):
        st.video("health_inspector.mp4", autoplay=True, loop=True, muted=True)
    else:
        st.info("※食中毒の動画（health_inspector.mp4）を準備中...")

    st.markdown('<div class="scenario-card">', unsafe_allow_html=True)
    st.write("保健所からの通告。先週末の客数名が食中毒を発症した。")
    st.write("被害額：1,500,000円（賠償金＋営業停止損害）")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("【A】PL保険を発動"): next_step(0, "A"); st.rerun()
    with col2:
        if st.button("【B】貯金を切り崩す"): next_step(1500000, "B"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.step == 3:
    st.subheader("STAGE 3：SNSという広域魔法")
    
    if os.path.exists("sns_flame.mp4"):
        st.video("sns_flame.mp4", autoplay=True, loop=True, muted=True)
    else:
        st.info("※炎上の動画（sns_flame.mp4）を準備中...")

    st.markdown('<div class="scenario-card">', unsafe_allow_html=True)
    st.write("店員がお客様の高級バッグを汚し、SNSで炎上。謝罪と補償を求められている。")
    st.write("被害額：300,000円")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("【A】施設賠償責任保険を適用"): next_step(0, "A"); st.rerun()
    with col2:
        if st.button("【B】丸腰で謝罪に行く"): next_step(300000, "B"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.step == 4:
    st.subheader("STAGE 4：消えた50人の足音")
    
    if os.path.exists("no_show.mp4"):
        st.video("no_show.mp4", autoplay=True, loop=True, muted=True)
    else:
        st.info("※ドタキャンの動画（no_show.mp4）を準備中...")

    st.markdown('<div class="scenario-card">', unsafe_allow_html=True)
    st.write("50名の団体予約がドタキャン。食材と人件費がすべて無駄に。")
    st.write("被害額：250,000円")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("【A】キャンセル保険で補填"): next_step(0, "A"); st.rerun()
    with col2:
        if st.button("【B】泣き寝入りする"): next_step(250000, "B"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.step == 5:
    st.subheader("👑 戦略レポート生成")
    st.markdown('<div class="scenario-card">', unsafe_allow_html=True)
    st.write(f"最終資金（HP）: **{st.session_state.hp:,}円**")
    
    pdf = create_diagnosis_pdf(st.session_state.hp, st.session_state.choices)
    st.download_button(
        label="📄 戦略診断書（PDF）をダウンロード",
        data=pdf,
        file_name="diagnosis_report.pdf",
        mime="application/pdf"
    )
    
    if st.button("🔄 最初からやり直す"):
        st.session_state.step = 0
        st.session_state.hp = 3000000
        st.session_state.choices = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)