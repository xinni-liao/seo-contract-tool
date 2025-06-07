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
    def header(self):
        font_path = os.path.join(os.path.dirname(__file__), "NotoSansTC-Regular.ttf")
        self.add_font("TW", "", font_path, uni=True)
        self.set_font("TW", size=14)
        self.cell(0, 10, "SEO 合約計算報告", 0, 1, "C")

    def chapter_title(self, title):
        self.set_font("TW", size=12)
        self.cell(0, 10, title, 0, 1)

    def chapter_body(self, text):
        self.set_font("TW", size=12)
        self.multi_cell(0, 10, text)

    def add_report(self, client_name, contract_start, original_expiry, total_downdays, adjusted_expiry):
        self.add_page()
        self.chapter_title("合約延展報告")
        body = (
            f"客戶名稱：{client_name}\n"
            f"原合約起始日：{format_date_zh(contract_start)}\n"
            f"原合約到期日：{format_date_zh(original_expiry)}\n"
            f"掉排名總天數：{total_downdays} 天\n"
            f"延後後的新合約到期日：{format_date_zh(adjusted_expiry)}"
        )
        self.chapter_body(body)

    def add_billing_report(self, client_name, bill_start, billing_cycle_months, next_billing_date, total_downdays, adjusted_billing_date, charge_ranges, nocharge_ranges):
        self.add_page()
        self.chapter_title("請款延期報告")

        body = (
            f"客戶名稱：{client_name}\n\n"
            f"１、📅 原請款週期：{bill_start} → {next_billing_date}\n\n"
            f"２、🔴 總共掉排名的天數：{total_downdays} 天\n\n"
        )

        if nocharge_ranges:
            body += f"３、🚫 暫停收費區間：\n\n"
            for s, e in nocharge_ranges:
                body += f"{s.date()} ~ {e.date()}（{(e - s).days} 天）\n"
            body += "\n"

        if charge_ranges:
            body += f"４、✅ 有收費區間：\n\n"
            for s, e in charge_ranges:
                body += f"{s.date()} ~ {e.date()}（{(e - s).days} 天）\n"
            body += "\n"

        body += f"５、🟡 因此，順延後的新請款日：{adjusted_billing_date}\n"

        self.chapter_body(body)

# 其餘程式碼保持不變
