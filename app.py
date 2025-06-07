import streamlit as st
from datetime import datetime, timedelta
from fpdf import FPDF
import os

st.set_page_config(page_title="SEO 合約工具", layout="centered", initial_sidebar_state="collapsed")

def format_date_zh(date_obj):
    return f"{date_obj.year}年{date_obj.month}月{date_obj.day}日"

def format_range_zh(start, end):
    delta_days = (end - start).days
    return f"{format_date_zh(start)} ～ {format_date_zh(end)}（{delta_days} 天）"

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

    def add_billing_report(self, client_name, bill_start, billing_cycle_months, next_billing_date, total_downdays, adjusted_billing_date, charge_ranges, nocharge_ranges):
        self.add_page()
        self.chapter_title(f"📄 客戶名稱：{client_name}")

        body = ""
        body += f"1. 原請款週期：{bill_start} → {next_billing_date}\n\n"
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

        body += f"5. 因此，順延後的新請款日：{adjusted_billing_date}"

        self.chapter_body(body)

# ⚙️ 示範資料（可替換為表單輸入）
if __name__ == '__main__':
    client_name = "慶昌珠寶"
    bill_start = "2025-02-13"
    billing_cycle_months = 3
    next_billing_date = "2025-05-14"
    total_downdays = 46
    adjusted_billing_date = "2025-06-29"

    charge_ranges = [
        (datetime(2025, 2, 13), datetime(2025, 2, 18)),
        (datetime(2025, 4, 5), datetime(2025, 5, 14)),
    ]

    nocharge_ranges = [
        (datetime(2025, 2, 18), datetime(2025, 4, 5)),
    ]

    pdf = PDFReport()
    pdf.add_billing_report(
        client_name,
        bill_start,
        billing_cycle_months,
        next_billing_date,
        total_downdays,
        adjusted_billing_date,
        charge_ranges,
        nocharge_ranges,
    )

    filename = f"{client_name}_請款報告_{adjusted_billing_date}.pdf"
    pdf.output(filename)
    st.success(f"已產生報告：{filename}")
