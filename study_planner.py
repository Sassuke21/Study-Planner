import streamlit as st

from bert_utils import get_bert_concept
from datetime import datetime
import pandas as pd

# Function to convert time intervals to hours
def convert_time_to_hours(time_interval):
    try:
        if " - " not in time_interval:
            raise ValueError("Invalid format! Use '9:00 AM - 11:00 AM'.")

        start_time_str, end_time_str = time_interval.split(" - ")
        start_time = datetime.strptime(start_time_str.strip(), "%I:%M %p")
        end_time = datetime.strptime(end_time_str.strip(), "%I:%M %p")

        duration = end_time - start_time
        if duration.total_seconds() < 0:
            raise ValueError("End time must be later than start time.")

        return duration.total_seconds() / 3600  # Convert to hours
    except ValueError as e:
        st.error(f"Error: {e}")
        return 0

class StudyPlanner:
    def __init__(self, study_goals, available_time, preferences, strengths, weaknesses):
        self.study_goals = study_goals
        self.available_time = available_time
        self.preferences = preferences
        self.strengths = strengths
        self.weaknesses = weaknesses
        self.study_progress = {subject: 0 for subject in study_goals}

    def display_study_plan(self):
        st.subheader("📚 Your Study Plan")
        df = pd.DataFrame({
            "Subject": [s.capitalize() for s in self.study_goals],
            "Time Allocation (hrs)": [self.available_time[s] for s in self.study_goals],
            "Preference": [self.preferences.get(s, "None") for s in self.study_goals],
            "Strength": [self.strengths.get(s, "None") for s in self.study_goals],
            "Weakness": [self.weaknesses.get(s, "None") for s in self.study_goals],
        })
        st.dataframe(df, use_container_width=True)

    def track_progress(self, subject, hours):
        if subject in self.study_progress:
            self.study_progress[subject] += hours
            st.success(f"✅ Updated progress: {subject.capitalize()} - {self.study_progress[subject]} hours studied")
        else:
            st.warning(f"⚠️ Subject '{subject}' not found in your study plan.")

    def show_progress(self):
        st.subheader("📊 Study Progress")
        progress_df = pd.DataFrame({
            "Subject": [s.capitalize() for s in self.study_progress.keys()],
            "Hours Studied": [self.study_progress[s] for s in self.study_progress.keys()],
            "Total Planned": [self.available_time[s] for s in self.study_progress.keys()],
        })
        st.bar_chart(progress_df.set_index("Subject"))

# Main function
def main():
    st.set_page_config(page_title="Study Planner", page_icon="📖", layout="wide")
    st.title("🎯 Study Planner")

    if "planner" not in st.session_state:
        st.session_state["planner"] = None  # Initialize session state

    with st.sidebar:
        st.header("📌 Setup Your Plan")
        study_goals = st.text_area("Enter subjects (comma-separated)").split(",")
        study_goals = [s.strip().lower() for s in study_goals if s.strip()]

        if not study_goals:
            st.warning("⚠️ Please enter at least one subject.")
            return  # Stop execution if no subjects are entered

        study_time_option = st.radio("Do you have a fixed schedule?", ["Yes", "No"])
        available_time = {}

        if study_time_option == "Yes":
            for goal in study_goals:
                time = st.text_input(f"Time for {goal.capitalize()} (e.g., 9:00 AM - 11:00 AM)")
                available_time[goal] = convert_time_to_hours(time)
        else:
            for goal in study_goals:
                available_time[goal] = st.number_input(f"Hours for {goal.capitalize()}", min_value=0.0, step=0.5)

        preferences, strengths, weaknesses = {}, {}, {}
        for goal in study_goals:
            with st.expander(f"🔍 {goal.capitalize()} Details"):
                preferences[goal] = st.text_input(f"Preference for {goal.capitalize()}")
                strengths[goal] = st.text_input(f"Strength in {goal.capitalize()}")
                weaknesses[goal] = st.text_input(f"Weakness in {goal.capitalize()}")

        if st.button("Generate Study Plan"):
            st.session_state["planner"] = StudyPlanner(study_goals, available_time, preferences, strengths, weaknesses)
            st.session_state["plan_generated"] = True  # Track if the plan was generated
            st.success("✅ Study plan created!")

    # Only show these sections if a study plan has been generated
    if st.session_state.get("plan_generated", False) and st.session_state["planner"]:
        planner = st.session_state["planner"]
        planner.display_study_plan()

        # Progress Tracking
        st.subheader("⏳ Track Your Progress")
        col1, col2 = st.columns([2, 1])
        with col1:
            subject = st.selectbox("Select a subject", planner.study_goals)
        with col2:
            hours_studied = st.number_input("Hours studied", min_value=0.0, step=0.5)

        if st.button("Update Progress"):
            planner.track_progress(subject, hours_studied)

        planner.show_progress()

if __name__ == "__main__":
    main()
