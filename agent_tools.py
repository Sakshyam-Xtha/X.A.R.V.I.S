import os
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()

@tool
def web_search(query: str)-> str:
    """
    Search the internet for real-time information, news, and technical documentation.
    Use this when the user asks about current events or specific tech updates.
    """    
    return search_tool.run(query)