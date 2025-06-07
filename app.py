import streamlit as st
from datetime import datetime, timedelta
from fpdf import FPDF
import os

st.set_page_config(page_title="SEO 合約工具", layout="centered", initial_sidebar_state="collapsed")

def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")

def format_date_zh(date_obj):
    return f"{date_obj.year}年{date_obj.month}月{date_obj.day}日"

def calculate_effective_days(start, end, exclusion_ranges):
    current = start
    charge_ranges = []
    nocharge_ranges = []
    while current < end:
        in_exclusion = False
        for exc_start, exc_end in exclusion_ranges:
            if exc_start <= current < exc_end:
                in_exclusion = True
                break
        next_day = current + timedelta(days=1)
        if in_exclusion:
            if not nocharge_ranges or nocharge_ranges[-1][1] != current:
                nocharge_ranges.append([current, next_day])
            else:
                nocharge_ranges[-1][1] = next_day
        else:
            if not charge_ranges or charge_ranges[-1][1] != current:
                charge_ranges.append([current, next_day])
            else:
                charge_ranges[-1][1] = next_day
        current = next_day
    charge_ranges = [(s, e) for s, e in charge_ranges]
    nocharge_ranges = [(s, e) for s, e in nocharge_ranges]
    total_excluded = sum((e - s).days for s, e in nocharge_ranges)
    return charge_ranges, nocharge_ranges, total_excluded

class PDFReport(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        font_path = os.path.join(os.path.dirname(__file__), "NotoSansTC-Regular.ttf")
        self.add_font("TW", "", font_path, uni=True)
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("TW", size=14)
        self.cell(0, 10, "SEO 合約報告", ln=True, align="C")
        self.ln(5)

    def chapter_title(self, title):
        self.set_font("TW", size=12)
        self.set_text_color(0)
        self.cell(0, 10, title, ln=True)

    def chapter_body(self, text):
        self.set_font("TW", size=11)
        self.set_text_color(50)
        self.multi_cell(0, 8, text)
        self.ln()

    def add_billing_report(self, client_name, bill_start, bill_end, total_downdays, adjusted_billing_date, charge_ranges, nocharge_ranges):
        self.add_page()
        self.chapter_title(f"客戶名稱：{client_name}")

        body = ""
        body += f"1. 原請款週期：{bill_start.strftime('%Y-%m-%d')} → {bill_end.strftime('%Y-%m-%d')}\n\n"
        body += f"2. 總共掉排名的天數：{total_downdays} 天\n\n"

        if nocharge_ranges:
            body += "3. 暫停收費區間：\n"
            for s, e in nocharge_ranges:
                days = (e - s).days
                body += f"   - {s.strftime('%Y-%m-%d')} ~ {e.strftime('%Y-%m-%d')}（{days} 天）\n"
            body += "\n"

        if charge_ranges:
            body += "4. 有收費區間：\n"
            for s, e in charge_ranges:
                days = (e - s).days
                body += f"   - {s.strftime('%Y-%m-%d')} ~ {e.strftime('%Y-%m-%d')}（{days} 天）\n"
            body += "\n"

        body += f"5. 因此，順延後的新請款日：{adjusted_billing_date.strftime('%Y-%m-%d')}"

        self.chapter_body(body)

st.title("SEO 延後請款計算工具")

with st.form("form"):
    client_name = st.text_input("客戶名稱", "慶昌珠寶")
    bill_start = st.date_input("原請款開始日", datetime(2025, 2, 13))
    bill_end = st.date_input("原請款結束日", datetime(2025, 5, 14))
    st.write("請輸入掉排名日期區間（可輸入多筆）：")
    drop_ranges = []
    for i in range(3):
        col1, col2 = st.columns(2)
        with col1:
            start = st.date_input(f"掉排名開始日 {i+1}", key=f"start{i}")
        with col2:
            end = st.date_input(f"掉排名結束日 {i+1}", key=f"end{i}")
        if start and end and start < end:
            drop_ranges.append((start, end))
    submitted = st.form_submit_button("產生報告")

if submitted:
    charge_ranges, nocharge_ranges, total_downdays = calculate_effective_days(bill_start, bill_end, drop_ranges)
    adjusted_date = bill_end + timedelta(days=total_downdays)

    pdf = PDFReport()
    pdf.add_billing_report(
        client_name,
        bill_start,
        bill_end,
        total_downdays,
        adjusted_date,
        charge_ranges,
        nocharge_ranges,
    )

    filename = f"{client_name}_請款報告_{adjusted_date.strftime('%Y-%m-%d')}.pdf"
    pdf.output(filename)
    with open(filename, "rb") as f:
        st.download_button("下載 PDF 報告", f, file_name=filename, mime="application/pdf")
    st.success("PDF 報告已產出！")
