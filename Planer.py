import streamlit as st
import json
import os

st.set_page_config(page_title="Troškovi", layout="centered")

FILE = "data.json"

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
# HOME / MESECI
# ---------------------------
st.title("💸 Finansije App")

st.subheader("📁 Meseci")

new_month = st.text_input("Novi mesec (npr. Maj 2026)")

if st.button("➕ Kreiraj / Otvori mesec"):
    if new_month:
        if new_month not in data:
            data[new_month] = []
            save_data(data)
        st.session_state["month"] = new_month

if data:
    selected_month = st.selectbox("Otvori mesec", list(data.keys()))
    if st.button("Otvori"):
        st.session_state["month"] = selected_month

if "month" not in st.session_state:
    st.stop()

month = st.session_state["month"]

st.divider()
st.title(f"📊 {month}")

# ---------------------------
# PLATA
# ---------------------------
plata = st.number_input("💰 Plata (RSD)", min_value=0.0, step=500.0)

# ---------------------------
# DODAVANJE TROŠKA
# ---------------------------
st.subheader("➕ Dodaj trošak")

naziv = st.text_input("Naziv troška")
kategorija = st.selectbox("Kategorija", ["🏠 Potrebe", "🎉 Želje"])
iznos = st.number_input("Iznos", min_value=0.0, step=100.0)

if st.button("Dodaj"):
    if naziv:
        data[month].append({
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

troskovi = data.get(month, [])

ukupno = sum(x["iznos"] for x in troskovi)
potrebe = sum(x["iznos"] for x in troskovi if x["kategorija"] == "🏠 Potrebe")
zelje = sum(x["iznos"] for x in troskovi if x["kategorija"] == "🎉 Želje")

st.write(f"🏠 Potrebe: {potrebe:.2f} RSD")
st.write(f"🎉 Želje: {zelje:.2f} RSD")
st.write(f"📦 Ukupno: {ukupno:.2f} RSD")

ostaje = plata - ukupno

if ostaje >= 0:
    st.success(f"Ostaje: {ostaje:.2f} RSD")
else:
    st.error(f"Minus: {abs(ostaje):.2f} RSD")

# ---------------------------
# LISTA + BRISANJE
# ---------------------------
st.divider()
st.subheader("📋 Svi troškovi")

if len(troskovi) == 0:
    st.info("Nema troškova još.")
else:
    for i, x in enumerate(troskovi):
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(
                f"**{x['naziv']}** ({x['kategorija']}) → "
                f"<span style='color:#00C853; font-weight:bold'>{x['iznos']:.2f} RSD</span>",
                unsafe_allow_html=True
            )

        with col2:
            if st.button("🗑️", key=f"del_{i}"):
                data[month].pop(i)
                save_data(data)
                st.rerun()