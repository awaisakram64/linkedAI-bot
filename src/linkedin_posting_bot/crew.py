# Warning control
import warnings
warnings.filterwarnings('ignore')

# Importing necessary libraries
import os
import yaml
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

from crewai import Agent, Task, Crew
from crewai_tools import DallETool

# Define CrewAI tool configurations
os.environ['OPENAI_MODEL_NAME'] = 'gpt-4o'
hugging_face_model = "huggingface/stabilityai/stable-diffusion-3.5-large-turbo"

# Define file paths for YAML configurations
files = {
    'agents': 'src/linkedin_posting_bot/config/agents.yaml',
    'tasks': 'src/linkedin_posting_bot/config/tasks.yaml',
}

# Load configurations from YAML files
configs = {}
for config_type, file_path in files.items():
    with open(file_path, 'r') as file:
        configs[config_type] = yaml.safe_load(file)

agents_config = configs['agents']
tasks_config = configs['tasks']

class SocialMediaPost(BaseModel):
    headline: str = Field(..., description="Headline of the news generated for the Linkedin post")
    summary: str = Field(..., description="Summary of the news extracted from source links")
    image_url: HttpUrl
    image_summary: str = Field(..., description="summary of the image generated")


# DALL-E Tool for image generation
dalle_tool = DallETool(
    model="dall-e-3",
    size="1024x1024",
    quality="standard",
    n=1
)

# Create Agents
market_news_monitor_agent = Agent(
    config=agents_config['market_news_monitor_agent'],
    verbose=False
)

quality_assurance_agent = Agent(
    config=agents_config['quality_assurance_agent']
)

content_creator_agent = Agent(
    config=agents_config['content_creator_agent']
)

content_creator_graphic_agent = Agent(
    config=agents_config['content_creator_graphic_agent'],
    tools=[dalle_tool],
)

# Create Tasks
news_research_task = Task(
    config=tasks_config['news_research_task'],
    agent=market_news_monitor_agent
)

news_filter_task = Task(
    config=tasks_config['news_filter_task'],
    agent=quality_assurance_agent
)

post_generator_task = Task(
    config=tasks_config['post_generator_task'],
    agent=content_creator_agent,
    context=[news_research_task, news_filter_task],
)

image_generator_task = Task(
    config=tasks_config['image_generator_task'],
    agent=content_creator_graphic_agent,
    context=[post_generator_task],
    output_json=SocialMediaPost
)

# Create Crew
linkedin_posting_crew = Crew(
    agents=[
        market_news_monitor_agent,
        quality_assurance_agent,
        content_creator_agent,
        content_creator_graphic_agent,
    ],
    tasks=[
        news_research_task,
        news_filter_task,
        post_generator_task,
        image_generator_task
    ],
    verbose=True,
)