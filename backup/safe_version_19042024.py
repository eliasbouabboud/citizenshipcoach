import json
import os
import streamlit as st
from streamlit.logger import get_logger
import random

LOGGER = get_logger(__name__)

index_map = {0: "A: ", 1: "B: ", 2: "C: ", 3: "D: "}


def transform_json(original_json):
    transformed_json = {}
    transformed_json["question"] = original_json["question"]
    transformed_json["answer_choices"] = []

    for index, choice in enumerate(original_json["choices"]):
        answer_choice = {
            "answer": choice,
            "is_correct": str(original_json["correct_answer"] == choice).lower() 
            }
        
        if original_json["correct_answer"] == choice : 
            answer_choice["explanation"] = original_json["explanation"] 
        else : 
            answer_choice["explanation"] = "Pas disponible"
       
        transformed_json["answer_choices"].append(answer_choice)

    return transformed_json



def load_questions(folder_path):
    json_files = [file for file in os.listdir(folder_path) if file.endswith('.json')]

    all_json_data = []
    for json_file in json_files:
        file_path = os.path.join(folder_path, json_file)
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            all_json_data.extend(json_data)

    return all_json_data


def gen_quiz(question_obj, key="my-form"):
    
    form = st.form(key=key)

    ans_list = question_obj["answer_choices"]
    choice_list = []
    correct_list = []
    exp_list = []


    q_string = question_obj["question"]

    for choice in ans_list:
        choice_list.append(choice["answer"])
        correct_list.append(choice["is_correct"])
        exp_list.append(choice["explanation"])

    selected_answer = form.radio(q_string, choice_list)
    submit = form.form_submit_button("Submit")

    curr_index = choice_list.index(selected_answer)

    if submit:
        # Check if correct
        curr_index = choice_list.index(selected_answer)

        if str(correct_list[curr_index]).lower() == "true":
            st.success("Correct! " + index_map[curr_index] + choice_list[curr_index])
            st.write(exp_list[curr_index])

            with st.expander("Explanations"):
                for index, item in enumerate(exp_list):
                    if index == curr_index:
                        continue
                    st.error(index_map[index] + choice_list[index])
                    st.write(item)
        else:
            st.error("Wrong! " + index_map[curr_index] + choice_list[curr_index])
            st.write(exp_list[curr_index])

            with st.expander("Explanations"):
                for index, item in enumerate(exp_list):
                    if index == curr_index:
                        continue

                    elif str(correct_list[index]).lower() == "true":
                        st.success(index_map[index] + choice_list[index])
                        st.write(item)

                    else:
                        st.error(index_map[index] + choice_list[index])
                        st.write(item)

def question_placeholder(questions, current_question) : 
    placeholder = st.empty()
    with placeholder.container():
      gen_quiz(transform_json(questions[current_question]), key="my-form")
      if st.button(label="Prochaine question", key="pro") : 
        placeholder.empty()


def choose_questions_for_session(questions_per_type) : 
    # Dictionary to group JSON objects by type
    type_groups = {}

    # Group JSON objects by type
    for json_obj in st.session_state.questions:
        type_key = json_obj["type"]
        if type_key not in type_groups:
            type_groups[type_key] = []
        type_groups[type_key].append(json_obj)

    # Dictionary to store randomly selected JSON objects per type
    random_selection = {}

    # Randomly select 10 JSON objects per type
    for type_key, group in type_groups.items():
        random.shuffle(group)  # Shuffle the list of JSON objects
        random_selection[type_key] = group[:questions_per_type]  # Select the first questions_per_type objects

    # Flatten the selected JSON objects into a single list
    return [json_obj for group in random_selection.values() for json_obj in group]




def next_question():
    if st.session_state.count + 1 >= len(st.session_state.questions):
        st.session_state.count = 0
    else:
        st.session_state.count += 1

def previous_question():
    if st.session_state.count > 0:
        st.session_state.count -= 1


def run():
    
    if 'questions' not in st.session_state:
        st.session_state.questions = load_questions("questions")

    if 'count' not in st.session_state:
      st.session_state.session_questions = choose_questions_for_session(questions_per_type = 4)
      
      st.session_state.count = 0
    #   st.session_state.available_quest = range(len(st.session_state.questions))
      st.session_state.chosen = {}


    st.title("Welcome to CitizenshipCoach! 👋")

    st.markdown(
        """
        Choissez une catégorie de question pour commencer, quel sujet préférez-vous ?
    """
    )


    # chosen = random.randrange(len(st.session_state.available_quest))
    

    # st.markdown("# Catégorie : " )

    question_categories = ["Histoire de France", "Géographie", "Structure politique", "Normes sociales"]
    category = st.selectbox("Choisissez une catégorie", question_categories)
  


    gen_quiz(transform_json(st.session_state.questions[st.session_state.count]), key="my-form")
    



    col1, col2 = st.columns(2)

    with col1:
        if st.button("⏮️ Previous", on_click=previous_question):
            pass

    with col2:
        if st.button("Next ⏭️", on_click=next_question):
            pass

    


if __name__ == "__main__":
    run()


