import streamlit as st
import pandas as pd
import os
import json



#Bild, Titel und Text eingefügt
st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTei8JNT3F-9ALGCAYqlL9EtMNxkcrywPjJpg&usqp=CAU")
st.title("SmartUp!")
st.header("Wow meine Noten!")

# Dokument bei dem alle Angaben gespeichert werden
DATA_FILE = "data2.json"

# Funktion um die Daten vom json file zu laden
def load_data():
    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    else:
        data = []
    return data

# Funktion zum Löschen der Notenliste aus dem data2.json-File
def delete_data():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        file.write("[]")

delete_button = st.button('Alle Noten löschen')
if delete_button:
    delete_data()
    st.write('Alle Noten wurden gelöscht.')

# Funktion um die Noten im json File zu speichern
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

# Notensystem von der Schweiz
grading_system = {'6.0': 'Excellent','5.75':'Excellent', '5.5': 'Very good','5.25':'Very good','5.0': 'Good', '4.75':'Good','4.5': 'Satisfactory', 
                  '4.25': 'Satisfactory','4.0': 'Sufficient','3.75': 'Sufficient', '3.5': 'Marginally sufficient','3.25': 'Marginally sufficient', '3.0': 'Insufficient',
                  '2.75': 'Insufficient','2.5': 'Insufficient','2.25': 'Insufficient','2.0': 'Very insufficient','1.75': 'Very insufficient','1.5': 'Very insufficient','1.25': 'Very insufficient', '1.0': 'Completely insufficient', '0.0': 'Not graded'}

# Funktion um die Daten vom json file zu laden
grades_data = load_data()

# dataframe kreieren um die Noten zu speichern
if grades_data:
    grades_df = pd.DataFrame(grades_data)
else:
    grades_df = pd.DataFrame(columns=['Fach', 'Note', 'Gewichtung'])


# Funktion zum Löschen einer spezifischen Note aus der JSON-Datei
def delete_grade(Fach, Note, Gewichtung):
    data = load_data()
    for entry in data:
        if entry["Fach"] == Fach and entry["Note"] == Note and entry['Gewichtung'] == Gewichtung:
            data.remove(entry)
    save_data(data)

#deletegrade_button = st.button('Eine Noten löschen')
#if deletegrade_button:
 #   delete_grade()
  #  st.write('Die Note wurden gelöscht.')
    
# Funktion um den Durchschnitt der einzelnen Fächer zu berrechnen
def compute_average_grade(df):
    df['Note'] = df['Note'].astype(float) # Convert the grade column to float
    df['Gewichtung'] = df['Gewichtung'].astype(float) # Convert the weight column to float
    df['Durchschnitt'] = df['Note'] * df['Gewichtung'] # Compute the weighted grade
    avg_df = df.groupby(['Fach'])['Durchschnitt', 'Gewichtung'].sum()
    avg_df['Notendurchschnitt'] = avg_df['Durchschnitt'] / avg_df['Gewichtung'] # Compute the average grade
    avg_df.drop(columns=['Durchschnitt', 'Gewichtung'], inplace=True)
    avg_df['Notendurchschnitt'] = avg_df['Notendurchschnitt'].apply(lambda x: '{:.1f}'.format(x)) # Format the average grade
    avg_df.reset_index(inplace=True)
    return avg_df


# Das layout von der App
st.title('Füge deine Noten ein:')
course_name = st.text_input('Fach')
grade = st.selectbox('Deine Note', list(grading_system.keys()))
weight = st.number_input('Gewichtung der Note', min_value=0.0, max_value=1.0, value=1.0, step=0.05)
submit_button = st.button('Einreichen')
if submit_button:
    grades_df = grades_df.append({'Fach': course_name, 'Note': grade, 'Gewichtung': weight}, ignore_index=True)
    avg_df = compute_average_grade(grades_df)
    st.write(avg_df)
    st.write(grades_df)
    grades_data = grades_df.to_dict('records')
    save_data(grades_data)

    
# Funktion zum Hervorheben von Noten in einer Tabelle
def highlight_grades(df):
    def highlight_color(val):
        if isinstance(val, str):
            return ''
        elif val >= 4:
            return 'color: green'
        else:
            return 'color: red'

    return df.style.applymap(highlight_color, subset=['Note', 'Durchschnitt'])

# Laden der Daten aus der JSON-Datei und Erstellung des DataFrame
data = load_data()
df = pd.DataFrame(data)

# Berechnung des Durchschnitts für jeden Kurs
df['Durchschnitt'] = df.groupby('Fach')['Note'].transform('mean')

# Hervorheben der Noten in der Tabelle
highlighted_df = highlight_grades(df)

# Anzeigen der formatierten Tabelle
st.dataframe(highlighted_df, height=500)

# Darstellung im App

st.header("Wunsch Note")
st.write("Hier kannst du berrechnen was für eine Note du noch erziehlen musst um deinen gewünschten Durchschnitt zu erreichen.")
st.write("Beachte, dass die Gewichtung nicht über 100% in dem Fach betragen sollte.")

# Funktion zur Berechnung der benötigten Note für einen gewünschten Durchschnitt
def calculate_required_grade(df, subject, desired_avg):
    current_avg = df[df['Fach'] == subject]['Durchschnitt'].iloc[0]
    remaining_weight = 1 - df[df['Fach'] == subject]['Gewichtung'].iloc[0]
    required_grade = (desired_avg - (current_avg * remaining_weight)) / df[df['Fach'] == subject]['Gewichtung'].iloc[0]
    return required_grade

data = load_data()
df = pd.DataFrame(data)

# Berechnung des Durchschnitts für jeden Kurs
df['Durchschnitt'] = df.groupby('Fach')['Note'].transform('mean')

# Anzeige des Eingabeformulars
with st.form('calculate_grade'):
    subject = st.selectbox('Fach auswählen', df['Fach'].unique())
    desired_avg = st.number_input('Gewünschter Durchschnitt', min_value=1.0, max_value=6.0, value=4.0)
    submit_button = st.form_submit_button('Berechnen')

# Berechnung der benötigten Note und Anzeige des Ergebnisses
if submit_button:
    required_grade = calculate_required_grade(df, subject, desired_avg)
    message = f"Um einen Durchschnitt von {desired_avg} im Fach {subject} zu erreichen, benötigen Sie eine Note von {required_grade:.1f}"
    st.write(message)
