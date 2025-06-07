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
        self.add_font("TW", "", "NotoSansTC-Regular.ttf", uni=True)
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
        original_range = format_range_zh(bill_start, next_billing_date)
        adjusted_range = format_range_zh(bill_start, adjusted_billing_date)
        body = (
            f"客戶名稱：{client_name}\n"
            f"原請款週期：{original_range}\n"
            f"繳費週期：每 {billing_cycle_months} 個月一繳\n"
            f"掉排名天數：{total_downdays} 天\n"
            f"順延後的新收費區間：{adjusted_range}\n"
            f"新請款日：{format_date_zh(adjusted_billing_date)}\n"
        )
        if charge_ranges:
            body += f"\n✅ 有收費區間：\n" + "\n".join([format_range_zh(s, e) for s, e in charge_ranges])
        if nocharge_ranges:
            body += f"\n🚫 暫停收費區間：\n" + "\n".join([format_range_zh(s, e) for s, e in nocharge_ranges])

        self.chapter_body(body)

def calculate_overlap_days_and_ranges(periods, billing_range_start, billing_range_end):
    total = 0
    charge_ranges = []
    nocharge_ranges = []

    cursor = billing_range_start
    sorted_periods = sorted(periods, key=lambda x: x[0])

    for start, end in sorted_periods:
        overlap_start = max(start, billing_range_start)
        overlap_end = min(end, billing_range_end)

        if overlap_start < overlap_end:
            if cursor < overlap_start:
                charge_ranges.append((cursor, overlap_start))
            nocharge_ranges.append((overlap_start, overlap_end))
            total += (overlap_end - overlap_start).days
            cursor = overlap_end

    if cursor < billing_range_end:
        charge_ranges.append((cursor, billing_range_end))

    return total, charge_ranges, nocharge_ranges

# main() 函數及其他部分保持不變
