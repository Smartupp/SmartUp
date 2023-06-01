import streamlit as st
import pandas as pd
import os
import json
from jsonbin import load_key, save_key
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# -------- load secrets for jsonbin.io --------
jsonbin_secrets = st.secrets["jsonbin"]
api_key = jsonbin_secrets["api_key"]
bin_id = jsonbin_secrets["bin_id"]

# -------- user login --------
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

fullname, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == True:   # login successful
    authenticator.logout('Logout', 'main')   # show logout button
elif authentication_status == False:
    st.error('Username/password is incorrect')
    st.stop()
elif authentication_status == None:
    st.warning('Please enter your username and password')
    st.stop()

# Notensystem von der Schweiz
grading_system = {'6.0': 'Excellent','5.75':'Excellent', '5.5': 'Very good','5.25':'Very good','5.0': 'Good', '4.75':'Good','4.5': 'Satisfactory', 
                  '4.25': 'Satisfactory','4.0': 'Sufficient','3.75': 'Sufficient', '3.5': 'Marginally sufficient','3.25': 'Marginally sufficient', '3.0': 'Insufficient',
                  '2.75': 'Insufficient','2.5': 'Insufficient','2.25': 'Insufficient','2.0': 'Very insufficient','1.75': 'Very insufficient','1.5': 'Very insufficient','1.25': 'Very insufficient', '1.0': 'Completely insufficient', '0.0': 'Not graded'}

# Daten aus json file Laden
data = load_key(api_key, bin_id, username)

if len(data) == 0:
    st.write("Keine Noten vorhanden")
    data = pd.DataFrame({
        "Semester": [],
        "Fach": [],
        "Note": [],
        "ECTS": [],
        "Gewichtung": []
    })
else:
    data = pd.DataFrame(data)

# Funktion zum Hervorheben von niedrigen Noten
def highlight_low_grades(value):
    if float(value) < 4.0:
        return 'background-color: yellow'
    else:
        return ''

# Streamlit App
st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTei8JNT3F-9ALGCAYqlL9EtMNxkcrywPjJpg&usqp=CAU")
st.title("SmartUp!")

# Tab-Navigation
tabs = ["Noten eingeben", "Notenansicht", "Noten löschen"]
selected_tab = st.sidebar.radio("Navigation", tabs)

# Tab: Noten eingeben
if selected_tab == "Noten eingeben":
    st.header("Wow meine Noten!")
    st.subheader("Noten eingeben")
    semester = st.number_input("Semester", min_value=1, max_value=10, step=1, value=1)
    subject = st.text_input("Fach", value="")
    ects = st.number_input("ECTS", min_value=1, max_value=30, step=1, value=1)
    grade = st.selectbox("Note", list(grading_system.keys()), index=8)
    gewichtung = st.number_input("Gewichtung", min_value=0.05, max_value=1.0, step=0.05, value=1.0)
    submit_button = st.button("Hinzufügen")

    data_new = {"Fach": subject, "Note": float(grade), "ECTS": ects, "Gewichtung": gewichtung, "Semester": semester}
    df = pd.DataFrame(data_new, index=[0])
    fin_df = pd.concat([data, df], ignore_index=True)
   
    # Daten in DataFrame speichern
    if submit_button:
        save_key(api_key, bin_id, username, fin_df.to_dict(orient='records'))
        st.write("Note hinzugefügt")

# Tab: Notenansicht
elif selected_tab == "Notenansicht":
    st.subheader("Notenansicht")
    view_option = st.selectbox("Ansichtsoption", ["Alle Noten", "Fach spezifisch", "Semester spezifisch"])

    if view_option == "Alle Noten":
        st.dataframe(data.style.applymap(highlight_low_grades, subset=['Note']))

        # Berechnung der benötigten Note für eine 4.0
        calculate_grade = st.button("Berechnen")
        if calculate_grade:
            desired_grade = 4.0
            current_grades = data['Note'].tolist()
            total_tests = len(current_grades) + 1
            current_average = sum(current_grades) / len(current_grades)
            required_grade = (desired_grade * total_tests) - sum(current_grades)

            if required_grade > 6.0:
                st.error("Die benötigte Note ist nicht erreichbar.")
            else:
                st.success(f"Um eine 4.0 in allen {total_tests} Tests zu erreichen, müssen Sie mindestens eine Note von {required_grade:.2f} im nächsten Test erhalten.")

    elif view_option == "Fach spezifisch":
        selected_subject = st.selectbox("Fach auswählen", data['Fach'].unique())
        subject_data = data[data['Fach'] == selected_subject]
        st.dataframe(subject_data.style.applymap(highlight_low_grades, subset=['Note']))

        # Berechnung der benötigten Note für eine 4.0
        calculate_grade = st.button("Berechnen für Fach")
        if calculate_grade:
            desired_grade = 4.0
            current_grades = subject_data['Note'].tolist()
            total_tests = len(current_grades) + 1
            current_average = sum(current_grades) / len(current_grades)
            required_grade = (desired_grade * total_tests) - sum(current_grades)

            if required_grade > 6.0:
                st.error("Die benötigte Note ist nicht erreichbar.")
            else:
                st.success(f"Um eine 4.0 in {selected_subject} in allen {total_tests} Tests zu erreichen, müssen Sie mindestens eine Note von {required_grade:.2f} im nächsten Test erhalten.")

    elif view_option == "Semester spezifisch":
        selected_semester = st.selectbox("Semester auswählen", data['Semester'].unique())
        semester_data = data[data['Semester'] == selected_semester]
        st.dataframe(semester_data.style.applymap(highlight_low_grades, subset=['Note']))

        # Berechnung der benötigten Note für eine 4.0
        calculate_grade = st.button("Berechnen für Semester")
        if calculate_grade:
            desired_grade = 4.0
            current_grades = semester_data['Note'].tolist()
            total_tests = len(current_grades) + 1
            current_average = sum(current_grades) / len(current_grades)
            required_grade = (desired_grade * total_tests) - sum(current_grades)

            if required_grade > 6.0:
                st.error("Die benötigte Note ist nicht erreichbar.")
            else:
                st.success(f"Um eine 4.0 im {selected_semester}. Semester in allen {total_tests} Tests zu erreichen, müssen Sie mindestens eine Note von {required_grade:.2f} im nächsten Test erhalten.")

# Tab: Noten löschen
elif selected_tab == "Noten löschen":
    st.subheader("Noten löschen")
    delete_option = st.selectbox("Lösch-Option", ["Spezifische Note löschen", "Alle Daten löschen"])

    if delete_option == "Spezifische Note löschen":
        selected_index = st.number_input("Index der zu löschenden Note", min_value=0, max_value=len(data)-1, step=1)
        if st.button("Löschen"):
            data = data.drop(index=selected_index).reset_index(drop=True)
            save_key(api_key, bin_id, username, data.to_dict(orient='records'))
            st.success("Note erfolgreich gelöscht")

    elif delete_option == "Alle Daten löschen":
        st.warning("Diese Aktion kann nicht rückgängig gemacht werden. Klicken Sie auf 'Löschen', um fortzufahren.")
        if st.button("Löschen"):
            data = pd.DataFrame({
                "Semester": [],
                "Fach": [],
                "Note": [],
                "ECTS": [],
            })
            save_key(api_key, bin_id, username, data.to_dict(orient='records'))
            st.success("Alle Daten erfolgreich gelöscht")

