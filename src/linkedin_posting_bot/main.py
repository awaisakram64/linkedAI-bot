#!/usr/bin/env python
import sys
import warnings
from src.linkedin_posting_bot.crew import linkedin_posting_crew
from src.linkedin_posting_bot.tools.refresh_token import refresh_linkedin_token
from src.linkedin_posting_bot.tools.linkedin_post import Posts
import os
import json

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# os.environ['LINKEDIN_CREDS']


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def post_engine(author_id, is_page, emojies, state):
    
    ai_gen_post_result = run(emojies)
    linkedin_create_post_callable(ai_gen_post_result, author_id, is_page,lifecycleState=state)

def run(emojies):
    """
    Run the crew.
    """
    from src.linkedin_posting_bot.crew_v1 import LinkedinPostingBot
    links = "TechCrunch (https://techcrunch.com), VentureBeat (https://venturebeat.com), Wired (https://www.wired.com), Ars Technica (https://arstechnica.com), The Verge (https://www.theverge.com), CNET (https://www.cnet.com), Engadget (https://www.engadget.com), Mashable (https://mashable.com), Gizmodo (https://gizmodo.com), Towards Data Science (https://towardsdatascience.com), KDnuggets (https://www.kdnuggets.com), Analytics Vidhya (https://www.analyticsvidhya.com), Data Science Central (https://www.datasciencecentral.com), The Gradient (https://thegradient.pub), DeepMind Blog (https://www.deepmind.com/blog), OpenAI Blog (https://openai.com/blog), AI Weekly (https://aiweekly.co), Data Science Dojo (https://datasciencedojo.com), Towards AI (https://www.towardsai.net), Bloomberg (https://www.bloomberg.com), Reuters (https://www.reuters.com), Forbes (https://www.forbes.com), Business Insider (https://www.businessinsider.com), Financial Times (https://www.ft.com), Wall Street Journal (https://www.wsj.com), Nature (https://www.nature.com), Science (https://www.sciencemag.org), PLOS ONE (https://journals.plos.org/plosone/), arXiv (https://arxiv.org), MIT Technology Review (https://www.technologyreview.com), European Data Portal (https://data.europa.eu), United Nations Data (https://data.un.org), World Bank Open Data (https://data.worldbank.org)"
    hashtags = "includes hashtags"
    emojies = "includes emojies" if emojies == 'true' else ""
    
    input = {
        "sources_links": links,
        "hashtags": hashtags,
        "emojies": emojies
    }
    
    # Trigger Crew with inputs
    result = linkedin_posting_crew.kickoff(inputs=input)
    post_result_dict = json.loads(result.json)
    return post_result_dict

def linkedin_create_post_callable(post_result_dict, author_id, is_page,lifecycleState="DRAFT"):
    
    token = access_token_callable()
    
    # Example for posting on personal profile
    person_id = author_id
    post_headline = post_result_dict.get('headline')
    post_summary = post_result_dict.get('summary')
    post_image_url = post_result_dict.get('image_url')
    
    personal_post = Posts(
        author_id=person_id, post_text=post_summary, media_url=post_image_url,
        media_title="AI generated Image", token=token,post_headline=post_headline, lifecycleState=lifecycleState,
        is_page=is_page
    )
    
    personal_post.create_post()
    
    return "post created!!"

def access_token_callable():
    linkedin_token = json.loads(os.environ['LINKEDIN_CREDS'])
    
    token_response = refresh_linkedin_token(linkedin_token)
    
    if token_response:
        print("Token Refresh Successful:")
        print(f"Expires In: {token_response.get('expires_in')} seconds")
    
    token = token_response.get('access_token')
    return token
    

    



# def train():
#     """
#     Train the crew for a given number of iterations.
#     """
#     inputs = {
#         "topic": "AI LLMs"
#     }
#     try:
#         LinkedinPostingBot().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while training the crew: {e}")

# def replay():
#     """
#     Replay the crew execution from a specific task.
#     """
#     try:
#         LinkedinPostingBot().crew().replay(task_id=sys.argv[1])

#     except Exception as e:
#         raise Exception(f"An error occurred while replaying the crew: {e}")

# def test():
#     """
#     Test the crew execution and returns the results.
#     """
#     inputs = {
#         "topic": "AI LLMs"
#     }
#     try:
#         LinkedinPostingBot().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while replaying the crew: {e}")
