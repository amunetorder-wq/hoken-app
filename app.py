import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import io

# --- 日本語フォントの設定 ---
try:
    pdfmetrics.registerFont(TTFont('MSMincho', 'C:/Windows/Fonts/msmincho.ttc'))
    font_name = 'MSMincho'
except:
    font_name = 'Helvetica'

# --- PDFを作成する関数（表形式） ---
def create_pdf(hp, choices):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # タイトル
    p.setFont(font_name, 20)
    p.drawCentredString(width / 2, height - 50, "リスク診断結果・保険提案書")

    # 基本情報
    p.setFont(font_name, 12)
    p.drawString(50, height - 100, f"最終運転資金残高: {hp:,}円")
    loss = 3000000 - hp
    p.drawString(50, height - 120, f"今回のシミュレーションによる損失合計: {loss:,}円")

    # シナリオの結果を表形式でまとめる
    scenario_names = ["水漏れ", "食中毒", "クレーム", "ドタキャン"]
    damages = [1100000, 1500000, 300000, 250000]
    
    # テーブル用のデータ作成
    data = [["トラブル内容", "あなたの選択", "実際の損失額"]]
    for i in range(len(choices)):
        choice_text = "保険あり(A)" if choices[i] == "A" else "未加入(B)"
        actual_damage = f"{0 if choices[i] == 'A' else damages[i]:,}円"
        data.append([scenario_names[i], choice_text, actual_damage])

    # テーブルのスタイル設定
    table = Table(data, colWidths=[150, 100, 150])
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), font_name, 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    # テーブルを描画
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, height - 300)

    # アドバイス
    p.drawString(50, height - 350, "【専門家のアドバイス】")
    p.setFont(font_name, 10)
    if "B" in choices:
        p.drawString(50, height - 370, "Bランクのリスクが顕在化しています。尼崎・西宮エリアでの店舗運営において、")
        p.drawString(50, height - 385, "これらのトラブルは『明日起きてもおかしくない』ものです。早急な対策を。")
    else:
        p.drawString(50, height - 370, "完璧なリスク管理です！現在の安心を維持しつつ、最新の特約についても")
        p.drawString(50, height - 385, "検討の余地があります。ぜひ一度ご相談ください。")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- アプリのメイン処理 ---
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.hp = 3000000
    st.session_state.choices = []

def next_step(damage, choice):
    st.session_state.hp -= damage
    st.session_state.choices.append(choice)
    st.session_state.step += 1

st.title("店舗防衛RPG - 3年目の試練")
st.write(f"**現在の運転資金:** {st.session_state.hp:,}円")
st.divider()

# --- 各ステップの分岐 ---
if st.session_state.step == 0:
    st.subheader("オープニング")
    st.write("おめでとうございます！お店は3年目を迎えました。しかしトラブルは突然やってきます。")
    if st.button("冒険を始める"):
        st.session_state.step = 1
        st.rerun()

elif st.session_state.step == 1:
    st.subheader("試練1：水漏れトラブル")
    st.write("2階からの水漏れでPOSレジが故障！")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("[A] 店舗総合保険"): next_step(0, "A"); st.rerun()
    with col2:
        if st.button("[B] 火災保険のみ"): next_step(1100000, "B"); st.rerun()

elif st.session_state.step == 2:
    st.subheader("試練2：食中毒トラブル")
    st.write("保健所から電話！食中毒の疑いで営業停止に。")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("[A] PL保険あり"): next_step(0, "A"); st.rerun()
    with col2:
        if st.button("[B] 未加入"): next_step(1500000, "B"); st.rerun()

elif st.session_state.step == 3:
    st.subheader("試練3：対人クレーム")
    st.write("客の高級バッグにスープをこぼしてしまった！")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("[A] 施設賠償責任保険"): next_step(0, "A"); st.rerun()
    with col2:
        if st.button("[B] 丸腰で対応"): next_step(300000, "B"); st.rerun()

elif st.session_state.step == 4:
    st.subheader("試練4：ドタキャン")
    st.write("50名の貸切予約がノーショウ（無断キャンセル）に。")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("[A] キャンセル保険"): next_step(0, "A"); st.rerun()
    with col2:
        if st.button("[B] 未加入"): next_step(250000, "B"); st.rerun()

elif st.session_state.step == 5:
    st.subheader("エンディング・診断結果")
    st.write(f"最終的な運転資金は『{st.session_state.hp:,}円』です。")
    
    # PDFデータの準備
    pdf_file = create_pdf(st.session_state.hp, st.session_state.choices)
    
    st.download_button(
        label="診断結果（PDF）をダウンロード",
        data=pdf_file,
        file_name="result.pdf",
        mime="application/pdf"
    )

    if st.button("最初からやり直す"):
        st.session_state.step = 0
        st.session_state.hp = 3000000
        st.session_state.choices = []
        st.rerun()