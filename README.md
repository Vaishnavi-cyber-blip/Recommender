# Recommender - Trip Bharat App
The Recommender feature of the Trip Bharat App leverages advanced AI capabilities to provide tailored travel recommendations for users planning trips in India. By combining tools like CrewAI and Groq, this module generates detailed itineraries and city insights based on user inputs such as budget, trip type, and month of travel. The feature is designed to deliver accurate and well-researched travel plans using a collaboration of AI-powered agents.

## Key Features
### AI-powered Agents:
  - Trip Maker Expert:
    - Role: Recommends destinations in India based on user preferences.
    - Goal: Tailor trip suggestions considering budget, group size, trip type, and time of year.
    - Task: Provide a well-reasoned breakdown of costs, cultural insights, and activity suggestions.

  - Local City Expert
      - Role: Offers detailed insights into Indian cities.
      - Goal: Research and compile local attractions, food, transport, and events.
      - Task: Supply information to support the Trip Maker Expert's recommendations.

### Customizable Travel Planning:
  - Users can specify:
      - Category: Mountains, Beaches, Heritage, Pilgrimage, or Road Trip.
      - Budget: Define the total budget for the trip.
      - Group Size: Number of people traveling.
      - Trip Type: Family, Friends, Couples, or Solo.
      - Month: Select the intended month of travel.

### Background Processing:
  - Displays a dynamic progress view during recommendation generation.
  - Captures real-time updates and provides total time elapsed.

### Detailed Results:
- Generates a comprehensive report that includes:
    - Location-specific recommendations.
    - Insights into local culture, food, and transportation.
    - Cost breakdown for the entire trip.

## Technologies Used
- Streamlit: User interface for receiving inputs and displaying results.
- Groq API: Utilizes the Llama3 model for language understanding and generation.
- CrewAI Framework: Defines collaborative agents and their respective tasks.
- LangChain Tools:
    - SerperDevTool: For Google-based search queries.
    - TavilySearchAPIWrapper: For retrieving detailed search results.

- Python Libraries:
  - base64: For encoding background images.
  - os: For handling environment variables.
  - time and sys: For processing tasks and timers.
  - re: For text processing in logs.

 ## How It Works
 1. User Input: Enter trip preferences, including category, budget, group size, month, and type.
 2. Agent Execution:
      - The Local City Expert gathers city-specific insights.
      - The Trip Maker Expert compiles detailed travel recommendations based on inputs and the           expert's findings.
3. Results:
  Receive an in-depth, formatted travel recommendation, including activities, expenses, and tips.

## Interface 
  
  ![Screenshot 2024-07-30 211909](https://github.com/user-attachments/assets/08cfbc3e-f94d-4fb3-9977-a3371748292b)


