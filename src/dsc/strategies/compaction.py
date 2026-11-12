import os

from agent_framework import (
    CharacterEstimatorTokenizer,
    SummarizationStrategy,
    TokenBudgetComposedStrategy,
    TruncationStrategy,
)
from agent_framework.openai import OpenAIChatClient
from azure.identity import DefaultAzureCredential

from dsc.constants.common import PROJECT_ROOT
from dsc.constants.plantillas import PL_SUMMARIZE_PROMPT
from dsc.prompts.utils import build_prompt_from_template
from dsc.utils.common import read_yaml

summarizer_client = OpenAIChatClient(
    model=os.getenv("FOUNDRY_MODEL_DEPLOYMENT"),
    base_url=os.getenv("FOUNDRY_MODEL_ENDPOINT"),
    credential=DefaultAzureCredential(),
)
tokenizer = CharacterEstimatorTokenizer()

config_summarize_prompt = read_yaml(PROJECT_ROOT / "config/summarize_prompt.yaml")
summarize_prompt = build_prompt_from_template(config_summarize_prompt, plantilla=PL_SUMMARIZE_PROMPT)

compaction_strategy = TokenBudgetComposedStrategy(
    token_budget=1000,
    tokenizer=tokenizer,
    strategies=[
        # Etapa 1: resumir la conversación antigua conservando datos financieros
        SummarizationStrategy(
            client=summarizer_client,
            target_count=4,
            threshold=2,
            prompt=summarize_prompt,
        ),

        # Etapa 2 (respaldo): eliminar grupos antiguos si aún se excede el presupuesto
        TruncationStrategy(
            max_n=1200,
            compact_to=1000,
            tokenizer=tokenizer,
        ),
    ],
    early_stop=True,  # detenerse en cuanto el historial entre en el presupuesto
)
