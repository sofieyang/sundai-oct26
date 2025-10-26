import sys
import os

from google.adk.agents import SequentialAgent
from .sub_agents.lead_finder_agent.agent import agent as lead_finder_agent
from .sub_agents.email_drafter_agent.agent import agent as email_drafter_agent

agent = SequentialAgent(
    name="chief_marketing_agent",
    description="Chief Marketing Agent coordinating lead finding and email drafting.",
    sub_agents=[lead_finder_agent, email_drafter_agent]
)

root_agent = agent

# if __name__ == "__main__":
#     test_company_url = "https://www.examplepharma.com"
#     result = agent.run({"company_url": test_company_url})
#     print(result)