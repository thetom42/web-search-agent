# Web Search AI Agent

A simple AI agent built with Python and Pydantic AI that acts as a Web Search Agent, leveraging the Tavily search API.

## Features

- Uses Pydantic AI for structured agent development
- Leverages Tavily API for web search capabilities
- Provides formatted search results with summaries
- Command-line interface for search queries
- Detailed logging of agent operations using logfire

## Prerequisites

- Python 3.8+
- [Tavily API key](https://tavily.com/)
- [OpenAI API key](https://platform.openai.com/)

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/web-search-agent.git
cd web-search-agent
```

2. Create and activate a virtual environment:

```bash
uv venv .venv
source .venv/bin/activate
```

3. Install the required packages:

```bash
uv pip install -r requirements.txt
```

4. Set up your environment variables:

```bash
cp .sample.env .env
```

Then edit the `.env` file to add your API keys:

```
TAVILY_API_KEY=your_tavily_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

Run the agent from the command line:

```bash
python agent.py
```

You will be prompted to enter a search query. The agent will then:
1. Use Tavily to search the web for relevant information
2. Process the search results
3. Generate a concise summary
4. Display the formatted results

## Logging and Debugging

The agent uses the `logfire` library to provide detailed logging of its operations, including the exact REST calls to the model and their responses. This helps with debugging and understanding the agent's behavior.

### Log Configuration

Logs are configured to:
- Display in the console
- Include DEBUG level messages for maximum visibility
- Send logs to the Logfire service if a LOGFIRE_TOKEN is provided in the .env file
- Capture full HTTP request and response details, including headers and bodies

### What Gets Logged

The logging captures:
- Agent initialization and execution
- Search queries and results
- Model interactions through pydantic_ai instrumentation
- Tool invocations and their results
- Model usage statistics
- Error conditions
- **Complete HTTP requests to the model API** (new)
- **Complete HTTP responses from the model API** (new)

### HTTP Tracing

The agent now includes detailed HTTP tracing capabilities that capture:
- Full request URLs to the model API
- Request headers and bodies (including the exact prompts sent to the model)
- Response status codes
- Response headers and bodies (including the exact responses from the model)
- Timing information for each request

This provides complete visibility into the exact data being sent to and received from the model API, which is invaluable for debugging and understanding how the agent interacts with the model.

### Agent Execution Details

The enhanced agent execution details display:
- Key output details (query, summary, number of results)
- Information about the agent result object structure
- Model messages and conversation history
- Model usage statistics and token counts
- HTTP trace information

### Agent Execution Details

In addition to standard logging, the agent prints details about the execution after completion. This includes:
- Information about the result object type and structure
- Available attributes on the result object
- Model usage statistics including token counts

This information provides visibility into how the agent is processing the user's query and how the model is being used.

### Customizing Logging

You can customize the logging level using Python's standard logging module:

```python
import logging

# Set to INFO level for less verbose logs
logging.getLogger("logfire").setLevel(logging.INFO)
logging.getLogger("pydantic_ai").setLevel(logging.INFO)

# Or set to DEBUG level for maximum detail
logging.getLogger("logfire").setLevel(logging.DEBUG)
logging.getLogger("pydantic_ai").setLevel(logging.DEBUG)
```

You can also adjust the logfire configuration:

```python
logfire.configure(
    send_to_logfire="if-token-present",  # Or "never" to disable Logfire service
)
```

## Code Explanation

### agent.py

The main file of the project contains the implementation of the Web Search Agent. Here's a breakdown of its components:

#### Environment Setup

```python
import os
import logfire
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logfire for logging with detailed tracing
logfire.configure(
    send_to_logfire="if-token-present",  # Only send logs if LOGFIRE_TOKEN is set
)

# Set logging to debug level
logging.getLogger("logfire").setLevel(logging.DEBUG)
logging.getLogger("pydantic_ai").setLevel(logging.DEBUG)

# Instrument pydantic_ai to enable detailed logging
logfire.instrument_pydantic_ai()
```

The application uses:
- `python-dotenv` to load environment variables from a `.env` file, making it easy to manage API keys and other configuration.
- `logfire` for structured logging, with configuration to display logs in the console and optionally send them to the Logfire service.
- Python's standard `logging` module to set debug level for logfire and pydantic_ai loggers, ensuring maximum visibility.
- `logfire.instrument_pydantic_ai()` to automatically log all Pydantic AI operations, including model requests, responses, and tool usage.

#### Data Models

```python
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
```

Pydantic models are used to define the structure of search results and the agent's response, ensuring type safety and validation.

#### Tavily Search Wrapper

```python
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
```

A wrapper class for the Tavily search functionality, which initializes the Tavily client with an API key and provides a method to perform searches.

#### Agent Definition

```python
@dataclass
class SearchDependencies:
    """Dependencies for the search agent."""
    tavily_client: TavilyClient

search_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=SearchDependencies,
    output_type=SearchResponse,
    system_prompt=(
        "You are a helpful web search assistant. "
        "Your task is to provide relevant search results and a concise summary "
        "based on the user's query. Be informative and accurate."
    ),
)

@search_agent.tool
async def perform_search(ctx: RunContext[SearchDependencies], query: str) -> dict:
    """Perform a web search using Tavily API."""
    logfire.info("Performing web search", query=query)
    search_results = ctx.deps.tavily_client.search(query)
    logfire.info("Search completed", num_results=len(search_results.get("results", [])))
    return search_results
```

The agent is defined using Pydantic AI's `Agent` class, with:
- The `openai:gpt-4o-mini` model as the LLM
- `SearchDependencies` for dependency injection
- `SearchResponse` as the structured output type
- A system prompt that defines the agent's role
- A tool for performing web searches using the Tavily API, with logging before and after the search operation

The `perform_search` tool includes structured logging that captures:
- When a search begins, including the query being searched
- When a search completes, including the number of results found

#### Result Formatting

```python
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
```

A dedicated function for formatting and printing search results, which displays:
- The original query
- A summary of the results
- A list of search results with titles, URLs, and content snippets

#### Main Function

```python
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
    
    # Run the search agent
    logfire.info("Running search agent")
    with logfire.span("agent_execution"):
        result = await search_agent.run(query, deps=deps)
    
    logfire.info("Agent execution completed",
                 num_results=len(result.output.results),
                 usage=result.usage())
    
    # Print the search results
    print_search_results(result.output)
    
    # Print the full agent-model conversation trace
    print_agent_conversation(result)
    
    logfire.info("Web Search Agent completed successfully")
```

The main function:
1. Logs the start of the agent execution
2. Gets the Tavily API key from environment variables, logging an error if not found
3. Initializes the Tavily search client with logging
4. Prompts the user for a search query and logs it
5. Sets up the dependencies for the agent
6. Runs the agent with the query and dependencies within a logging span for timing
7. Logs the completion of the agent execution with result statistics
8. Prints the formatted search results
9. **Prints the agent execution details and model usage statistics** (new step)
10. Logs the successful completion of the agent

The use of `logfire.span("agent_execution")` creates a timed span in the logs, which helps track how long the agent execution takes.

#### Agent Execution Details

```python
def print_agent_conversation(result):
    """Print the agent execution details and model usage statistics."""
    print("\n" + "="*50)
    print("AGENT EXECUTION DETAILS")
    print("="*50)
    
    # Print information about the result
    print(f"\nOutput Type: {type(result).__name__}")
    print(f"Output Content Type: {type(result.output).__name__}")
    
    # Print available attributes
    print("\nAvailable Attributes:")
    for attr in dir(result):
        if not attr.startswith('_') and attr != 'output':
            print(f"  - {attr}")
    
    # Print output details
    print("\n" + "-"*50)
    print("OUTPUT DETAILS:")
    
    try:
        # Print the output attributes
        output = result.output
        print(f"\nQuery: {output.query}")
        print(f"Summary: {output.summary}")
        print(f"Number of results: {len(output.results)}")
    except Exception as e:
        print(f"Error processing output: {e}")
    
    # Print usage statistics
    if hasattr(result, 'usage') and callable(result.usage):
        usage = result.usage()
        print("\n" + "-"*50)
        print("MODEL USAGE STATISTICS:")
        print(f"Request Tokens: {usage.request_tokens}")
        print(f"Response Tokens: {usage.response_tokens}")
        print(f"Total Tokens: {usage.total_tokens}")
```

The `print_agent_conversation` function provides detailed information about the agent execution:

1. It prints the type of the result object and its output
2. It lists all available attributes of the result object for inspection
3. It displays key details from the output, including the query, summary, and number of results
4. It prints usage statistics including token counts for the model interaction

This function gives you visibility into the agent's output structure and model usage statistics, helping you understand how the agent is processing queries and how many tokens are being used.

## Debugging

The project includes VSCode launch configurations for running and debugging the agent. To use them:

1. Open the project in VSCode
2. Go to the Run and Debug panel
3. Select either "Run Web Search Agent" or "Debug Web Search Agent"
4. Press F5 or click the green play button

## License

MIT
