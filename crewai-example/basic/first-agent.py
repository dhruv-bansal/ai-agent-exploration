import os

from crewai import Crew, Agent, Task
from dotenv import load_dotenv


def test_get_pid():
    pid = os.getpid()
    print(pid)


info_agent = Agent(
    role= "Information Agent",
    goal= "Give compelling information about a certain topic",
    backstory= """
    You love to know information.
    People love and hate you for the same.
    You win most of the quizzes at your local pub"""
)

task = Task (
    description= "Tell me all about the blue-ringed octopus",
    expected_output="Give me quick summary and then 3 bullet points",
    agent=info_agent
)

crew = Crew(
    agents=[info_agent],
    tasks=[task],
    verbose=1
)

if __name__ == "__main__":
    load_dotenv()
    test_get_pid()
    result = crew.kickoff()

    print(result)