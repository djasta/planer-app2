import streamlit as st
from supabase import create_client
from datetime import datetime

st.set_page_config(page_title="Troškovi", layout="centered")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def format_money(x):
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def get_all_rows():
    response = supabase.table("troskovi").select("*").execute()
    return response.data or []


def get_months():
    rows = get_all_rows()
    months = sorted(list(set(row["mesec"] for row in rows if row.get("mesec"))))
    return months


def get_expenses(month):
    response = (
        supabase.table("troskovi")
        .select("*")
        .eq("mesec", month)
        .neq("naziv", "__PLATA__")
        .execute()
    )
    return response.data or []


def get_salary(month):
    response = (
        supabase.table("troskovi")
        .select("*")
        .eq("mesec", month)
        .eq("naziv", "__PLATA__")
        .execute()
    )

    rows = response.data or []

    if len(rows) == 0:
        return 0.0

    return float(rows[0].get("iznos") or 0)


def save_salary(month, amount):
    response = (
        supabase.table("troskovi")
        .select("*")
        .eq("mesec", month)
        .eq("naziv", "__PLATA__")
        .execute()
    )

    rows = response.data or []

    if len(rows) == 0:
        supabase.table("troskovi").insert({
            "mesec": month,
            "naziv": "__PLATA__",
            "kategorija": "plata",
            "iznos": float(amount),
            "datum": datetime.now().strftime("%d.%m.%Y")
        }).execute()
    else:
        supabase.table("troskovi").update({
            "iznos": float(amount)
        }).eq("id", rows[0]["id"]).execute()


st.title("💸 Finansije App")
st.subheader("📁 Meseci")

months = get_months()

new_month = st.text_input("Novi mesec")

if st.button("➕ Kreiraj / Otvori"):
    if new_month:
        st.session_state["month"] = new_month

        if new_month not in months:
            save_salary(new_month, 0)

        st.rerun()

months = get_months()

if months:
    selected_month = st.selectbox("Otvori mesec", months)

    if st.button("Otvori"):
        st.session_state["month"] = selected_month
        st.rerun()

if "month" not in st.session_state:
    st.stop()

month = st.session_state["month"]

st.divider()
st.title(f"📊 {month}")

current_salary = get_salary(month)

plata = st.number_input(
    "💰 Plata",
    min_value=0.0,
    step=500.0,
    value=float(current_salary)
)

save_salary(month, plata)

st.subheader("➕ Dodaj trošak")

naziv = st.text_input("Naziv")
kategorija = st.selectbox("Kategorija", ["🏠 Potrebe", "🎉 Želje"])
iznos = st.number_input("Iznos", min_value=0.0, step=100.0)

if st.button("Dodaj"):
    if naziv:
        supabase.table("troskovi").insert({
            "mesec": month,
            "naziv": naziv,
            "kategorija": kategorija,
            "iznos": float(iznos),
            "datum": datetime.now().strftime("%d.%m.%Y")
        }).execute()

        st.success("Dodato ✔")
        st.rerun()

st.divider()
st.subheader("📊 Pregled")

troskovi = get_expenses(month)

ukupno = sum(float(x["iznos"] or 0) for x in troskovi)
potrebe = sum(float(x["iznos"] or 0) for x in troskovi if x["kategorija"] == "🏠 Potrebe")
zelje = sum(float(x["iznos"] or 0) for x in troskovi if x["kategorija"] == "🎉 Želje")

st.write(f"🏠 Potrebe: {format_money(potrebe)} RSD")
st.write(f"🎉 Želje: {format_money(zelje)} RSD")
st.write(f"📦 Ukupno: {format_money(ukupno)} RSD")

ostaje = plata - ukupno

if ostaje >= 0:
    st.success(f"Ostaje: {format_money(ostaje)} RSD")
else:
    st.error(f"Minus: {format_money(abs(ostaje))} RSD")

st.divider()
st.subheader("📋 Svi troškovi")

if len(troskovi) == 0:
    st.info("Nema troškova.")
else:
    top3_ids = set(
        x["id"] for x in sorted(
            troskovi,
            key=lambda x: float(x["iznos"] or 0),
            reverse=True
        )[:3]
    )

    kategorije = ["🏠 Potrebe", "🎉 Želje"]

    for kat in kategorije:
        stavke = [x for x in troskovi if x["kategorija"] == kat]

        with st.expander(f"{kat} ({len(stavke)})", expanded=True):
            if len(stavke) == 0:
                st.info("Nema troškova u ovoj kategoriji.")
            else:
                for broj, x in enumerate(stavke, start=1):
                    color = "red" if x["id"] in top3_ids else "green"
                    datum = x.get("datum", "Bez datuma")

                    st.markdown(f"### {broj}. {x['naziv']}")
                    st.caption(f"📅 {datum}")

                    st.markdown(
                        f"<span style='color:{color}; font-weight:bold; font-size:20px;'>"
                        f"→ {format_money(float(x['iznos'] or 0))} RSD"
                        f"</span>",
                        unsafe_allow_html=True
                    )

                    btn1, btn2 = st.columns(2)

                    with btn1:
                        if st.button("✏️ Edit", key=f"edit_{x['id']}", use_container_width=True):
                            st.session_state["edit_id"] = x["id"]
                            st.rerun()

                    with btn2:
                        if st.button("🗑️ Delete", key=f"del_{x['id']}", use_container_width=True):
                            supabase.table("troskovi").delete().eq("id", x["id"]).execute()
                            st.rerun()

                    st.divider()

if "edit_id" in st.session_state:
    edit_id = st.session_state["edit_id"]

    response = (
        supabase.table("troskovi")
        .select("*")
        .eq("id", edit_id)
        .execute()
    )

    rows = response.data or []

    if rows:
        item = rows[0]

        st.subheader("✏️ Edit trošak")

        new_name = st.text_input(
            "Naziv",
            item["naziv"],
            key=f"edit_naziv_{edit_id}"
        )

        new_cat = st.selectbox(
            "Kategorija",
            ["🏠 Potrebe", "🎉 Želje"],
            index=0 if item["kategorija"] == "🏠 Potrebe" else 1,
            key=f"edit_kategorija_{edit_id}"
        )

        new_amount = st.number_input(
            "Iznos",
            value=float(item["iznos"] or 0),
            key=f"edit_iznos_{edit_id}"
        )

        if st.button("Sačuvaj", key=f"sacuvaj_edit_{edit_id}"):
            supabase.table("troskovi").update({
                "naziv": new_name,
                "kategorija": new_cat,
                "iznos": float(new_amount),
                "datum": item.get("datum", datetime.now().strftime("%d.%m.%Y"))
            }).eq("id", edit_id).execute()

            del st.session_state["edit_id"]
            st.rerun()
    else:
        del st.session_state["edit_id"]
        st.rerun()
