from google.adk.agents import SequentialAgent
from .sequence_steps.MedicalTemplate.agent import MedicalTemplate
from .sequence_steps.TemplateValidator.agent import TemplateValidator

medical_template_agent = SequentialAgent(
    name="medical_template_agent",
    sub_agents=[MedicalTemplate, TemplateValidator],
    description="Executes a sequence of Medical Template Population and Validation of the populated template.",   
)
