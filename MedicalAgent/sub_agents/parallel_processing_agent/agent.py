from google.adk.agents import ParallelAgent
from .parallel_steps.AssessmentPlanner.agent import AssessmentPlanner
from .parallel_steps.Critic.agent import Critic
from .parallel_steps.Summariser.agent import Summariser
from .parallel_steps.medical_template_agent.agent import medical_template_agent



parallel_processing_agent = ParallelAgent(
    name="parallel_processing_agent",
    sub_agents=[medical_template_agent, AssessmentPlanner, Critic, Summariser],
    description="This agent orchestrates the parallel processing of medical template generation, assessment plan generation, " \
    "critic feedback generation, and summary generation using specialized sub-agents and ensures all the agents have executed their tasks.",   
)