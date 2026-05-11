import streamlit as st
import json
import os

st.set_page_config(page_title="Troškovi", layout="centered")

FILE = "data.json"

# ---------------------------
# FORMAT BROJA
# ---------------------------
def format_money(x):
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ---------------------------
# LOAD / SAVE
# ---------------------------
def load_data():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            try:
                data = json.load(f)
            except:
                return {}

        for month in list(data.keys()):
            if isinstance(data[month], list):
                data[month] = {
                    "plata": 0.0,
                    "troskovi": data[month]
                }

            if not isinstance(data[month], dict):
                data[month] = {
                    "plata": 0.0,
                    "troskovi": []
                }

        return data

    return {}

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load_data()

# ---------------------------
# HOME
# ---------------------------
st.title("💸 Finansije App")

st.subheader("📁 Meseci")

new_month = st.text_input("Novi mesec")

if st.button("➕ Kreiraj / Otvori"):
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

if month not in data:
    data[month] = {"plata": 0.0, "troskovi": []}
    save_data(data)

st.divider()
st.title(f"📊 {month}")

# ---------------------------
# PLATA
# ---------------------------
plata = st.number_input(
    "💰 Plata",
    min_value=0.0,
    step=500.0,
    value=float(data[month].get("plata", 0.0))
)

data[month]["plata"] = float(plata)
save_data(data)

# ---------------------------
# DODAVANJE
# ---------------------------
st.subheader("➕ Dodaj trošak")

naziv = st.text_input("Naziv")
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

ukupno = sum(x["iznos"] for x in troskovi)
potrebe = sum(x["iznos"] for x in troskovi if x["kategorija"] == "🏠 Potrebe")
zelje = sum(x["iznos"] for x in troskovi if x["kategorija"] == "🎉 Želje")

st.write(f"🏠 Potrebe: {format_money(potrebe)} RSD")
st.write(f"🎉 Želje: {format_money(zelje)} RSD")
st.write(f"📦 Ukupno: {format_money(ukupno)} RSD")

ostaje = plata - ukupno

if ostaje >= 0:
    st.success(f"Ostaje: {format_money(ostaje)} RSD")
else:
    st.error(f"Minus: {format_money(abs(ostaje))} RSD")

# ---------------------------
# LISTA + TOP 3 BOJA + EDIT + DELETE
# ---------------------------
st.divider()
st.subheader("📋 Svi troškovi")

if len(troskovi) == 0:
    st.info("Nema troškova.")
else:
    sorted_indices = sorted(
        range(len(troskovi)),
        key=lambda i: troskovi[i]["iznos"],
        reverse=True
    )

    top3 = set(sorted_indices[:3])

    for i in range(len(troskovi)):
        x = troskovi[i]

        col1, col2, col3 = st.columns([5, 2, 2])

        with col1:
            st.markdown(f"{x['naziv']} {x['kategorija']}")

        color = "red" if i in top3 else "green"

        with col2:
            st.markdown(
                f"<span style='color:{color}; font-weight:bold'>"
                f"→ {format_money(x['iznos'])} RSD"
                f"</span>",
                unsafe_allow_html=True
            )

        with col3:
            btn1, btn2 = st.columns(2)

            with btn1:
                if st.button("✏️", key=f"edit_{i}"):
                    st.session_state["edit_index"] = i

            with btn2:
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
