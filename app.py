import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Raqam", page_icon="⚫", layout="wide")

# ---------- ثيم أسود وذهبي ----------
st.markdown("""
<style>
    .stApp {
        background-color: #0E0E0E;
        color: #D4AF37;
    }
    .css-1d391kg, .css-1wrcrro {
        background-color: #0E0E0E;
    }
    h1, h2, h3, .metric-label, .stMarkdown, p {
        color: #D4AF37 !important;
    }
    .stMetric label {
        color: #D4AF37 !important;
    }
    .stMetric .css-1xarl3l {
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("رقم | Raqam")
st.caption("ارفع شيت مبيعاتك .. افهم أرقامك في دقيقة")

uploaded_file = st.file_uploader("", type=["csv", "xlsx"])

if uploaded_file:
    # قراءة الملف
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("الملف اترفع، بنحلل...")

    # ---- التنضيف التلقائي: هنحاول نخمّن الأعمدة ----
    # عادةً نحتاج: عمود تاريخ، عمود منتج، عمود كمية، عمود سعر بيع، عمود مرتجع؟
    # ناس كتير بيسموهم عربي. MVP هنحاول نلاقي أي تشابه
    cols = df.columns.tolist()
    date_col = next((c for c in cols if 'تاريخ' in c or 'date' in c.lower()), None)
    prod_col = next((c for c in cols if 'منتج' in c or 'صنف' in c or 'product' in c.lower()), cols[0])
    qty_col  = next((c for c in cols if 'كمية' in c or 'quantity' in c.lower()), None)
    price_col= next((c for c in cols if 'سعر' in c or 'price' in c.lower()), None)
    return_col = next((c for c in cols if 'مرتجع' in c or 'return' in c.lower()), None)

    # لو مش موجودين، استخدم افتراض أول عمودين رقميين
    if qty_col is None:
        nums = df.select_dtypes(include='number').columns
        qty_col = nums[0] if len(nums) > 0 else None
    if price_col is None:
        nums = df.select_dtypes(include='number').columns
        price_col = nums[1] if len(nums) > 1 else None

    if qty_col and price_col:
        df['الإيراد'] = df[qty_col] * df[price_col]
    else:
        st.warning("مش لاقي أعمدة كمية وسعر. حاول تسميهم 'كمية' و 'سعر'.")

    # ---- الأرقام الذهبية ----
    total_sales = df['الإيراد'].sum() if 'الإيراد' in df.columns else 0
    total_returns = df[df[return_col] == 1]['الإيراد'].sum() if return_col and 'الإيراد' in df.columns else 0
    return_rate = (total_returns / total_sales * 100) if total_sales else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 إجمالي المبيعات", f"{total_sales:,.0f} ج.م")
    col2.metric("📉 المرتجعات", f"{total_returns:,.0f} ج.م")
    col3.metric("٪ نسبة المرتجع", f"{return_rate:.1f}%")

    # ---- توب 5 منتجات بالأعمدة ----
    if prod_col and 'الإيراد' in df.columns:
        top5 = df.groupby(prod_col)['الإيراد'].sum().nlargest(5).reset_index()
        fig = px.bar(top5, x=prod_col, y='الإيراد', color_discrete_sequence=['#D4AF37'])
        fig.update_layout(
            plot_bgcolor='#0E0E0E',
            paper_bgcolor='#0E0E0E',
            font_color='#D4AF37',
            title_text="أعلى 5 منتجات إيرادًا",
            xaxis_title="المنتج",
            yaxis_title="الإيراد (ج.م)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("مش قادر أحدد المنتج، لكن الأرقام طلعت.")

    # ---- توصية فورية ----
    if return_rate > 15:
        st.error("🚨 المرتجعات عالية جدًا (>15%). راجع سياسة الاستبدال أو جودة الوصف.")
    elif return_rate > 5:
        st.warning("⚡ المرتجعات متوسطة، فيه تحسين ممكن.")
    else:
        st.success("✅ نسبة المرتجعات تحت السيطرة.")

    st.caption("تحليل أولي من Raqam — للحصول على تقرير استراتيجي مفصل، ابعت الملف على الواتساب وسعر الخدمة 1500 ج.م")
else:
    st.image("https://via.placeholder.com/400x200/0E0E0E/D4AF37?text=Raqam+Logo", use_column_width=True)
