from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService, BaseSessionService
from google.adk.sessions.database_session_service import DatabaseSessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part
from . import utils


async def get_new_session_service(persistent=False):
    if not persistent:
        return InMemorySessionService()
    else:
        db_url = "sqlite+aiosqlite:///./my_agent_data.db"
        return DatabaseSessionService(db_url=db_url)


async def __run_agent(
    runner: Runner, prompt: str, user_id: str, session_id: str, state_displayer=None
) -> str:
    if state_displayer:
        await state_displayer(
            runner.session_service,
            runner.app_name,
            user_id,
            session_id,
            "State BEFORE processing",
        )

    final_response = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=Content(parts=[Part(text=prompt)], role="user"),
        ):
            await utils.process_agent_response(event)

            if event.is_final_response():
                final_response = event.content.parts[0].text
    except Exception as e:
        final_response = f"An error occured: {e}"

    print("\n" + "-" * 50)
    print("✅ Final Response:")
    print(final_response)
    print("-" * 50 + "\n")

    # Display state after processing the message
    if state_displayer:
        await state_displayer(
            runner.session_service,
            runner.app_name,
            user_id,
            session_id,
            "State AFTER processing",
        )

    return final_response


async def run_agent_query(
    agent: Agent,
    query: str,
    session_id: str,
    user_id: str,
    session_service: BaseSessionService,
):
    """Initializes a runner and executes a query for a given agent and session."""
    print(f"\n🚀 Running query for agent: '{agent.name}' in session: '{session_id}'...")
    runner = Runner(agent=agent, session_service=session_service, app_name=agent.name)
    return await __run_agent(
        session_id=session_id, prompt=query, user_id=user_id, runner=runner
    )


async def run_agent_interactive(
    agent: Agent, session_id: str, user_id: str, session_service: BaseSessionService
):
    """Initializes a runner and starts an interactive chat for a given agent and session."""
    print(f"\n🚀 Running: '{agent.name}' interactively in session: '{session_id}'...")
    runner = Runner(agent=agent, session_service=session_service, app_name=agent.name)

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Ending conversation. Your data has been saved to the database.")
            break

        await __run_agent(
            session_id=session_id,
            prompt=user_input,
            user_id=user_id,
            runner=runner,
        )
