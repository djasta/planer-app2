import streamlit as st
import json
import os

st.set_page_config(page_title="Troškovi", layout="centered")

FILE = "data.json"
RSD_TO_EUR = 0.0085  # približno

# ---------------------------
# LOAD / SAVE
# ---------------------------
def load_data():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
            except:
                pass
    return {}

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load_data()

# ---------------------------
# FORMAT
# ---------------------------
def format_money(x):
    return f"{x:,.2f}"

# ---------------------------
# INIT MONTH
# ---------------------------
st.title("💸 Finansije App")

currency = st.radio("Valuta", ["RSD", "EUR"])

st.subheader("📁 Meseci")

new_month = st.text_input("Novi mesec (npr. Maj 2026)")

if st.button("➕ Kreiraj / Otvori mesec"):
    if new_month:
        if new_month not in data:
            data[new_month] = {"plata": 0.0, "troskovi": []}
            save_data(data)
        st.session_state["month"] = new_month

if data:
    selected_month = st.selectbox("Otvori mesec", list(data.keys()))
    if st.button("Otvori"):
        st.session_state["month"] = selected_month

if "month" not in st.session_state:
    st.stop()

month = st.session_state["month"]

# sigurnost strukture
if month not in data:
    data[month] = {"plata": 0.0, "troskovi": []}

st.divider()
st.title(f"📊 {month}")

# ---------------------------
# PLATA (SAVE PO MESECU)
# ---------------------------
plata = st.number_input(
    "💰 Plata",
    min_value=0.0,
    step=500.0,
    value=float(data[month]["plata"])
)

data[month]["plata"] = float(plata)
save_data(data)

# ---------------------------
# DODAVANJE TROŠKA
# ---------------------------
st.subheader("➕ Dodaj trošak")

naziv = st.text_input("Naziv troška")
kategorija = st.selectbox("Kategorija", ["🏠 Potrebe", "🎉 Želje"])
iznos = st.number_input("Iznos", min_value=0.0, step=100.0)

if st.button("Dodaj"):
    if naziv:
        data[month]["troskovi"].append({
            "naziv": naziv,
            "kategorija": kategorija,
            "iznos": float(iznos)
        })
        save_data(data)
        st.success("Dodato ✔")

# ---------------------------
# PREGLED
# ---------------------------
st.divider()
st.subheader("📊 Pregled")

troskovi = data[month]["troskovi"]
plata = data[month]["plata"]

ukupno = sum(x["iznos"] for x in troskovi)
potrebe = sum(x["iznos"] for x in troskovi if x["kategorija"] == "🏠 Potrebe")
zelje = sum(x["iznos"] for x in troskovi if x["kategorija"] == "🎉 Želje")

if currency == "EUR":
    st.write(f"🏠 Potrebe: {format_money(potrebe * RSD_TO_EUR)} €")
    st.write(f"🎉 Želje: {format_money(zelje * RSD_TO_EUR)} €")
    st.write(f"📦 Ukupno: {format_money(ukupno * RSD_TO_EUR)} €")

    ostaje = (plata - ukupno) * RSD_TO_EUR

    if ostaje >= 0:
        st.success(f"Ostaje: {format_money(ostaje)} €")
    else:
        st.error(f"Minus: {format_money(abs(ostaje))} €")

else:
    st.write(f"🏠 Potrebe: {format_money(potrebe)} RSD")
    st.write(f"🎉 Želje: {format_money(zelje)} RSD")
    st.write(f"📦 Ukupno: {format_money(ukupno)} RSD")

    ostaje = plata - ukupno

    if ostaje >= 0:
        st.success(f"Ostaje: {format_money(ostaje)} RSD")
    else:
        st.error(f"Minus: {format_money(abs(ostaje))} RSD")

# ---------------------------
# TOP 3
# ---------------------------
st.divider()
st.subheader("🔥 Top 3 troška")

top3 = sorted(troskovi, key=lambda x: x["iznos"], reverse=True)[:3]

for x in top3:
    st.markdown(
        f"<span style='color:red; font-weight:bold'>"
        f"{x['naziv']} → {format_money(x['iznos'])} RSD"
        f"</span>",
        unsafe_allow_html=True
    )

# ---------------------------
# LISTA + EDIT + DELETE
# ---------------------------
st.divider()
st.subheader("📋 Svi troškovi")

if len(troskovi) == 0:
    st.info("Nema troškova još.")
else:
    for i, x in enumerate(troskovi):
        col1, col2, col3 = st.columns([4, 1, 1])

        with col1:
            st.write(f"**{x['naziv']}** ({x['kategorija']}) → {format_money(x['iznos'])} RSD")

        with col2:
            if st.button("✏️", key=f"edit_{i}"):
                st.session_state["edit_index"] = i

        with col3:
            if st.button("🗑️", key=f"del_{i}"):
                data[month]["troskovi"].pop(i)
                save_data(data)
                st.rerun()

# ---------------------------
# EDIT MODE
# ---------------------------
if "edit_index" in st.session_state:
    idx = st.session_state["edit_index"]
    item = data[month]["troskovi"][idx]

    st.subheader("✏️ Edit trošak")

    new_name = st.text_input("Naziv", item["naziv"])
    new_cat = st.selectbox(
        "Kategorija",
        ["🏠 Potrebe", "🎉 Želje"],
        index=0 if item["kategorija"] == "🏠 Potrebe" else 1
    )
    new_amount = st.number_input("Iznos", value=float(item["iznos"]))

    if st.button("Sačuvaj"):
        data[month]["troskovi"][idx] = {
            "naziv": new_name,
            "kategorija": new_cat,
            "iznos": float(new_amount)
        }
        save_data(data)
        del st.session_state["edit_index"]
        st.rerun()
