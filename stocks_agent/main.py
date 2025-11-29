from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

import yfinance as yf
from common import consts, runner
import asyncio
import uuid
from dotenv import load_dotenv

load_dotenv()

initial_state = {
    "user_name": "Harish",
    "user_preferences": """
        I like to invest in various stocks.
        My top 3 favourite tickers to invest are GOOG, NFLX and NVDA  
    """,
}


def get_stock_price(ticker: str) -> dict:
    """
    Identify the potential companies or tickers from the users input. 
    For each ticker or company fetch the current stock price for a given ticker symbol.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        float: The current stock price.
    """
    stock = yf.Ticker(ticker=ticker)
    price = stock.info.get("currentPrice", "Price not available")
    return {"price": price, "ticker": ticker}


def create_stocks_agent():
    return Agent(
        model=LiteLlm(model=consts.MODEL_ID),
        name="stocks_agent",
        description="A helpful agent that gets stock price.",
        instruction="""
        You are a stock price assistant. You find the stock price. 
        Always return the ticker symbol in your response.

        Here is some iformation about the user:
        Name: 
        {user_name}
        Preferences: 
        {user_preferences}
        """,
        tools=[get_stock_price],
    )


async def run_stocks_agent(query="Stock price of apple"):
    user_id = "Harish"
    session_id = str(uuid.uuid4())
    
    socks_agent = create_stocks_agent()
    session_service = await runner.get_new_session_service()
    
    session = await session_service.create_session(
        app_name=socks_agent.name,
        user_id=user_id,
        session_id=session_id,
        state=initial_state,
    )
    print(f"Query: {query}")
    await runner.run_agent_query(
        agent=socks_agent, query=query, user_id=user_id, session_id=session.id, session_service=session_service
    )


async def main():
    await run_stocks_agent("Hey. How are my favourite stocks doing today?")


if __name__ == "__main__":
    asyncio.run(main())
