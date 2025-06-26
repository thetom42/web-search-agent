import os
from dataclasses import dataclass
from typing import List, Optional
import json
import logging
import logfire
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from tavily import TavilyClient
from pydantic_ai import Agent, RunContext, capture_run_messages

# Configure logfire for logging (without requiring authentication)
logfire.configure(send_to_logfire=False)

# Set logging to debug level
logging.getLogger("pydantic_ai").setLevel(logging.DEBUG)

# Enable Pydantic AI instrumentation - this is the key for logging model calls
logfire.instrument_pydantic_ai()

# Load environment variables from .env file
load_dotenv()

# Define models for structured data
class SearchResult(BaseModel):
    """A single search result from Tavily."""
    title: str = Field(description="The title of the search result")
    url: str = Field(description="The URL of the search result")
    content: str = Field(description="A snippet of content from the search result")

class SearchResponse(BaseModel):
    """The structured response from our search agent."""
    query: str = Field(description="The original search query")
    summary: str = Field(description="A concise summary of the search results")
    results: List[SearchResult] = Field(description="List of search results")

@dataclass
class SearchDependencies:
    """Dependencies for the search agent."""
    tavily_client: TavilyClient

# Create a wrapper class for Tavily search functionality
class TavilySearch:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the TavilySearch with an API key."""
        if api_key is None:
            api_key = os.getenv("TAVILY_API_KEY")
            if not api_key:
                raise ValueError("TAVILY_API_KEY environment variable is not set")
        
        self.client = TavilyClient(api_key=api_key)
    
    def search(self, query: str):
        """Perform a search using the Tavily API."""
        return self.client.search(query)

# Initialize the search agent with instrumentation enabled
search_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=SearchDependencies,
    output_type=SearchResponse,
    system_prompt=(
        "You are a helpful web search assistant. "
        "Your task is to provide relevant search results and a concise summary "
        "based on the user's query. Be informative and accurate."
    ),
    instrument=True,  # Enable instrumentation to log model calls
)

@search_agent.tool
async def perform_search(ctx: RunContext[SearchDependencies], query: str) -> dict:
    """Perform a web search using Tavily API."""
    logfire.info("Performing web search", query=query)
    search_results = ctx.deps.tavily_client.search(query)
    logfire.info("Search completed", num_results=len(search_results.get("results", [])))
    return search_results

def print_search_results(response: SearchResponse):
    """Print the search results in a formatted way."""
    print("\n" + "="*50)
    print(f"SEARCH QUERY: {response.query}")
    print("="*50)
    print(f"\nSUMMARY:\n{response.summary}\n")
    print("-"*50)
    print("SEARCH RESULTS:")
    print("-"*50)
    
    for i, result in enumerate(response.results, 1):
        print(f"{i}. {result.title}")
        print(f"   URL: {result.url}")
        print(f"   {result.content[:200]}...")
        print()

def print_model_messages(captured_messages):
    """Print the captured model messages in a simplified way."""
    print("\n" + "="*50)
    print("MODEL API CALLS")
    print("="*50)
    
    for i, msg in enumerate(captured_messages):
        # Print ModelRequest objects
        if type(msg).__name__ == 'ModelRequest':
            print(f"\n[{i+1}] MODEL REQUEST:")
            
            # Print parts (system prompt, user prompt, etc.)
            if hasattr(msg, 'parts'):
                print(f"Parts count: {len(msg.parts)}")
                for j, part in enumerate(msg.parts):
                    print(f"  Part {j+1} Type: {type(part).__name__}")
                    if hasattr(part, 'content') and part.content:
                        content_str = str(part.content)
                        print(f"  Content: {content_str[:200]}..." if len(content_str) > 200 else f"  Content: {content_str}")
                    if hasattr(part, 'tool_name'):
                        print(f"  Tool Name: {part.tool_name}")
            
            # Print the full JSON for ModelRequest
            if hasattr(msg, '__dict__'):
                try:
                    print("\nFull Request JSON:")
                    print(json.dumps(msg.__dict__, indent=2, default=str))
                except Exception as e:
                    print(f"Error serializing ModelRequest: {e}")
        
        # Print ModelResponse objects
        elif type(msg).__name__ == 'ModelResponse':
            print(f"\n[{i+1}] MODEL RESPONSE:")
            if hasattr(msg, 'model_name'):
                print(f"Model: {msg.model_name}")
            if hasattr(msg, 'usage'):
                print(f"Usage: {msg.usage}")
            
            # Print parts (tool calls, text responses, etc.)
            if hasattr(msg, 'parts'):
                print(f"Parts count: {len(msg.parts)}")
                for j, part in enumerate(msg.parts):
                    print(f"  Part {j+1} Type: {type(part).__name__}")
                    if hasattr(part, 'tool_name'):
                        print(f"  Tool Name: {part.tool_name}")
                    if hasattr(part, 'args') and part.args:
                        print(f"  Args: {part.args}")
            
            # Print the full JSON for ModelResponse
            if hasattr(msg, '__dict__'):
                try:
                    print("\nFull Response JSON:")
                    print(json.dumps(msg.__dict__, indent=2, default=str))
                except Exception as e:
                    print(f"Error serializing ModelResponse: {e}")

async def main():
    logfire.info("Starting Web Search Agent")
    
    # Get API key from environment
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        logfire.error("TAVILY_API_KEY environment variable is not set")
        raise ValueError("TAVILY_API_KEY environment variable is not set")
    
    # Initialize Tavily client
    logfire.info("Initializing Tavily client")
    tavily_search = TavilySearch(tavily_api_key)
    
    # Get search query from user
    query = input("Enter your search question: ")
    logfire.info("Received search query", query=query)
    
    # Set up dependencies
    deps = SearchDependencies(tavily_client=tavily_search.client)
    
    # Run the search agent with message capture
    logfire.info("Running search agent")
    captured_messages = []
    with capture_run_messages() as messages:
        result = await search_agent.run(query, deps=deps)
        captured_messages = messages
    
    logfire.info("Agent execution completed",
                 num_results=len(result.output.results),
                 usage=result.usage())
    
    # Print the search results
    print_search_results(result.output)
    
    # Print the model messages
    print_model_messages(captured_messages)
    
    logfire.info("Web Search Agent completed successfully")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())