import base64
import streamlit as st
import sys
import time
from crewai import Agent, Task, Crew, Process
from langchain.agents import Tool
import os
import re
from langchain_groq import ChatGroq
from crewai_tools import SerperDevTool
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_community.tools.tavily_search.tool import TavilySearchResults

st.set_page_config(page_title="Recommender", page_icon="🗺️")
groq_api_key = os.environ["GROQ_API_KEY"]
tavily_api_key = os.environ["TAVILY_API_KEY"]
serper_api_key=os.environ["SERPER_API_KEY"]

llm = ChatGroq(api_key=groq_api_key, model="llama3-8b-8192")
search = TavilySearchAPIWrapper(tavily_api_key=tavily_api_key)
tavily_tool = TavilySearchResults(api_wrapper=search)
tool = SerperDevTool(serper_api_key=serper_api_key)
task_values = []

@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("assets/wall6.png")

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
    background-image: url("data:image/png;base64,{img}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

[data-testid="stSidebar"] > div:first-child {{
    background-image: url("data:image/png;base64,{img}");
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

[data-testid="stToolbar"] {{
    right: 2rem;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

def create_crewai_setup(category, budget, num_people, trip_type, month):
    # Define the local city expert agent
    city_insights = Agent(
        role="Local City Expert",
        goal=f"""Provide the BEST insights about the cities of India.
            Important:
                    - Once you know the selected city, provide keenly researched insights of the city.
                    - Research local events, activities, food, transport, and accommodation information.
                    - Keep the information detailed.
                    - Avoid reusing the same input.
                    - Stop searching as soons as you get the results""",
        backstory=f"""A knowledgeable local guide with extensive information 
                     about every city of India, its attractions, customs and always updated 
                     about current events in the city.""",
        verbose=True,
        allow_delegation=True,
        tools=[tool,tavily_tool],
        llm=llm,
    )

    # Define the trip maker expert agent
    Travel_Agent = Agent(
        role="Trip Maker Expert",
        goal=f"""Recommend places in India for planning a trip, considering the category, budget per head, number of people traveling, type of trip and month of visit.
                Category: {category}
                Budget: {budget}
                Number of People: {num_people}
                Type: {trip_type}
                Time: {month}

                Important:
                    - Final output must contain all the detailed key insights of the locations perfect for customs, culture 
                    information, tourist attractions, activities, food.
                    - The final output must contain detailed reasoning why you are recommending those places.
                    - The final output must contain a proper breakdown of expenses.
                    - Avoid reusing the same input.""",
        backstory=f"""Expert at understanding the user's demands like {category}, 
                     {budget}, {num_people}, {trip_type}, {month} and recommending 
                     places in India they must visit. Skilled in recommending with detailed 
                     insights of the place.""",
        verbose=True,
        allow_delegation=True,
        tools=[tool,tavily_tool],
        llm=llm,
    )

    # Define tasks for the local city expert and trip maker expert agents
    task1 = Task(
        description=f"""Research about the recommended place and provide keen insights into the place, 
        including food, costs, accommodation, tourist attractions, transport, and dos and don'ts.
            
                Helpful Tips:
                - To find blog articles and Google results, perform searches on Google such as the following:
                - "Trip to {category} as {trip_type} in India under {budget}"
                
                Important:
                - Do not generate fake information or improper budget breakdown. Only return the information you find. Nothing else!""",
        expected_output="Detailed information of the city.",
        agent=city_insights,
    )

    task2 = Task(
        description=f"""Based on the factors like {category}, 
        in budget of {budget}, number of people traveling are {num_people}, and type of trip {trip_type}, 
        in the month of {month}, use the results from the Local City Expert to compile all the information in a 
        well-formatted manner. The pointers should be detailed.""",
        expected_output="Detailed and clear report of recommendation.",
        agent=Travel_Agent,
        context=[task1],
    )

    # Create and run the crew
    itinerary_crew = Crew(
        agents=[city_insights, Travel_Agent],
        tasks=[task1, task2],
        verbose=2,
        process=Process.sequential,
    )

    crew_result = itinerary_crew.kickoff()
    return crew_result


class StreamToExpander:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []
        self.colors = ['red', 'green', 'blue', 'orange']  # Define a list of colors
        self.color_index = 0  # Initialize color index

    def write(self, data):
        # Filter out ANSI escape codes using a regular expression
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        # Check if the data contains 'task' information
        task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        if task_value:
            st.toast(":robot_face: " + task_value)

        # Check if the text contains the specified phrase and apply color
        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            # Apply different color and switch color index
            self.color_index = (self.color_index + 1) % len(self.colors)  # Increment color index and wrap around if necessary

            cleaned_data = cleaned_data.replace("Entering new CrewAgentExecutor chain", f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]")

        if "Local City Expert" in cleaned_data:
            # Apply different color 
            cleaned_data = cleaned_data.replace("Local City Expert", f":{self.colors[self.color_index]}[Local City Expert]")
        if "Trip Maker Expert" in cleaned_data:
            cleaned_data = cleaned_data.replace("Trip Maker Expert", f":{self.colors[self.color_index]}[Trip Maker Expert]")
        
        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []


def main():
    st.markdown("<h1 style='color: #004aad; text-align: center;'>Recommender</h1>", unsafe_allow_html=True)
    with st.expander("About the Team:"):
        left_co, cent_co,last_co = st.columns(3)
        with cent_co:
            st.image("assets/logo.png")
        st.subheader("Agent 1")
        st.text("""       
        Role = Trip Maker Expert
        Goal = Recommend place in India for planning a trip, considering the category, budget per head, number of people traveling, type of trip and the month of visit.
        Backstory = Expert at understanding the users demand and recommending 
                    the place in  India they must visit.
        Task = Recommend a best place to visit as per demand.""")
        
        st.subheader("Agent 2")
        st.text("""       
        Role = Local City Expert
        Goal = Provide the BEST insights about the cities of India.
        Backstory = A knowledgeable local guide with extensive information 
                     about the every city of India, its attractions, customs and always updated 
                     about current events in city.
        Task = Provide detailed researched content to Trip Maker Expert.""")
      
    categories = ["Mountains", "Beaches", "Heritage", "Pilgrimage", "Road Trip"]
    months = ["January", "February", "March", "April", "May", "June", "July", "August","September","October","November","December"]
    type=["Family","Friends","Couples","Solo"]
    # Create the columns
    col1, col2, col3, col4, col5 = st.columns(5)

    # Add input elements within the columns
    with col1:
        category = st.selectbox("Category:", categories)
    with col2:
        budget = st.number_input('Net Budget:', min_value=3000)
    with col3:
        num_people = st.number_input("Number of People:", min_value=1, step=1)

    
    
    with col4:
        month = st.selectbox("Month :", months)
    with col5:
        trip_type=st.selectbox("Trip Type:", type)


    
    if st.button("Run Analysis"):
        stopwatch_placeholder = st.empty()
        
        # Start the stopwatch
        start_time = time.time()
        with st.expander("Processing!"):
            sys.stdout = StreamToExpander(st)
            with st.spinner("Generating Results"):
                crew_result = create_crewai_setup(category, budget, num_people,trip_type, month)

        end_time = time.time()
        total_time = end_time - start_time
        stopwatch_placeholder.text(f"Total Time Elapsed: {total_time:.2f} seconds")

        st.header("Results:")
        st.markdown(crew_result)


if __name__ == "__main__":
    main()
