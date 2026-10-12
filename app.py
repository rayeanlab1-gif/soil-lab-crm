import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="نظام تتبع مختبر التربة المطور", layout="wide", page_icon="🔬")

DATA_FILE = "soil_lab_crm.csv"
SALES_TEAM = ["علي مدحت", "محمد حمامة", "محمد الجندي", "محمد عادل", "غير محدد"]

def load_data():
    cols = ["الاسم", "النوع", "المنطقة", "الحي", "حالة العميل", "آخر تحديث", 
            "تاريخ الزيارة الأخيرة", "موعد المتابعة القادمة", "سبب عدم التعاقد", 
            "اسم المندوب", "نوع الخدمة", "قيمة العرض", "تاريخ أول زيارة", "أيام الإغلاق",
            "المهندس المسؤول", "رقم الجوال", "البريد الإلكتروني"]
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            for c in cols:
                if c not in df.columns:
                    df[c] = "0" if c in ["قيمة العرض", "أيام الإغلاق"] else "غير مسجل"
            return df.astype(str).replace("nan", "")
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

df_crm = load_data()

st.title("🔬 نظام CRM مختبر التربة والمواد - لوحة تحليل الأداء")
st.markdown("---")

st.header("📊 مؤشرات أداء المبيعات والصفقات المالية")
if not df_crm.empty and len(df_crm) > 0:
    total_clients = len(df_crm)
    won_df = df_crm[df_crm["حالة العميل"].str.contains("شريك|معتمد", na=False, case=False)]
    won_deals = len(won_df)
    total_prospects = total_clients - won_deals
    
    total_revenue = pd.to_numeric(won_df["قيمة العرض"], errors='coerce').fillna(0).sum()
    avg_closing_time = pd.to_numeric(won_df["أيام الإغلاق"], errors='coerce').fillna(0).mean() if won_deals > 0 else 0
    conversion_rate = (won_deals / total_clients * 100) if total_clients > 0 else 0
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🎯 إجمالي الداتا", f"{total_clients} جهة")
    k2.metric("👥 داتا العملاء المحتملين", f"{total_prospects} عميل")
    k3.metric("💰 إجمالي قيمة العقود", f"{total_revenue:,.0f} ريال")
    k4.metric("⏳ متوسط وقت إغلاق الصفقة", f"{avg_closing_time:.1f} يوم")
    
    st.markdown("#### 🔍 الرسوم البيانية")
    c_chart1, c_chart2 = st.columns(2)
    with c_chart1:
        st.write("📌 حجم الزيارات والمشاريع لكل مندوب:")
        st.bar_chart(df_crm["اسم المندوب"].value_counts())
    with c_chart2:
        st.write("⚠️ أسباب تعطل أو خسارة الصفقات:")
        lost_df = df_crm[(df_crm["سبب عدم التعاقد"] != "لا يوجد / قيد المتابعة") & (df_crm["سبب عدم التعاقد"] != "")]
        if not lost_df.empty:
            st.bar_chart(lost_df["سبب عدم التعاقد"].value_counts())
        else:
            st.info("لا توجد صفقات خاسرة مسجلة.")
else:
    st.info("في انتظار تسجيل أول معاملة لعرض الرسوم البيانية.")

st.markdown("---")

st.header("🔍 محرك البحث والتعديل الفوري")
if not df_crm.empty and len(df_crm) > 0:
    search_query = st.selectbox("اختر اسم المكتب أو الشركة للتعديل:", [""] + list(df_crm["الاسم"].unique()))
    if search_query:
        filtered_rows = df_crm[df_crm["الاسم"] == search_query]
        idx_list = filtered_rows.index.tolist()
        
        r_name = str(filtered_rows["الاسم"].values[0])
        r_status = str(filtered_rows["حالة العميل"].values[0]).strip()
        r_agent = str(filtered_rows["اسم المندوب"].values[0]).strip()
        r_service = str(filtered_rows["نوع الخدمة"].values[0]).strip()
        r_reason = str(filtered_rows["سبب عدم التعاقد"].values[0]).strip()
        r_notes = str(filtered_rows["آخر تحديث"].values[0])
        r_contact = str(filtered_rows["المهندس المسؤول"].values[0])
        r_phone = str(filtered_rows["رقم الجوال"].values[0])
        r_email = str(filtered_rows["البريد الإلكتروني"].values[0])
        r_first_date = str(filtered_rows["تاريخ أول زيارة"].values[0])
        
        try: r_price = float(filtered_rows["قيمة العرض"].values[0])
        except: r_price = 0.0
        try: r_next_visit = datetime.strptime(str(filtered_rows["موعد المتابعة القادمة"].values[0]).strip(), "%Y-%m-%d")
        except: r_next_visit = datetime.now()
        
        with st.form("edit_form"):
            st.markdown("#### ⚙️ تحديث بيانات التواصل والصفقة")
            col_e1, col_e2, col_e3 = st.columns(3)
            with col_e1:
                opts = ["مستهدف (لم يزر)", "تمت الزيارة الأولى", "مفاوضات وعروض أسعار", "شريك معتمد (إحالات مستمرة)"]
                e_status = st.selectbox("الحالة البيعية الحالية", opts, index=opts.index(r_status) if r_status in opts else 0)
                e_agent = st.selectbox("المندوب المسؤول", SALES_TEAM, index=SALES_TEAM.index(r_agent) if r_agent in SALES_TEAM else 4)
                e_contact_name = st.text_input("اسم المهندس المسؤول بالجهة", value=r_contact)
            with col_e2:
                srvs = ["لم تحدد بعد", "فحص تربة وجسات (رخص بلدي)", "اختبارات دمك وترصيص ميداني", "كسر مكعبات خرسانة", "اختبارات أسفلت ومواد"]
                e_service = st.selectbox("نوع الخدمة", srvs, index=srvs.index(r_service) if r_service in srvs else 0)
                e_price = st.number_input("قيمة العرض (بالريال)", value=r_price, step=500.0)
                e_phone = st.text_input("رقم جوال المهندس / التواصل", value=r_phone)
            with col_e3:
                rsns = ["لا يوجد / قيد المتابعة", "السعر مرتفع مقارنة بالمنافسين", "لديهم مختبر آخر حصري", "تأخير في إصدار رخصة بلدي من طرفهم", "العميل غير مهتم بالبناء حالياً", "مشكلة في سرعة ومواعيد الجسات لدينا"]
                e_reason = st.selectbox("سبب عدم إتمام العقد", rsns, index=rsns.index(r_reason) if r_reason in rsns else 0)
                e_next_visit = st.date_input("موعد المتابعة القادمة", r_next_visit)
                e_email = st.text_input("البريد الإلكتروني للجهة", value=r_email)
                
            e_notes = st.text_area("تحديث الملاحظات الفنية ونتائج المتابعة", value=r_notes)
            
            if st.form_submit_button("💾 حفظ التعديلات وتحديث البيانات"):
                days = "0"
                if "شريك" in e_status or "معتمد" in e_status:
                    try:
                        start = datetime.strptime(r_first_date.strip(), "%Y-%m-%d")
                        days = str(max(0, (datetime.now() - start).days))
                    except: days = "1"
                    
                for current_idx in idx_list:
                    df_crm.at[current_idx, "حالة العميل"] = str(e_status)
                    df_crm.at[current_idx, "اسم المندوب"] = str(e_agent)
                    df_crm.at[current_idx, "نوع الخدمة"] = str(e_service)
                    df_crm.at[current_idx, "قيمة العرض"] = str(e_price)
                    df_crm.at[current_idx, "سبب عدم التعاقد"] = str(e_reason)
                    df_crm.at[current_idx, "موعد المتابعة القادمة"] = str(e_next_visit.strftime("%Y-%m-%d"))
                    df_crm.at[current_idx, "آخر تحديث"] = str(e_notes)
                    df_crm.at[current_idx, "تاريخ الزيارة الأخيرة"] = str(datetime.now().strftime("%Y-%m-%d"))
                    df_crm.at[current_idx, "أيام الإغلاق"] = str(days)
                    df_crm.at[current_idx, "المهندس المسؤول"] = str(e_contact_name)
                    df_crm.at[current_idx, "رقم الجوال"] = str(e_phone)
                    df_crm.at[current_idx, "البريد الإلكتروني"] = str(e_email)
                
                df_crm.to_csv(DATA_FILE, index=False)
                st.success("تم تحديث وحفظ البيانات بنجاح!")
                st.rerun()
else:
    st.write("سجل جهات أولاً لتفعيل محرك البحث.")

st.markdown("---")

st.header("➕ إضافة مكتب هندسي أو شركة مقاولات جديدة")
with st.form("add_client_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("اسم الجهة (الشركة/المكتب)")
        client_type = st.selectbox("النوع", ["مكتب استشارات هندسية", "شركة مقاولات عامة", "مطور عقاري", "أخرى"])
        agent_name = st.selectbox("اسم المندوب القائم بالزيارة", SALES_TEAM)
        contact_name = st.text_input("اسم المهندس المسؤول هناك")
    with col2:
        region = st.selectbox("المنطقة", ["شمال الرياض", "شرق الرياض", "جنوب الرياض", "وسط الرياض", "غرب الرياض"])
        district = st.text_input("الحي بالتحديد")
        phone = st.text_input("رقم جوال المهندس / التواصل")
    with col3:
        status = st.selectbox("الحالة الأولية", ["مستهدف (لم يزر)", "تمت الزيارة الأولى"])
        next_visit = st.date_input("موعد المتابعة القادمة", datetime.now())
        email = st.text_input("البريد الإلكتروني للجهة")

    last_notes = st.text_area("تفاصيل الزيارة الميدانية الأولى")
    if st.form_submit_button("حفظ وبدء حساب الوقت وبناء الداتا"):
        if name:
            new_data = {
                "الاسم": str(name), "النوع": str(client_type), "المنطقة": str(region), "الحي": str(district),
                "حالة العميل": str(status), "آخر تحديث": str(last_notes), "تاريخ الزيارة الأخيرة": str(datetime.now().strftime("%Y-%m-%d")),
                "موعد المتابعة القادمة": str(next_visit.strftime("%Y-%m-%d")), "سبب عدم التعاقد": "لا يوجد / قيد المتابعة",
                "اسم المندوب": str(agent_name), "نوع الخدمة": "لم تحدد بعد", "قيمة العرض": "0",
                "تاريخ أول زيارة": str(datetime.now().strftime("%Y-%m-%d")), "أيام الإغلاق": "0",
                "المهندس المسؤول": str(contact_name), "رقم الجوال": str(phone), "البريد الإلكتروني": str(email)
            }
            df_crm = pd.concat([df_crm, pd.DataFrame([new_data])], ignore_index=True)
            df_crm.to_csv(DATA_FILE, index=False)
            st.success(f"تم حفظ {name} وبيانات المهندس بنجاح!")
            st.rerun()

st.markdown("---")

st.header("📥 قاعدة بيانات العملاء المحتملين وتفاصيل التواصل المجمعة")
prospects_only = df_crm[~df_crm["حالة العميل"].str.contains("شريك|معتمد", na=False, case=False)]
st.dataframe(prospects_only[["الاسم", "النوع", "المنطقة", "المهندس المسؤول", "رقم الجوال", "حالة العميل", "اسم المندوب", "موعد المتابعة القادمة"]], use_container_width=True)
csv_bytes = prospects_only.to_csv(index=False).encode('utf-8-sig')
