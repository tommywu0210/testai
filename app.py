import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="产品库存管理", layout="wide")
st.title("📦 产品库存管理系统")

# ============================================================
# 数据库配置
# ============================================================
DATABASE_FILE = "products.db"

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT    NOT NULL,
            price REAL    NOT NULL,
            stock INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def load_data():
    """读取所有产品"""
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query("SELECT * FROM products ORDER BY id DESC", conn)
    conn.close()
    return df

def add_product(name, price, stock):
    """添加新产品"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO products (name, price, stock)
        VALUES (?, ?, ?)
    """, (name, price, stock))
    
    conn.commit()
    conn.close()

def update_product(product_id, name, price, stock):
    """更新产品"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE products
        SET name = ?, price = ?, stock = ?
        WHERE id = ?
    """, (name, price, stock, product_id))
    
    conn.commit()
    conn.close()

def delete_product(product_id):
    """删除产品"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    
    conn.commit()
    conn.close()

# ============================================================
# 初始化
# ============================================================
init_database()

# ============================================================
# 创建标签页
# ============================================================
tab1, tab2, tab3 = st.tabs(["📋 查看库存", "➕ 添加产品", "✏️ 编辑产品"])

# ============================================================
# 标签页1：查看库存
# ============================================================
with tab1:
    st.subheader("📋 所有产品")
    
    df = load_data()
    
    if len(df) > 0:
        # 统计信息
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("产品总数", len(df))
        
        with col2:
            total_value = (df['price'] * df['stock']).sum()
            st.metric("总库存价值", f"¥{total_value:,.0f}")
        
        with col3:
            st.metric("平均单价", f"¥{df['price'].mean():,.0f}")
        
        st.write("---")
        
        # 显示表格
        st.dataframe(df, use_container_width=True)
        
        # 下载功能
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下载为CSV",
            data=csv,
            file_name=f"products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("📝 暂无产品，请先添加")

# ============================================================
# 标签页2：添加产品
# ============================================================
with tab2:
    st.subheader("➕ 添加新产品")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        name = st.text_input("产品名称", placeholder="例如：Dupixent")
    
    with col2:
        price = st.number_input("价格", min_value=0.0, step=1000.0)
    
    with col3:
        stock = st.number_input("库存数量", min_value=0, step=1)
    
    if st.button("💾 添加产品", use_container_width=True):
        if name and price > 0 and stock > 0:
            add_product(name, price, stock)
            st.success("✅ 产品已添加！")
            st.rerun()
        else:
            st.error("❌ 请填写所有字段且数值必须大于0")

# ============================================================
# 标签页3：编辑产品
# ============================================================
with tab3:
    st.subheader("✏️ 编辑产品")
    
    df = load_data()
    
    if len(df) > 0:
        # 选择产品
        product_id = st.selectbox(
            "选择要编辑的产品",
            options=df['id'].tolist(),
            format_func=lambda x: f"ID {x}: {df[df['id']==x]['name'].values[0]}"
        )
        
        # 获取当前数据
        current = df[df['id'] == product_id].iloc[0]
        
        st.write("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_name = st.text_input("产品名称", value=current['name'])
        
        with col2:
            new_price = st.number_input("价格", value=float(current['price']), min_value=0.0, step=1000.0)
        
        with col3:
            new_stock = st.number_input("库存数量", value=int(current['stock']), min_value=0, step=1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ 保存修改", use_container_width=True):
                update_product(product_id, new_name, new_price, new_stock)
                st.success("✅ 产品已更新！")
                st.rerun()
        
        with col2:
            if st.button("🗑️ 删除产品", use_container_width=True):
                delete_product(product_id)
                st.success("✅ 产品已删除！")
                st.rerun()
    else:
        st.info("📝 暂无产品")
