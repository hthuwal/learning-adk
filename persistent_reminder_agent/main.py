from .memory_agent.agent import memory_agent
from common import runner
import asyncio
from dotenv import load_dotenv

load_dotenv()

initial_state = {
    "user_name": "Harish",
    "reminders": [],
}


async def main():
    user_id = "Harish"
    APP_NAME = memory_agent.name
    session_id = None
    session_service = await runner.get_new_session_service(persistent=True)

    existing_session = await session_service.list_sessions(
        app_name=APP_NAME,
        user_id=user_id,
    )

    if existing_session and len(existing_session.sessions) > 0:
        session_id = existing_session.sessions[0].id
        print(f"Harish - Found existing session id: {session_id}")
    else:
        new_sssion = await session_service.create_session(
            app_name=APP_NAME, user_id=user_id, state=initial_state
        )
        session_id = new_sssion.id
        print(f"Created new Session: {session_id}")

    await runner.run_agent_interactive(
        agent=memory_agent,
        session_id=session_id,
        user_id=user_id,
        session_service=session_service,
    )


if __name__ == "__main__":
    asyncio.run(main())
