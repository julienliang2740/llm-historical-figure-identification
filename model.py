from openai import OpenAI

from dotenv import load_dotenv
import os
import getpass

from pydantic import BaseModel
from typing import Literal, Union, Tuple

load_dotenv()
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")



class KnowByNameFormat(BaseModel):
    recognize: Literal["yes", "no"]
    description: str

class KnowByBio(BaseModel):
    name_guess: str
    reasoning: str



know_by_name_prompt = """
Examine a name that will be provided to you, and tell me whether or not you recognize the individual.
If you do, say yes in the recognize category, and provide a VERY BRIEF description about the person as you know them (maximum 2 sentences, ideally just 1 sentence, containing time era, basic summary, etc.)
If you do not recognize the person, just say no.
"""

know_by_bio_prompt = """
You will be given an anonymized biography/summary of an individual where all the names and times are fake. Identify the name of the person who you think this is, and provide a brief reasoning.
"""

anonymize_biography_prompt = """
Anonymize the biography below. Change all the names of people, places, and more into fake names. Do not have any proper nouns, or even the real geographic names. Also change the year/times to fake times.
Translate into English if the biography given is not in English.
Return only the anonymized biography and nothing else.
"""



def run_api(system_prompt, user_prompt, call_purpose, model="gpt-4o-mini"):
    # for now we only have gpt
    response = ""

    if call_purpose == "know_by_name":
        response = run_gpt(system_prompt, user_prompt, KnowByNameFormat, model)
    elif call_purpose == "know_by_bio":
        response = run_gpt(system_prompt, user_prompt, KnowByBio, model)
    elif call_purpose == "anonymize_biography":
        response = run_gpt_unformatted(system_prompt, user_prompt, model)

    return response

def run_gpt(system_prompt, user_prompt, format, model="gpt-4o-mini", temperature: float = 0):
    open_ai_key = os.environ["OPENAI_API_KEY"]
    client = OpenAI(api_key=open_ai_key)

    response = client.beta.chat.completions.parse(
      model=model,
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
      ],
      temperature=temperature,
      response_format=format
    )

    resp = response.choices[0].message.parsed
    resp_formatted = resp.model_dump() # resp_formatted should be a dict

    return resp_formatted

def run_gpt_unformatted(system_prompt, user_prompt, model="gpt-4o-mini", temperature: float = 0):
    open_ai_key = os.environ["OPENAI_API_KEY"]
    client = OpenAI(api_key=open_ai_key)

    response = client.chat.completions.create(
      model=model,
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
      ],
      temperature=temperature,
    )

    resp = response.choices[0].message.content
    return resp