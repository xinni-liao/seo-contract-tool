import streamlit as st
from datetime import datetime, timedelta
from fpdf import FPDF
import os

st.set_page_config(page_title="SEO 合約工具", layout="centered", initial_sidebar_state="collapsed")

def format_date_zh(date_obj):
    return f"{date_obj.year}年{date_obj.month}月{date_obj.day}日"

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

    def add_billing_report(self, client_name, bill_start, billing_cycle_months, next_billing_date, total_downdays, adjusted_billing_date):
        self.add_page()
        self.chapter_title("請款延期報告")
        original_range = f"{format_date_zh(bill_start)} ～ {format_date_zh(next_billing_date)}"
        adjusted_range = f"{format_date_zh(bill_start)} ～ {format_date_zh(adjusted_billing_date)}"
        body = (
            f"客戶名稱：{client_name}\n"
            f"原請款週期：{original_range}\n"
            f"繳費週期：每 {billing_cycle_months} 個月一繳\n"
            f"掉排名天數：{total_downdays} 天\n"
            f"順延後的新收費區間：{adjusted_range}\n"
            f"新請款日：{format_date_zh(adjusted_billing_date)}"
        )
        self.chapter_body(body)

def calculate_downtime_days(periods):
    return sum((end - start).days + 1 for start, end in periods)

def main():
    st.title("📈 SEO 合約掉排名與請款日調整工具")

    st.markdown("""
    <style>
    @media (max-width: 768px) {
        .element-container { padding: 10px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

    st.write("這是一個行動裝置友善的工具，可計算合約到期日與順延請款日，並可匯出 PDF 報告。")

    option = st.radio("請選擇您要使用的計算功能：", ["📅 合約延展計算", "💰 請款順延計算"])

    if option == "📅 合約延展計算":
        client_name = st.text_input("👤 客戶名稱")
        contract_start = st.date_input("📅 合約起始日")

        st.subheader("⬇️ 掉出第一頁的日期區間")
        periods = []
        num_periods = st.number_input("輸入掉排名的區間數量：", min_value=1, step=1, key="contract")

        for i in range(int(num_periods)):
            with st.container():
                st.markdown(f"**第 {i+1} 段區間**")
                start_date = st.date_input(f"開始日期", key=f"start_c_{i}")
                end_date = st.date_input(f"結束日期", key=f"end_c_{i}")
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

                pdf = PDFReport()
                pdf.add_report(client_name, contract_start_dt.date(), original_expiry.date(), total_downdays, adjusted_expiry.date())
                output_path = "seo_contract_report.pdf"
                pdf.output(output_path)
                with open(output_path, "rb") as f:
                    st.download_button("⬇️ 下載 PDF 報告", f, file_name=output_path)
                os.remove(output_path)

    elif option == "💰 請款順延計算":
        client_name = st.text_input("👤 客戶名稱")
        billing_start = st.date_input("💰 請款起始日（即首次繳費日）")
        billing_cycle = st.selectbox("📦 繳費週期：", [1, 3], format_func=lambda x: f"每 {x} 個月繳一次")

        st.subheader("⬇️ 掉出第一頁的日期區間")
        periods = []
        num_periods = st.number_input("輸入掉排名的區間數量：", min_value=1, step=1, key="billing")

        for i in range(int(num_periods)):
            with st.container():
                st.markdown(f"**第 {i+1} 段區間**")
                start_date = st.date_input(f"開始日期", key=f"start_b_{i}")
                end_date = st.date_input(f"結束日期", key=f"end_b_{i}")
                if end_date >= start_date:
                    periods.append((datetime.combine(start_date, datetime.min.time()),
                                    datetime.combine(end_date, datetime.min.time())))
                else:
                    st.error(f"⚠️ 第 {i+1} 段結束日不能早於開始日")

        if st.button("💰 計算請款日順延"):
            if billing_start and periods:
                total_downdays = calculate_downtime_days(periods)
                billing_start_dt = datetime.combine(billing_start, datetime.min.time())
                next_billing_date = billing_start_dt + timedelta(days=30 * billing_cycle)
                adjusted_billing_date = next_billing_date + timedelta(days=total_downdays)

                st.success("✅ 計算結果如下：")
                st.write(f"📅 原請款週期：{billing_start_dt.date()} → {next_billing_date.date()}")
                st.write(f"🔴 掉排名天數：{total_downdays} 天")
                st.write(f"🟡 延後後的下一次請款日：{adjusted_billing_date.date()}")

                pdf = PDFReport()
                pdf.add_billing_report(client_name, billing_start_dt.date(), billing_cycle, next_billing_date.date(), total_downdays, adjusted_billing_date.date())
                output_path = "seo_billing_report.pdf"
                pdf.output(output_path)
                with open(output_path, "rb") as f:
                    st.download_button("⬇️ 下載 PDF 報告", f, file_name=output_path)
                os.remove(output_path)

if __name__ == "__main__":
    main()
