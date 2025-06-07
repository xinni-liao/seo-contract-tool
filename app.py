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
        super().__init__()
        font_path = os.path.join(os.path.dirname(__file__), "NotoSansTC-Regular.ttf")
        self.add_font("TW", "", font_path, uni=True)

    def header(self):
        self.set_font("TW", size=14)
        self.cell(0, 10, "SEO 合約計算報告", 0, 1, "C")

    def chapter_title(self, title):
        self.set_font("TW", size=12)
        self.cell(0, 10, title, 0, 1)

    def chapter_body(self, text):
        self.set_font("TW", size=12)
        self.multi_cell(0, 10, text)

    def add_report(self, client_name, contract_start, original_expiry, total_downdays, adjusted_expiry, charge_ranges, nocharge_ranges):
        self.add_page()
        self.chapter_title("合約延展報告")
        body = (
            f"客戶名稱：{client_name}\n"
            f"原合約起始日：{format_date_zh(contract_start)}\n"
            f"原合約到期日：{format_date_zh(original_expiry)}\n"
            f"掉排名總天數：{total_downdays} 天\n"
        )

        if nocharge_ranges:
            body += f"\n🚫 暫停計費區間：\n"
            for s, e in nocharge_ranges:
                days = (e - s).days
                body += f"- {s.date()} ~ {e.date()}（{days} 天）\n"

        if charge_ranges:
            body += f"\n✅ 有計費區間：\n"
            for s, e in charge_ranges:
                days = (e - s).days
                body += f"- {s.date()} ~ {e.date()}（{days} 天）\n"

        body += f"\n延後後的新合約到期日：{format_date_zh(adjusted_expiry)}"

        self.chapter_body(body)

    def add_billing_report(self, client_name, bill_start, billing_cycle_months, next_billing_date, total_downdays, adjusted_billing_date, charge_ranges, nocharge_ranges):
        self.add_page()
        self.chapter_title("請款延期報告")

        body = f"客戶名稱：{client_name}\n\n"
        body += f"📅 原請款週期：{bill_start} → {next_billing_date}\n\n"
        body += f"🔴 總共掉排名的天數：{total_downdays} 天\n\n"

        if nocharge_ranges:
            body += f"🚫 暫停收費區間：\n\n"
            for s, e in nocharge_ranges:
                days = (e - s).days
                body += f"{s.date()} ~ {e.date()}（{days} 天）\n"
            body += "\n"

        if charge_ranges:
            body += f"✅ 有收費區間：\n\n"
            for s, e in charge_ranges:
                days = (e - s).days
                body += f"{s.date()} ~ {e.date()}（{days} 天）\n"
            body += "\n"

        body += f"🟡 因此，順延後的新請款日：{adjusted_billing_date}\n"

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

def main():
    st.title("📈 SEO排名請款計算工具")

    st.write("解放SEO合約計算的工具，邁向開心人生的小確幸！")

    option = st.radio("請選擇您要使用的計算功能：", ["💰 請款順延計算", "📅 合約延展計算"])

    if option == "💰 請款順延計算":
        client_name = st.text_input("👤 客戶名稱")
        billing_start = st.date_input("💰 請款起始日（即首次繳費日）")
        billing_cycle = st.selectbox("📦 繳費週期：", [1, 3], format_func=lambda x: f"每 {x} 個月繳一次")

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

        if st.button("💰 計算請款日順延"):
            if billing_start and periods:
                billing_start_dt = datetime.combine(billing_start, datetime.min.time())
                next_billing_date = billing_start_dt + timedelta(days=30 * billing_cycle)

                delay_days, charge_ranges, nocharge_ranges = calculate_overlap_days_and_ranges(periods, billing_start_dt, next_billing_date)
                adjusted_billing_date = next_billing_date + timedelta(days=delay_days)

                st.success("✅ 計算結果如下：")

                if charge_ranges:
                    st.write("✅ 有收費區間：")
                    for s, e in charge_ranges:
                        st.write(f"- {s.date()} ~ {e.date()}（{(e - s).days} 天）")
                if nocharge_ranges:
                    st.write("🚫 暫停收費區間：")
                    for s, e in nocharge_ranges:
                        st.write(f"- {s.date()} ~ {e.date()}（{(e - s).days} 天）")

                st.write(f"📅 原請款週期：{billing_start_dt.date()} → {next_billing_date.date()}")
                st.write(f"🔴 掉排名總共天數（在收費期間內）：{delay_days} 天")
                st.write(f"🟡 順延後的新請款日：{adjusted_billing_date.date()}")

                pdf = PDFReport()
                pdf.add_billing_report(client_name, billing_start_dt.date(), billing_cycle, next_billing_date.date(), delay_days, adjusted_billing_date.date(), charge_ranges, nocharge_ranges)

                month_label = f"{adjusted_billing_date.year}{adjusted_billing_date.month:02d}"
                safe_client = client_name.replace(" ", "_").replace("/", "_")
                filename = f"{safe_client}_請款報告_{month_label}.pdf"

                pdf.output(filename)
                with open(filename, "rb") as f:
                    st.download_button("⬇️ 下載 PDF 報告", f, file_name=filename)
                os.remove(filename)

    if option == "📅 合約延展計算":
        client_name = st.text_input("👤 客戶名稱", key="contract_client")
        contract_start = st.date_input("📅 合約起始日", key="contract_start")

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
                contract_start_dt = datetime.combine(contract_start, datetime.min.time())
                original_expiry = contract_start_dt + timedelta(days=365)
                total_downdays, charge_ranges, nocharge_ranges = calculate_overlap_days_and_ranges(periods, contract_start_dt, original_expiry)
                adjusted_expiry = original_expiry + timedelta(days=total_downdays)

                st.success("✅ 計算結果如下：")
                st.write(f"🟢 原合約起始日：{contract_start_dt.date()}")
                st.write(f"📆 原合約到期日：{original_expiry.date()}")
                st.write(f"🔴 掉排名總天數：{total_downdays} 天")

                if nocharge_ranges:
                    st.write("🚫 暫停計費區間：")
                    for s, e in nocharge_ranges:
                        st.write(f"- {s.date()} ~ {e.date()}（{(e - s).days} 天）")
                if charge_ranges:
                    st.write("✅ 有計費區間：")
                    for s, e in charge_ranges:
                        st.write(f"- {s.date()} ~ {e.date()}（{(e - s).days} 天）")

                st.write(f"🟡 延後後的新合約到期日：{adjusted_expiry.date()}")

                pdf = PDFReport()
                pdf.add_report(client_name, contract_start_dt.date(), original_expiry.date(), total_downdays, adjusted_expiry.date(), charge_ranges, nocharge_ranges)

                month_label = f"{adjusted_expiry.year}{adjusted_expiry.month:02d}"
                safe_client = client_name.replace(" ", "_").replace("/", "_")
                filename = f"{safe_client}_合約延展報告_{month_label}.pdf"

                pdf.output(filename)
                with open(filename, "rb") as f:
                    st.download_button("⬇️ 下載 PDF 報告", f, file_name=filename)
                os.remove(filename)

if __name__ == "__main__":
    main()
