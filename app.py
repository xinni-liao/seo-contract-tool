import streamlit as st
from datetime import datetime, timedelta
from fpdf import FPDF
import os

st.set_page_config(page_title="SEO 合約工具", layout="centered", initial_sidebar_state="collapsed")

class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "SEO 合約計算報告", 0, 1, "C")

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, 0, 1)

    def chapter_body(self, text):
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, text)

    def add_report(self, contract_start, original_expiry, total_downdays, adjusted_expiry):
        self.add_page()
        self.chapter_title("計算結果")
        body = (
            f"原合約起始日：{contract_start}\n"
            f"原合約到期日：{original_expiry}\n"
            f"掉排名總天數：{total_downdays} 天\n"
            f"延後後的新合約到期日：{adjusted_expiry}"
        )
        self.chapter_body(body)

def calculate_downtime_days(periods):
    total_days = 0
    for start, end in periods:
        total_days += (end - start).days + 1
    return total_days

def main():
    st.title("📈 SEO 合約掉排名計算工具")

    st.markdown("""
    <style>
    @media (max-width: 768px) {
        .element-container { padding: 10px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

    st.write("這是一個行動裝置友善的工具，可協助您計算掉出第一頁的天數，並自動調整合約到期日，也可匯出 PDF 報告。")

    contract_start = st.date_input("📅 合約起始日")

    st.subheader("⬇️ 掉出第一頁的日期區間")
    periods = []
    num_periods = st.number_input("輸入掉排名的區間數量：", min_value=1, step=1)

    for i in range(int(num_periods)):
        with st.container():
            st.markdown(f"**第 {i+1} 段區間**")
            start_date = st.date_input(f"開始日期", key=f"start_{i}")
            end_date = st.date_input(f"結束日期", key=f"end_{i}")
            if end_date >= start_date:
                periods.append((datetime.combine(start_date, datetime.min.time()),
                                datetime.combine(end_date, datetime.min.time())))
            else:
                st.error(f"⚠️ 第 {i+1} 段結束日不能早於開始日")

    if st.button("📅 計算合約到期日"):
        if contract_start and periods:
            total_downdays = calculate_downtime_days(periods)
            contract_start_dt = datetime.combine(contract_start, datetime.min.time())
            original_expiry = contract_start_dt + timedelta(days=365)
            adjusted_expiry = original_expiry + timedelta(days=total_downdays)

            st.success("✅ 計算結果如下：")
            st.write(f"🟢 原合約起始日：{contract_start_dt.date()}")
            st.write(f"📆 原合約到期日：{original_expiry.date()}")
            st.write(f"🔴 掉排名總天數：{total_downdays} 天")
            st.write(f"🟡 延後後的新合約到期日：{adjusted_expiry.date()}")

            if st.button("📤 匯出 PDF 報告"):
                pdf = PDFReport()
                pdf.add_report(contract_start_dt.date(), original_expiry.date(), total_downdays, adjusted_expiry.date())
                output_path = "seo_contract_report.pdf"
                pdf.output(output_path)
                with open(output_path, "rb") as f:
                    st.download_button("⬇️ 下載 PDF 報告", f, file_name=output_path)
                os.remove(output_path)

if __name__ == "__main__":
    main()
