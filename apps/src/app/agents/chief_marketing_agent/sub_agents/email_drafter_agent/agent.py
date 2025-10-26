from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
import os

from .settings import DESCRIPTION, INSTRUCTION

agent = LlmAgent(
    model= LiteLlm(model="claude-3-7-sonnet-20250219"),
    name="email_drafter_agent",
    description=DESCRIPTION,
    instruction=INSTRUCTION,
)