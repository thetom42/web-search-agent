# Implementing a Simple Web Search AI Agent

The task is to build a simple AI agent with Python and Pydantic AI that acts as a Web Search Agent.

Do it step-by-step strictly following the order below.

1. Create a Python virtual environment. The venv should be in a subfolder named '.venv'. Use the uv package manager for that. Always call the uv tool without a path.

2. Activate the virtual environment.

3. Fetch the Pydantic AI documentation bank code example at 'https://ai.pydantic.dev/examples/bank-support' as a code example to understand how to utilize the Pydantic AI framework. If the document is truncated, repeat the fetch with an adapted start_index until you have read the whole document.

4. Fetch the Tavily documentation at 'https://docs.tavily.com/sdk/reference/python' to understand how to implement a Tavily search in Python. If the document is truncated, repeat the fetch with an adapted start_index until you have read the whole document.

5. Implement the agent.py using Tavily for the web search:

- Use the dotenv package for the management of environment variables. Make sure the you load the environment right at the beginning of the Python script. 
- Make use of the decorators that come with the Pydantic AI package to achieve a good level of encapsulation like it is done in the bank-support example.
- Use a class wrapper for Tavily search functionality. Implement the Tavily search using the Tavily Python SDK.
- Implement the printing of the results in a dedicated function instead of putting it into the main function.
- Use the 'openai:gpt-4o-mini' model as the agent's LLM.
- For the search question, ask the user from the command line.

6. Install the needed Python packages.

7. Create all relevant files that are needed to run the project later on:

- a .sample.env for a the API keys we will need,
- a .gitignore,
- a requirements.txt, only the top level packages.

8. Then create a run and debug configuration. As the "type" use "debugpy" instead of "python" for both the run and the debug configuration.

9. Finally write a technical documentation in the README.md. Make sure it contains a section with detailed explanations of the agent.py code.
