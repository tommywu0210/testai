import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(page_title="Product Inventory Manager", layout="wide")

# ============================================================
# 数据库文件
# ============================================================
DATABASE_FILE = "products.db"
USERS_DB = "authorized_users.db"

# ============================================================
# 第1步：初始化授权用户数据库
# ============================================================
def init_users_database():
    """创建授权用户表"""
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS authorized_users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            email      TEXT UNIQUE NOT NULL,
            name       TEXT NOT NULL,
            role       TEXT DEFAULT 'viewer',
            department TEXT,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active     INTEGER DEFAULT 1
        )
    """)
    
    conn.commit()
    conn.close()

# ============================================================
# 第2步：添加授权用户（您在维护这个列表）
# ============================================================
def add_authorized_user(email, name, role, department):
    """添加一个授权用户"""
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO authorized_users (email, name, role, department)
            VALUES (?, ?, ?, ?)
        """, (email, name, role, department))
        conn.commit()
        conn.close()
        return True, "✅ User added successfully"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "❌ This email already exists"

# ============================================================
# 第3步：验证邮箱是否有权限
# ============================================================
def verify_user_access(email):
    """检查邮箱是否在授权列表中"""
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM authorized_users 
        WHERE email = ? AND active = 1
    """, (email,))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return True, {
            "id": user[0],
            "email": user[1],
            "name": user[2],
            "role": user[3],
            "department": user[4]
        }
    return False, None

# ============================================================
# 第4步：加载所有授权用户（管理员查看）
# ============================================================
def load_all_users():
    conn = sqlite3.connect(USERS_DB)
    df = pd.read_sql_query("SELECT * FROM authorized_users ORDER BY id DESC", conn)
    conn.close()
    return df

# ============================================================
# 第5步：停用/激活用户
# ============================================================
def toggle_user_status(user_id, active):
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE authorized_users SET active = ? WHERE id = ?", (active, user_id))
    conn.commit()
    conn.close()

# ============================================================
# 第6步：删除用户
# ============================================================
def delete_user(user_id):
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM authorized_users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# ============================================================
# 初始化Session State
# ============================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None

# ============================================================
# 登录页面
# ============================================================
def login_page():
    st.title("🔐 Sanofi Internal Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.write("---")
        st.write("### Product Inventory Management System")
        st.write("Please enter your Sanofi email to continue")
        st.write("---")
        
        email = st.text_input(
            "Sanofi Email",
            placeholder="yourname@sanofi.com",
            key="login_email"
        )
        
        if st.button("🔓 Login", use_container_width=True):
            if email:
                if not email.endswith("@sanofi.com"):
                    st.error("❌ Please use your Sanofi email (@sanofi.com)")
                else:
                    is_authorized, user_info = verify_user_access(email)
                    
                    if is_authorized:
                        st.session_state.logged_in = True
                        st.session_state.user_info = user_info
                        st.success(f"✅ Welcome, {user_info['name']}!")
                        st.rerun()
                    else:
                        st.error("❌ You are not authorized to access this system. Please contact the administrator.")
            else:
                st.warning("⚠️ Please enter your email")

# ============================================================
# 管理员：用户管理界面
# ============================================================
def admin_user_management():
    st.subheader("👥 Manage Authorized Users")
    
    tab1, tab2 = st.tabs(["📋 View Users", "➕ Add User"])
    
    with tab1:
        df = load_all_users()
        
        if len(df) > 0:
            st.dataframe(df, use_container_width=True)
            
            st.write("---")
            st.write("**Manage User Status**")
            
            user_id = st.selectbox(
                "Select user to manage",
                options=df['id'].tolist(),
                format_func=lambda x: f"{df[df['id']==x]['name'].values[0]} ({df[df['id']==x]['email'].values[0]})"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Activate", use_container_width=True):
                    toggle_user_status(user_id, 1)
                    st.success("User activated")
                    st.rerun()
            with col2:
                if st.button("🚫 Deactivate", use_container_width=True):
                    toggle_user_status(user_id, 0)
                    st.success("User deactivated")
                    st.rerun()
        else:
            st.info("No users yet")
    
    with tab2:
        st.write("**Add a new authorized user**")
        
        col1, col2 = st.columns(2)
        with col1:
            new_email = st.text_input("Email", placeholder="employee@sanofi.com")
            new_name = st.text_input("Name", placeholder="John Doe")
        with col2:
            new_role = st.selectbox("Role", ["admin", "editor", "viewer"])
            new_department = st.text_input("Department", placeholder="Customer Service")
        
        if st.button("💾 Add User", use_container_width=True):
            if new_email and new_name:
                if not new_email.endswith("@sanofi.com"):
                    st.error("❌ Please use a Sanofi email")
                else:
                    success, message = add_authorized_user(new_email, new_name, new_role, new_department)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.warning("⚠️ Please fill in email and name")

# ============================================================
# 主应用
# ============================================================
def main_app():
    user = st.session_state.user_info
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title("📦 Product Inventory Management System")
    with col3:
        st.write(f"👤 **{user['name']}** ({user['role']})")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.rerun()
    
    st.write("---")
    
    # 根据角色显示不同标签页
    if user['role'] == 'admin':
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Inventory", "➕ Add Product", "✏️ Edit Product", "👥 Manage Users"])
    else:
        tab1, tab2, tab3 = st.tabs(["📋 Inventory", "➕ Add Product", "✏️ Edit Product"])
    
    # ... (库存管理功能，同之前的代码)
    
    with tab1:
        st.subheader("📋 All Products")
        st.info("Inventory data goes here...")
    
    with tab2:
        if user['role'] in ['admin', 'editor']:
            st.subheader("➕ Add New Product")
            st.info("Add product form goes here...")
        else:
            st.warning("⚠️ You don't have permission to add products.")
    
    with tab3:
        if user['role'] == 'admin':
            st.subheader("✏️ Edit Product")
            st.info("Edit product form goes here...")
        else:
            st.warning("⚠️ Only admins can edit products.")
    
    if user['role'] == 'admin':
        with tab4:
            admin_user_management()

# ============================================================
# 主程序
# ============================================================
init_users_database()

# 如果是第一次运行，添加您自己为admin
conn = sqlite3.connect(USERS_DB)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM authorized_users")
count = cursor.fetchone()[0]
conn.close()

if count == 0:
    add_authorized_user("tommy.wu@sanofi.com", "Tommy Wu", "admin", "Customer Service")

if st.session_state.logged_in:
    main_app()
else:
    login_page()