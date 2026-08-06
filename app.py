import streamlit as st
import pandas as pd

st.title("📊 销售数据分析工具")

# 上传Excel文件
uploaded_file = st.file_uploader("上传Excel文件", type="xlsx")

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    
    st.write("✅ 数据加载成功！")
    st.dataframe(df)
    
    # 计算总销售额
    total_sales = df["销售额"].sum()
    st.metric("总销售额", f"{total_sales:,.0f}")
    
    # 计算单价
    df["单价"] = df["销售额"] / df["数量"]
    st.write("💰 每个产品单价：")
    st.dataframe(df[["产品", "单价"]])
    
    # 最高销售产品
    top_product = df.loc[df["销售额"].idxmax()]
    st.success(f"🏆 销售额最高产品: {top_product['产品']} — {top_product['销售额']:,.0f}")