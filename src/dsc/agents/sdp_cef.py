from agent_framework import Agent, InMemoryHistoryProvider
from agent_framework.openai import OpenAIChatClient

from dsc.constants.common import PROJECT_ROOT
from dsc.prompts.utils import build_prompt_from_template
from dsc.strategies.compaction import compaction_strategy
from dsc.utils.common import read_yaml

config_system_prompt = read_yaml(PROJECT_ROOT / "config/system_prompt.yaml")
system_prompt = build_prompt_from_template(config_system_prompt)

def get_sdp_cef_agent(client: OpenAIChatClient):
    """
    """
    agente = Agent(
        client=client,
        name="BancoCuyDeOroAsesorSdP",
        instructions=system_prompt,
        default_options={
            "store": False
        },
        context_providers=[
            InMemoryHistoryProvider(
                "historial",
                load_messages=True
            )
        ],
        compaction_strategy=compaction_strategy,
    )

    return agente
