import asyncio
from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage
from graph.graph import graph


async def main():
    messages = []
    print("Marketing Agent CLI (type 'quit' to exit)\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() in ("quit", "exit"):
            break

        messages.append(HumanMessage(content=user_input))
        result = await graph.ainvoke({"messages": messages})
        messages = result["messages"]

        print(f"\nAgent: {messages[-1].content}\n")


if __name__ == "__main__":
    asyncio.run(main())
