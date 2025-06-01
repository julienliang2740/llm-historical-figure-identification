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



know_by_name_system_prompt = """
You will be shown a single personal name.

YOUR TASK
Decide whether you recognize the individual and respond in the **exact** two-line format below.

RULES
1. Draw only on general knowledge—do not invent facts or use external tools.
2. If the name is familiar, write one concise sentence (≤ 25 words) giving era & core claim to fame.
3. If the name is unfamiliar or too ambiguous, say “no” and leave the description blank.

OUTPUT:
recognized: <yes|no>
description: <one-sentence summary OR blank>
"""

know_by_bio_system_prompt = """
You are a historical detective.  
You will receive an anonymized life summary in which **all proper nouns—names, dynasties, places, calendars, and titles—have been replaced with invented ones**.  
Your job is to infer the most likely real historical figure being described, using only the sequence of events, roles, accomplishments, and relationships.

GUIDELINES
1. **Ignore every fabricated name or date.** They contain no information.
2. Rely on distinctive patterns—office held, key battles, writings, inventions, family ties, manner of death, etc.
3. If more than one figure fits, pick the single most probable. If you are truly unsure, answer “Uncertain”.
4. Keep your explanation brief (≤ 75 words).

OUTPUT:
Guess: <real name or “Uncertain”>  
Reason: <concise justification>
"""

anonymize_biography_system_prompt = """
You are an industrial-grade anonymizer.
Your mission: turn any historical or biographical passage into a version with
• NO real proper nouns,
• NO real numerals or calendar labels,
• NO geographic references that exist,
while preserving the causal order of events.
You must obey every rule that follows exactly.
"""

anonymize_biography_user_prompt = """
TASK  ➜ Produce a fully anonymised passage.

REPLACE-RULES
1)  PEOPLE Invent a two-part name built from **CVC + CVCC** syllables (e.g. “Mol Tesk”), Latin letters only.
     • Do not reuse any syllable that appears in the source.
     • No output token may share ≥ 3 consecutive letters with ANY source proper noun.
2)  PLACES / POLITIES Create fantasy names (e.g. “Verdan Canton”, “Dominion of Selqor”) obeying the same 3-letter-overlap ban.
3)  TITLES / OFFICES Keep the functional noun (“general”, “scribe”) but change realm modifiers (“of the Obsidian Marches”).
4)  DATES Convert every explicit year to the form **“Year ##”** where ## is a RANDOM two-digit number between 11 and 97
     and never matches the real digits.
     Ages become relative (“in early childhood”, “by his mid-thirties”).
5)  TEXTS / TEMPLES / OBJECTS Rename as in rule 1.
6)  HARD NO-CARRY-OVER If ANY substring ≥ 3 letters from a source name slips through, you must rewrite it.

OUTPUT FORMAT
• English prose only — no lists, no bullets, no headings.  
• Retain the same paragraph breaks as the input.  
• **Return ONLY the anonymized passage — zero commentary, zero labels.**

INPUT TO ANONYMIZE ⬇
"""

anonymize_biography_scratchpad_prompt = """
### SCRATCHPAD - NOT FOR OUTPUT
Step 1  List every proper noun / year you will replace.
Step 2  Show your invented substitutes.
Step 3  Draft the anonymized passage.
Step 4  SELF-AUDIT: scan the draft; if any token shares ≥ 3 consecutive letters with a source token, rewrite it.
Only after passing Step 4 may you reveal the final passage (and nothing else).
"""


def run_api(user_input, call_purpose, model="gpt-4o"):
    # for now we only have gpt
    response = ""

    # user_input -> person's name
    if call_purpose == "know_by_name":
        response = run_gpt(know_by_name_system_prompt, user_input, KnowByNameFormat, model)
    # user_input -> anonymized biography
    elif call_purpose == "know_by_bio":
        response = run_gpt(know_by_bio_system_prompt, user_input, KnowByBio, model)
    # user_input -> non-anonymized biography
    elif call_purpose == "anonymize_biography":
        response = run_gpt_unformatted(anonymize_biography_system_prompt, anonymize_biography_user_prompt + user_input + anonymize_biography_scratchpad_prompt, model)

    return response

def run_gpt(system_prompt, user_prompt, format, model="gpt-4o", temperature: float = 0):
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

def run_gpt_unformatted(system_prompt, user_prompt, model="gpt-4o", temperature: float = 0):
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