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
from langchain_openai import ChatOpenAI, AzureChatOpenAI
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
    You don't have to answer without tool call. if you don't have the information, you should say so.

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

    # Azure OpenAI configuration based on your curl request
    # Your endpoint: https://home-openai-v1.openai.azure.com/openai/v1//chat/completions
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://home-openai-v1.openai.azure.com")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # Since your endpoint uses /openai/v1//chat/completions format (not standard Azure deployments path),
    # we'll use ChatOpenAI with custom base_url to match your curl request
    base_url = f"{azure_endpoint}/openai/v1"
    
    llm = ChatOpenAI(
        model=azure_deployment,
        openai_api_key=azure_api_key,
        openai_api_base=base_url,
        temperature=0,
    )
    
    agent = {"input" : lambda x: x["input"]} | prompt | llm | ReActSingleInputOutputParser()
    
    result = agent.invoke({"input": 'What is the length of the text "Hello, world!"?'})
    print("Final Result:", result)

