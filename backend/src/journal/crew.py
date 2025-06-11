# src/latest_ai_development/crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class Journal():
  """Journal crew"""

  agents: List[BaseAgent]
  tasks: List[Task]
  
  @agent
  def birthday_identifier(self) -> Agent:
    return Agent(
      config=self.agents_config['birthday_identifier'], 
      verbose=True,
      tools=[SerperDevTool()]
    )

  @agent
  def birthday_extractor(self) -> Agent:
    return Agent(
      config=self.agents_config['birthday_extractor'], 
      verbose=True
    )

  @agent
  def gift_suggestor(self) -> Agent:
    return Agent(
      config=self.agents_config['gift_suggestor'], 
      verbose=True
    )

  @task
  def birthday_identifier_task(self) -> Task:
    return Task(
      config=self.tasks_config['birthday_identifier_task']
    )
  
  @task
  def birthday_extraction_task(self) -> Task:
    return Task(
      config=self.tasks_config['birthday_extraction_task'],
      output_file='output/birthday_extraction.json'
    )

  @task
  def gift_suggestion_task(self) -> Task:
    return Task(
      config=self.tasks_config['gift_suggestion_task'],
      output_file='output/gift_suggestion.json'
    )

  @crew
  def crew(self) -> Crew:
    """Creates the Birthday Processing crew"""
    return Crew(
      agents=self.agents, # Automatically created by the @agent decorator
      tasks=self.tasks, # Automatically created by the @task decorator
      process=Process.sequential,
      verbose=True,
    )

journa_service = Journal()