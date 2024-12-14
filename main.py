import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
API_KEY = 'AIzaSyDr5FmPRhSzNK8UgUl3KpOct-fQHvtA7GE'
genai.configure(api_key=API_KEY)

# Streamlit app title
st.title("Ansu's Homework helper")

# Configure model generation settings
generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    safety_settings=safety_settings,
    generation_config=generation_config,
    system_instruction=(
        "You are an expert at teaching science,maths,social and other subjects to kids. Your task is to engage in conversations about science and others. "
        "Keep your answers as short and to the point as possible. "
        "Make sure if the prompt is in Nepali then answer in Nepali. "
        "Try to give answers of questions with context of Nepal. "
        "Rely on past chats as well. "
        "If the prompts are given in English answer in English as well."
    ),
)

# Chat session
chat_session = model.start_chat(history=[])

# Function to generate notes using AI
def generate_notes(subject, chapter):
    prompt = f"Write notes for the {subject} subject on the chapter '{chapter}'."
    response = chat_session.send_message(prompt)
    return response.text

# Function to save notes to a JSON file
def save_notes(notes):
    with open("notes.json", "w") as f:
        json.dump(notes, f, indent=4)

# Function to load notes from the JSON file
def load_notes():
    if os.path.exists("notes.json"):
        with open("notes.json", "r") as f:
            return json.load(f)
    return {}

# Notes Tab
tab_selection = st.sidebar.radio("Choose a tab", ["Homework helper", "Notes"])

# Load existing notes
notes = load_notes()

if tab_selection == "Homework helper":
    # Prompt input from user
    prompt = st.text_area("Enter your question:", placeholder="Type your question here...")

    # Submit button
    if st.button("Ask 🤓"):
        if not prompt:
            st.error("Please enter a prompt before submitting.")
        else:
            try:
                # Send message to model
                response = chat_session.send_message(prompt)
                model_response = response.text

                # Display the model response
                st.subheader("Model Response:")
                st.write(model_response)

                # Update chat history
                chat_session.history.append({"role": "user", "parts": [prompt]})
                chat_session.history.append({"role": "model", "parts": [model_response]})

            except Exception as e:
                st.error(f"An error occurred: {e}")

elif tab_selection == "Notes":
    st.title("Notes Section")

    # Define subject frames
    subjects = ["English", "Nepali", "Social", "C.Math", "O.Math", "Science", "Health"]

    for subject in subjects:
        with st.expander(f"{subject} Notes", expanded=True):
            # Display existing chapters as dropdown
            chapter_choices = list(notes.get(subject, {}).keys())
            selected_chapter = st.selectbox(f"Select Chapter for {subject}:", options=[""] + chapter_choices)

            if selected_chapter:
                existing_notes = notes[subject].get(selected_chapter, "")
                updated_notes = st.text_area(f"Update notes for {subject} - {selected_chapter}:", value=existing_notes)

                extra_prompt = st.text_input("Provide extra prompt to edit the notes (optional):")

                if st.button(f"Update Notes for {subject} - {selected_chapter}"):
                    if updated_notes != existing_notes:
                        # Optionally send the extra prompt to the AI to edit the notes
                        if extra_prompt:
                            prompt = f"Update the following notes with this extra info: {extra_prompt}.\n\nExisting Notes: {updated_notes}"
                            response = chat_session.send_message(prompt)
                            updated_notes = response.text  # Get the AI's updated notes
                    
                    # Save updated notes
                    notes[subject][selected_chapter] = updated_notes
                    save_notes(notes)
                    st.success(f"Notes for {subject} - {selected_chapter} updated successfully!")

                # Option to delete the chapter
                if st.button(f"Delete Chapter {selected_chapter}"):
                    del notes[subject][selected_chapter]
                    save_notes(notes)
                    st.success(f"Chapter {selected_chapter} deleted successfully.")

                st.subheader(f"Current Notes for {subject} - {selected_chapter}")
                st.write(existing_notes)

            # Text input to add new chapter and notes
            chapter = st.text_input(f"Enter chapter for {subject}:", placeholder="e.g., Chapter 1: Introduction to Grammar")
            notes_input = st.text_area(f"Add notes for {subject} - {chapter}:", placeholder="Type your notes here...")

            # Option to ask AI to generate notes
            if st.button(f"Ask AI to Write Notes for {subject} - {chapter}") and chapter:
                ai_notes = generate_notes(subject, chapter)
                st.write("AI Generated Notes:")
                st.write(ai_notes)
                notes_input = ai_notes  # Set AI response to the notes input box

            # Store and display the notes for new chapter
            if chapter and notes_input:
                if subject not in notes:
                    notes[subject] = {}
                notes[subject][chapter] = notes_input
                save_notes(notes)  # Save notes to the JSON file
                st.subheader(f"Notes for {subject} - {chapter}")
                st.write(notes_input)

    # Display all saved notes
    if st.button("Show All Saved Notes"):
        st.subheader("Saved Notes")
        for subject, chapters in notes.items():
            st.write(f"### {subject}")
            for chapter, note in chapters.items():
                st.write(f"**{chapter}:** {note}")
