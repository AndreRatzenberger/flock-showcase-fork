import asyncio
from datetime import timedelta

from flock.core import Flock, FlockFactory
from flock.routers.default.default_router import DefaultRouterConfig
from flock.workflow.temporal_config import (
    TemporalActivityConfig,
    TemporalRetryPolicyConfig,
    TemporalWorkflowConfig,
)


async def main():
 
    # --------------------------------
    # Create the flock with Temporal config
    # --------------------------------
    # Set global Temporal parameters
    # In this case, we're setting the task queue to "flock-test-queue"
    # and the workflow execution timeout to 10 minutes
    # and the default activity retry policy to 2 attempts
    flock = Flock(
        enable_temporal=True,
        temporal_config=TemporalWorkflowConfig(
            task_queue="flock-test-queue",
            workflow_execution_timeout=timedelta(minutes=10),
            default_activity_retry_policy=TemporalRetryPolicyConfig(
                maximum_attempts=2
            ),
        ),
    )

    # --------------------------------
    # Create a normal agent
    # --------------------------------
    agent = FlockFactory.create_default_agent(
        name="my_presentation_agent",
        input="topic",
        output="funny_title, funny_slide_headers",
    )

    flock.add_agent(agent)

   
    # --------------------------------
    # Create a Temporal ready agent
    # --------------------------------
    # This agent is ready to be used with Temporal
    # It has a Temporal activity config that sets the start to close timeout to 1 minute
    # and the retry policy to 4 attempts
    # and the non retryable error types to "ValueError"
    content_agent = FlockFactory.create_default_agent(
        name="content_agent",
        input="funny_title, funny_slide_headers",
        output="funny_slide_content",
        temporal_activity_config=TemporalActivityConfig(
            start_to_close_timeout=timedelta(minutes=1),
            retry_policy=TemporalRetryPolicyConfig(
                maximum_attempts=4,
                initial_interval=timedelta(seconds=2),
                non_retryable_error_types=["ValueError"],
            ),
        ),
    )

    flock.add_agent(content_agent)

    # --------------------------------
    # Add the agent to the router
    # --------------------------------
    # This is the router that will be used to route the my_presentation_agent to the content agent
    agent.add_component(DefaultRouterConfig(hand_off="content_agent"))

    print(
        f"Starting Flock run on Temporal task queue: {flock.temporal_config.task_queue}"
    )

    # --------------------------------
    # Run the flock
    # --------------------------------
    # This is the main function that will be used to run the flock
    result = await flock.run_async(
        start_agent="my_presentation_agent",
        input={
            "topic": "A presentation about how good of an idea it is to combine ai agents with temporal.io"
        },
    )

    print("\n--- Result ---")
    print(result)


if __name__ == "__main__":
    print(
        "Ensure a Temporal worker is running and listening on the specified task queue(s)."
    )
    asyncio.run(main())
