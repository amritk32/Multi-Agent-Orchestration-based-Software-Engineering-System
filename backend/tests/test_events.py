import asyncio
import threading

from events import ProjectEventManager


def test_project_events_are_isolated_and_can_be_published_from_threads():
    async def exercise():
        manager = ProjectEventManager()
        queue_a = manager.subscribe("project-a", asyncio.get_running_loop())
        queue_b = manager.subscribe("project-b", asyncio.get_running_loop())

        thread_a = threading.Thread(
            target=manager.publish,
            args=("project-a", {"type": "agent_start", "agent": "requirements"}),
        )
        thread_b = threading.Thread(
            target=manager.publish,
            args=("project-b", {"type": "agent_start", "agent": "architecture"}),
        )
        thread_a.start()
        thread_b.start()
        thread_a.join()
        thread_b.join()

        assert await asyncio.wait_for(queue_a.get(), timeout=1) == {
            "type": "agent_start",
            "agent": "requirements",
        }
        assert await asyncio.wait_for(queue_b.get(), timeout=1) == {
            "type": "agent_start",
            "agent": "architecture",
        }

    asyncio.run(exercise())
