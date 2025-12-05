from dotenv import load_dotenv
import os

# Initialize Phoenix instrumentation FIRST, before other imports
import phoenix as px
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor

LangChainInstrumentor().instrument()

tracer_provider = register(
    project_name="react-agent",
    endpoint="http://localhost:6006/v1/traces",
)

from langchain_core.prompts import PromptTemplate
from langchain_core.tools import render_text_description, tool
from langchain_openai import ChatOpenAI
from langchain_classic.agents.output_parsers import ReActSingleInputOutputParser

load_dotenv()

@tool
def get_text_length(text: str) -> int:
    """Returns the length of a text by characters"""
    print(f"get_text_length enter with {text=}")
    text = text.strip("'\n").strip(
        '"'
    )  # stripping away non alphabetic characters just in case

    return len(text)



if __name__ == "__main__":
    print("Hello ReAct LangChain!")
    tools = [get_text_length]

    template = """
    Answer the following questions as best you can. You have access to the following tools:

    {tools}
    
    Use the following format:
    
    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question
    
    Begin!
    
    Question: {input}
    Thought:
    """

    prompt = PromptTemplate.from_template(template=template).partial(
        tools=render_text_description(tools),
        tool_names=", ".join([t.name for t in tools]),
    )

    llm = ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "qwen/qwen3-235b-a22b:free"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        temperature=0,
    )
    
    agent = {"input" : lambda x: x["input"]} | prompt | llm | ReActSingleInputOutputParser()
    
    result = agent.invoke({"input": 'What is the length of the text "Hello, world!"?'})
    print("Final Result:", result)