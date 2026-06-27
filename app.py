import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pymannkendall as mk
import matplotlib.pyplot as plt
import mplfinance as mpf

# =============================
# CẤU HÌNH TRANG
# =============================
st.set_page_config(
    page_title="Phân tích cổ phiếu bằng Mann-Kendall",
    page_icon="📈",
    layout="wide"
)

st.title("📈 PHÂN TÍCH GIÁ CỔ PHIẾU VÀ KIỂM ĐỊNH MANN-KENDALL")

# =============================
# SIDEBAR
# =============================

st.sidebar.header("Thông tin đầu vào")

ticker = st.sidebar.text_input(
    "Mã cổ phiếu",
    "VCB.VN"
)

start_date = st.sidebar.date_input(
    "Ngày bắt đầu",
    pd.to_datetime("2026-01-01")
)

end_date = st.sidebar.date_input(
    "Ngày kết thúc",
    pd.to_datetime("2026-06-27")
)

# =============================
# NÚT CHẠY
# =============================

if st.sidebar.button("Phân tích"):

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

    # =============================
    # XỬ LÝ DỮ LIỆU
    # =============================

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel("Ticker")

    full_date_range = pd.date_range(
        start=df.index.min(),
        end=df.index.max(),
        freq="D"
    )

    df = df.reindex(full_date_range)

    df = df.ffill()

    df["simple_ret"] = df["Close"].pct_change()

    df["log_ret"] = np.log(
        df["Close"] / df["Close"].shift(1)
    )

    # =============================
    # DỮ LIỆU
    # =============================

    st.subheader("Dữ liệu")

    st.dataframe(df)

    # =============================
    # GIÁ ĐÓNG CỬA + LOG RETURN
    # =============================

    st.subheader("Giá đóng cửa và Log Return")

    fig, ax = plt.subplots(
        2,
        1,
        figsize=(10,8),
        sharex=True
    )

    ax[0].plot(
        df.index,
        df["Close"],
        color="red",
        linewidth=2,
        label="Close Price"
    )

    ax[0].set_title("Giá đóng cửa")
    ax[0].set_ylabel("VND")
    ax[0].legend()
    ax[0].grid(True)

    ax[1].plot(
        df.index,
        df["log_ret"],
        color="green",
        linewidth=1.5,
        label="Log Return"
    )

    ax[1].set_title("Log Return")
    ax[1].set_ylabel("Return")
    ax[1].set_xlabel("Date")
    ax[1].legend()
    ax[1].grid(True)

    plt.tight_layout()

    st.pyplot(fig)

    # =============================
    # BIỂU ĐỒ NẾN
    # =============================

    st.subheader("Biểu đồ nến")

    fig2, axlist = mpf.plot(
        df,
        type="candle",
        mav=(10,20),
        volume=True,
        style="yahoo",
figsize=(12,6),
        title=f"{ticker}",
        returnfig=True
    )

    st.pyplot(fig2)

    # =============================
    # KIỂM ĐỊNH MANN-KENDALL
    # =============================

    close_prices = df["Close"].dropna().reset_index(drop=True)

    result = mk.original_test(close_prices)

    st.subheader("Kết quả kiểm định Mann-Kendall")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Trend",
            result.trend
        )

        st.metric(
            "Tau",
            round(result.Tau,4)
        )

    with col2:

        st.metric(
            "p-value",
            round(result.p,6)
        )

        st.metric(
            "Variance S",
            round(result.var_s,2)
        )

    st.markdown("---")

    if result.p < 0.05:

        if result.trend == "increasing":

            st.success(
                "Có xu hướng TĂNG có ý nghĩa thống kê (p < 0.05)."
            )

        elif result.trend == "decreasing":

            st.success(
                "Có xu hướng GIẢM có ý nghĩa thống kê (p < 0.05)."
            )

        else:

            st.success(
                "Có xu hướng đáng kể về mặt thống kê."
            )

    else:

        st.warning(
            "Không phát hiện xu hướng có ý nghĩa thống kê."
        )
