import streamlit as st
import yfinance as yf
import pandas as pd
import pymannkendall as mk
import matplotlib.pyplot as plt

# =============================
# CẤU HÌNH TRANG
# =============================
st.set_page_config(
    page_title="Kiểm định Mann-Kendall",
    page_icon="📈",
    layout="centered"
)

st.title("📈 KIỂM ĐỊNH XU HƯỚNG GIÁ CỔ PHIẾU BẰNG MANN-KENDALL")

st.write(
    """
Ứng dụng sử dụng kiểm định **Mann-Kendall** để xác định
giá cổ phiếu có xu hướng tăng, giảm hay không có xu hướng.
"""
)

# =============================
# NHẬP THÔNG TIN
# =============================

ticker = st.text_input(
    "Nhập mã cổ phiếu:",
    value="VCB.VN"
)

start_date = st.date_input(
    "Ngày bắt đầu",
    value=pd.to_datetime("2024-01-01")
)

end_date = st.date_input(
    "Ngày kết thúc",
    value=pd.to_datetime("2026-06-27")
)

# =============================
# NÚT THỰC HIỆN
# =============================

if st.button("Thực hiện kiểm định"):

    try:

        with st.spinner("Đang tải dữ liệu..."):

            df = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False
            )

        if df.empty:
            st.error("Không tìm thấy dữ liệu.")
            st.stop()

        # Nếu cột dạng MultiIndex thì bỏ level ticker
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel("Ticker")

        close_price = df["Close"]

        # =============================
        # VẼ BIỂU ĐỒ
        # =============================

        fig, ax = plt.subplots(figsize=(10,5))

        ax.plot(
            close_price,
            color="blue",
            linewidth=2
        )

        ax.set_title(f"Giá cổ phiếu {ticker}")
        ax.set_xlabel("Ngày")
        ax.set_ylabel("Giá")
        ax.grid(True)

        st.pyplot(fig)

        # =============================
        # KIỂM ĐỊNH
        # =============================

        result = mk.original_test(close_price)

        st.subheader("Kết quả kiểm định")

        st.write(f"**Trend:** {result.trend}")
        st.write(f"**p-value:** {result.p:.6f}")
        st.write(f"**Tau:** {result.Tau:.4f}")
        st.write(f"**S:** {result.s}")
        st.write(f"**Variance of S:** {result.var_s:.2f}")
        st.write(f"**Z:** {result.z:.4f}")

        # =============================
        # DIỄN GIẢI
        # =============================

        st.subheader("Diễn giải")

        if result.p < 0.05:

            if result.trend == "increasing":
                st.success(
                    "Có xu hướng tăng có ý nghĩa thống kê (p < 0.05)."
                )

            elif result.trend == "decreasing":
                st.success(
"Có xu hướng giảm có ý nghĩa thống kê (p < 0.05)."
                )

            else:
                st.success(
                    "Có xu hướng đáng kể về mặt thống kê."
                )

        else:
            st.warning(
                "Không phát hiện xu hướng có ý nghĩa thống kê (p ≥ 0.05)."
            )

        # =============================
        # HIỂN THỊ DỮ LIỆU
        # =============================

        st.subheader("Dữ liệu")

        st.dataframe(df)

    except Exception as e:
        st.error(e)
