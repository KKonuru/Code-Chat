from langchain_community.tools import WikipediaQueryRun 
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import YouTubeSearchTool 
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, SystemMessage
from main import codeChat
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver


class CodingAgent:
    def __init__(self, codebase:str,temperature:float,rag_temperature:float):
        self._llm = ChatOllama(
            model="llama3-groq-tool-use",
            temperature=temperature
        )
        wiki_api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=250)
        wikipedia = WikipediaQueryRun(description="A tool to explain things in text format. Only use this tool if you think the user would benefit with a ", api_wrapper=wiki_api_wrapper)
        youtube = YouTubeSearchTool(description="A tool to search YouTube videos. Use this tool if you think the user asked about a programming concept that can be better explained with a video.")

        self._tools = [wikipedia,youtube,self._create_rag_tool()]
        system_prompt = SystemMessage(
            """
            You are a highly capable coding assistant designed to help users understand codebases/projects/repositories and answer programming-related questions.

            If you are asked a specific question about code from a codebase or project or respository follow these steps:
            1. Use the RAG tool to get the answer. You already have access to the codebase. Use the full query for the rag tool.
            2. If the RAG tool cannot answer the question, ask for more information.
            3. If the RAG tool can answer the question, return the full response from the RAG tool.

            Else if the question is about a programming concept:
            1. Use the youtube tool to get videos relevant to the question.
             2. If relevant get a wikipedia summary for the question.

            If the question involves both tasks, you must split the query appropriately and send the codebase-related part to the RAG tool and handle the programming-related part separately by providing external resources and explanations.

            Guidelines:
            - NEVER ask the user for clarification about their query.
            - Always use at least one tool for the query.
            - If the user is asking a question about some specific code, use the rag tool to get the answer.

            Here are some examples:
            Human: Can you explain the Counter component and how it uses the props for the functionality?
            AI: tool_calls=[{"name": "rag_tool", "args": {"query": "Can you explain the Counter component and how it uses the props for the functionality?"}, "id": "3"}]
            Tool: 
            ```jsx
                    import React from 'react';

                    const Counter = () => {
                    const [count, setCount] = useState(0);

                    return (
                        <div>
                        <p>You have clicked the button {count} times</p>
                        <button onClick={() => setCount(count + 1)}>Click me</button>
                        </div>
                    );
                    };

                    export default Counter;
                    ```
                    This code defines a `Counter` component that displays a message indicating how many times a button has been clicked. The component uses the `useState` hook to keep track of 
                    the current count, and it updates this state whenever the button is clicked. The component also includes an `onClick` event handler that calls the `setCount` function with the updated count value.
            AI:
                ```jsx
                    import React from 'react';

                    const Counter = () => {
                    const [count, setCount] = useState(0);

                    return (
                        <div>
                        <p>You have clicked the button {count} times</p>
                        <button onClick={() => setCount(count + 1)}>Click me</button>
                        </div>
                    );
                    };

                    export default Counter;
                    ```
                    This code defines a `Counter` component that displays a message indicating how many times a button has been clicked. The component uses the `useState` hook to keep track of 
                    the current count, and it updates this state whenever the button is clicked. The component also includes an `onClick` event handler that calls the `setCount` function with the updated count value.,
            Human: Can you help me understand what React props are and how I can use them?
            AI: tool_calls=[{"name": "youtube_tool", "args": {"query": "React Props"}}, {"name": "youtube_tool", "args": {"query": "Props in React"}}]
            Tool: ['https://www.youtube.com/watch?v=uvEAvxWvwOs&pp=ygULUmVhY3QgcHJvcHM%3D', 'https://www.youtube.com/watch?v=PHaECbrKgs0&pp=ygULUmVhY3QgcHJvcHM%3D']
            AI: Here are some YouTube videos that can help you understand how props work in React:

                1. [React Props](https://www.youtube.com/watch?v=uvEAvxWvwOs&pp=ygULUmVhY3QgcHJvcHM%3D)
                2. [Props in React](https://www.youtube.com/watch?v=PHaECbrKgs0&pp=ygULUmVhY3QgcHJvcHM%3D)

                You can watch these videos to get a better understanding of how props work in React.
            """
            )
        memory = MemorySaver()
        self._agent = create_react_agent(self._llm, self._tools, state_modifier=system_prompt,checkpointer=memory)
        self._code_chat = codeChat(codebase,rag_temperature)
    
    def _create_rag_tool(self):
        """Creates the RAG tool dynamically."""
        @tool
        def rag_tool(query):
            """
            A tool that fetches CodeLlama explanation of the code.
            Use this tool whenever the user asks a question pertaining to a codebase/project/repository.
            """
            stream_obj = self._code_chat.llmResponse(query)
            return "".join(stream_obj)

        return rag_tool

    def changeCodebase(self,codebase:str):
        self._code_chat = codeChat(codebase)

    def query(self, query):
        config = {"configurable": {"thread_id": "abc123"}}
        response = self._agent.invoke({'messages': [HumanMessage(query)]}, config=config)
        
        messages = response["messages"]

        #Find the last AI
        return messages[-1].content
    def getRagApp(self):
        return self._code_chat
    def setAgentTemp(self,temperature:float):
        self._llm.temperature = temperature
    def setCodeLLMTemp(self,temperature:float):
        self._code_chat.adjustTemperature(temperature)


def main():
    agent = CodingAgent()

    while True:
        query = input("Enter your query: ")
        agent.query(query)

if __name__=="__main__":
    main()