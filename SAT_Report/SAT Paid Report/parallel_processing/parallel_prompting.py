# imports

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from datetime import datetime, timedelta

import os
import json
import nest_asyncio
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from typing import List

nest_asyncio.apply()

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# LLM Initialisation

def initialize_llm():
    provider = os.getenv("MODEL_PROVIDER")
    if provider == "GROQ":
        # Initialize the Groq LLM
        llm = ChatGroq(
            model= os.getenv("GROQ_MODEL"),
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.1,
            max_tokens=10000,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
        )
    elif provider == "OPENAI":
        # Initialize the OpenAI LLM
        llm = ChatOpenAI(
            model= os.getenv("OPENAI_MODEL"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.1,
            max_tokens=10000,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
        )
    return llm

llm = initialize_llm()

# Prompts

EXECUTIVE_SUMMARY_PROMPT = """ 
Student Data: 
Name: {student_name} 
Persona Name: {persona_name} 
Persona strengths: {persona_strengths} 
Persona challenges: {persona_challenges} 
 
SAT Performance: 
Total Score: {current_sat_score_total}  
Accuracy: {current_sat_accuracy} 
Time Management: {current_sat_time_management} 
 
Top 3 Strengths in Math with accuracy: {math_top_skills} 
Top 3 Weaknesses in Math with accuracy: {math_bottom_skills} 
Top 3 Strengths in Reading & Writing with accuracy: {rw_top_skills} 
Top 3 Weaknesses in Reading & Writing with accuracy: {rw_bottom_skills} 
 
Target SAT Dates: {planned_sat_date} 
Realistic Target Score: {goal_score} 
 
Preferred Tone: {tone}
 
Instructions: 
You are an expert SAT coach and behavioral science specialist. Write a personalized, comprehensive SAT readiness report for a Sherpal student using the structured input provided. 

Your tone should be **{tone}**, while also remaining **authentic, calm, and professional** — never salesy or exaggerated. Match the student’s persona thoughtfully but avoid frequently repeating their persona name. Speak to a smart, serious student. The report includes multiple sections and should remain motivational yet concise throughout. Avoid lengthy explanations—prioritize clear, high-impact takeaways over broad commentary. Keep it inspiring, focused, and straight to the point. Maintain consistent tone and phrasing across all sections to support reliable and repeatable output. 

Requirements for each section:

**CRITICAL: Return ONLY valid JSON in exactly this structure:** 
Do not wrap the JSON response inside markdown code block tags like ```json or ``` — return only raw JSON :

{{
"title":"Executive Summary"
"description":
    [
        {{
            "title":"Summary"
             "description": "Write a brief summary using SECOND PERSON addressing the student directly. Start with '{student_name}, you are a {persona_name} and key traits in one sentence using students Persona Strengths and Persona Challenges.' Include current SAT score of {current_sat_score_total}, accuracy rate of {current_sat_accuracy}% and time management at {current_sat_time_management}% in one sentance. Use the provided {current_level_assessment} for honest assessment of current level in one sentance. End with: {goal_achievability_assessment} for realistic evaluation of target score achievability in one sentance. Important: Any dates included in the summary must be in 'Month Year' format (e.g., June 2025). Maximum 100 words."
        }},
        {{
            "title":"Key Strengths"
            "description":
            {{
                "Reading & Writing: these are the top 3 Reading and writing skills: {rw_top_skills}
                output must follow the below structure as array of strings:
                ["<skill1> (accuracy%)", "<skill2> (accuracy%)", "<skill3> (accuracy%)"],

                "Math: these are the top 3 Math skills: {math_top_skills}
                output must follow the below structure as array of strings:
                ["<skill1> (accuracy%)", "<skill2> (accuracy%)", "<skill3> (accuracy%)"]

            }},
        }},
        {{
            "title": "Focus Areas for Growth"
            "description":
            {{
                "Reading & Writing: these are the bottom three Reading and Writing skills:{rw_bottom_skills}
                output must follow the below structure as array of strings:"
                "["<skill1> (accuracy%)", "<skill2> (accuracy%)", "<skill3> (accuracy%)"]",
                "Math: these are the bottom three Math skills:{math_bottom_skills} 
                output must follow the below structure as array of strings:"
                "["<skill1> (accuracy%)", "<skill2> (accuracy%)", "<skill3> (accuracy%)"]"
            }},
        }},
        {{
            "title": "Study Plan"
            "description": "The start of any strong study plan begins with review. Before you move forward, take time to go back and focus on the 'Recommended Questions' highlighted in your score reports. These key questions from your SAT Practice Test, Domain Tests, and Endurance Test are where the deepest learning happens. Reviewing them is your first real step toward smarter progress."
        }}
    ]
}}
"""

FOUNDATION_PHASE_PROMPT = """
You are an expert SAT coach and behavioral science specialist. Write a personalized SAT Foundation Phase study plan, using the structured input provided.

Preferred Tone: {tone}

Your tone should be **{tone}**, while also remaining authentic, calm, and professional — never salesy or exaggerated. Match the student's persona thoughtfully but avoid frequently repeating their persona name. Speak to a smart, serious student. The report includes multiple sections and should remain motivational yet concise throughout.

Create a personalized SAT Foundation Phase study plan for a student named {student_name}. This student is described as a "{persona_name}", with the following strengths: {persona_strengths}, faces these challenges: {persona_challenges}, and growth strategies: {growth_strategies}.

Here is the student's profile and data:
- Name: {student_name}
- Persona Name: {persona_name}
- Key Strengths: {persona_strengths}
- Areas of Improvement: {persona_challenges}
- Growth Strategies: {growth_strategies}

- Current SAT Score: {current_sat_score_total}
- Goal SAT Score: {goal_score}

- Reading & Writing Skill (in priority order): {rw_foundation_skills}
- Math Skill (in priority order): {math_foundation_skills}

Avoid lengthy explanations—prioritize clear, high-impact takeaways over broad commentary - keep it inspiring, focused, and straight to the point. Maintain consistent tone and phrasing across sections to support reliable and repeatable output.

The Foundation Phase will take place from {foundation_date_range}.

Instructions:
- Do not include '\\n'
- Data should be purely generated based on the Persona details.
- avoid bullet points, lists, or line breaks between sentences.

Purpose:
To build a strong baseline of understanding across all SAT-tested skills with focus on accuracy, concept clarity, and learning discipline.

Key Focus:
- Establish structured study habits
- Improve accuracy and comprehension of core skills
- Identify and start closing skill gaps
- Build confidence slowly through consistency

Using the above data, generate a **Foundation Phase** study report divided into the following sections with these exact headings:

1. Weekly Goals  
2. Practice Methods  
3. Weekly Structure  
4. Flex Day Activities

Requirements for each section:

**CRITICAL: Return ONLY valid JSON in exactly this structure:**
Do not wrap the JSON response inside markdown code block tags like ```json or ``` — return only raw JSON :

{{
    "title": "Foundation Phase",
    "description":
    [
      {{
         "title": "Weekly Goals",
         "description": "Summarize clear, specific, outcome-driven goals the student should achieve each week during the Foundation Phase. Avoid mentioning how to achieve them or practice methods. Focus on measurable improvements in both Math and Reading & Writing, steady reduction of repeat mistakes, and improved reasoning and accuracy."
      }},
      {{
         "title": "Skill Areas",
         "description":
         [
            {{
               "title": "Reading & Writing",
               "description": "List these reading and writing skills: {rw_foundation_skills}"
            }},
            {{
               "title": "Math", 
               "description": "List these math skills: {math_foundation_skills}"
            }},
         ]
      }},
      {{
         "title": "Practice Methods",
         "description": 
         [
            {{
               "title": "Reading & Writing",
               "description": "For each Reading & Writing skill, create THREE completely UNIQUE and DISTINCT tactical, specific, and actionable practice method that seamlessly integrates: the study tips and recommended exercises from **ONLY that specific skill's summary** in {rw_foundation_skill_summary_objects}, the appropriate practice level guidance from {rw_foundation_skills_with_level_message}, the student's strengths ({persona_strengths}), areas for improvement ({persona_challenges}), and growth strategies ({growth_strategies}). Draw from the skill's key concepts and avoid the common mistakes listed. Each method should be a single, concrete practice activity that directly addresses the skill needs. Ensure NO overlap in core activities, techniques, or approaches between the three methods.

               Strictly follow this output Format as: 
               '<skill_name>': [
               'First specific, tactical practice method that naturally incorporates the skill's study tips, recommended exercises, level requirements, and student profile into a concrete, actionable activity.',
               'Second specific, tactical practice method that naturally incorporates the skill's study tips, recommended exercises, level requirements, and student profile into a concrete, actionable activity.',
               'Third specific, tactical practice method that naturally incorporates the skill's study tips, recommended exercises, level requirements, and student profile into a concrete, actionable activity.' ]"
            }},
            {{
               "title": "Math",
               "description": "For each Math skill, create THREE completely UNIQUE and DISTINCT tactical, specific, and actionable practice methods that seamlessly integrate: the skill-specific strategies and tips from **ONLY that specific skill's summary** in {math_foundation_skill_summary_objects}, the appropriate practice level guidance from {math_foundation_skills_with_level_message}, the student's strengths ({persona_strengths}), areas for improvement ({persona_challenges}), and growth strategies ({growth_strategies}). 

               **SKILL-SPECIFIC ALIGNMENT REQUIREMENT**: When generating practice methods for a particular Math skill (e.g., 'Algebra'), use ONLY the summary data, strategies, tips, and exercises that belong to that exact skill from {math_foundation_skill_summary_objects}. DO NOT mix or cross-reference content from other skills' summaries.

               Each method should be a single, concrete practice activity that directly addresses the skill needs. Ensure NO overlap in core activities, techniques, or approaches between the three methods.

               Strictly follow this output Format as: 
               '<skill_name>': [
               'First specific, tactical practice method that naturally incorporates the skill's study tips, recommended exercises, level requirements, and student profile into a concrete, actionable activity.',
               'Second specific, tactical practice method that naturally incorporates the skill's study tips, recommended exercises, level requirements, and student profile into a concrete, actionable activity.',
               'Third specific, tactical practice method that naturally incorporates the skill's study tips, recommended exercises, level requirements, and student profile into a concrete, actionable activity.' ]"
            }}
         ]
      }},
      {{
         "title": "Weekly Structure",
         "description": "Provide a generic overview of the weekly routine focused on deep conceptual mastery.Explain how each weekday will include focused dual-skill practice (one Math and one Reading & Writing skill), starting with the weakest skills early in the week, midweek focus on moderate skills, Fridays for review, {foundational_saturday_activity}, and one Flex Day for rest and adaptability."

      }},
      {{
         "title": "Flex Day Activities", 
         "description": "Suggest actionable, persona-aligned activities that support rest, reflection, cognitive flexibility, and low-pressure practice. Include reflection on errors, experimenting with new tools or techniques, mixed-skill challenges, physical or mindfulness rest activities, and goal-setting for the next week."
      }}
    ]
}}

**Requirements:**
- Return valid JSON only - no additional text
- Keep descriptions concise but personalized 
- Do not include any generic or vague advice. Use the data provided to personalize every recommendation.
- Make Flex Day Activities unique to the student's persona
- For Practice Methods: Each skill should have ONE comprehensive practice method that naturally weaves together all the provided elements (skill summaries, level guidance, student profile) into a cohesive, actionable routine.
"""

ELEVATION_PHASE_PROMPT = """

You are an expert SAT coach and behavioral science specialist. Write a personalized SAT Elevation Phase study plan, using the structured input provided.

Preferred Tone: {tone}

Your tone should be **{tone}**, while also remaining authentic, calm, and professional — never salesy or exaggerated. Match the student's persona thoughtfully but avoid frequently repeating their persona name. Speak to a smart, serious student. The report includes multiple sections and should remain motivational yet concise throughout.

Create a personalized SAT Elevation Phase study plan for a student named {student_name}. This student is described as a "{persona_name}", with the following strengths: {persona_strengths}, faces these challenges: {persona_challenges}, and growth strategies: {growth_strategies}.

Here is the student's profile and data:
- Name: {student_name}
- Persona Name: {persona_name}
- Key Strengths: {persona_strengths}
- Areas of Improvement: {persona_challenges}
- Growth Strategies: {growth_strategies}

- Current SAT Score: {current_sat_score_total}
- Goal SAT Score: {goal_score}

- Reading & Writing Skill Accuracies (in priority order): {rw_elevation_skills}
- Math Skill Accuracies (in priority order): {math_elevation_skills}


Avoid lengthy explanations—prioritize clear, high-impact takeaways over broad commentary - keep it inspiring, focused, and straight to the point. Maintain consistent tone and phrasing across sections to support reliable and repeatable output.

The Elevation Phase will take place from {elevation_date_range}.

Instructions:
- Do not include '\\n'
- Data should be purely generated based on the Persona details.
- avoid bullet points, lists, or line breaks between sentences.

Purpose:
To push skill application under timed conditions, refine accuracy, and improve cognitive flexibility with mid-level and advanced skills.

Key Focus:
- Reduce careless mistakes
- Reinforce second-tier skills (those partially mastered)
- Introduce moderate time pressure
- Layer more strategic practice
- Use performance review cycles (analyze → adapt → retest)

Using the above data, generate a **Elevation Phase** study report divided into the following sections with these exact headings:

1. Weekly Goals  
2. Practice Methods  
3. Weekly Structure  
4. Flex Day Activities

Requirements for each section:

**CRITICAL: Return ONLY valid JSON in exactly this structure:**
Do not wrap the JSON response inside markdown code block tags like ```json or ``` — return only raw JSON :

{{
    title: "Elevation Phase",
    description:
    [
      {{
         "title": "Weekly Goals",
         "description": "Summarize clear, specific, outcome-driven goals the student should achieve each week during the Elevation Phase. Avoid mentioning how to achieve them or practice methods. Focus on measurable improvements in both Math and Reading & Writing, steady reduction of repeat mistakes, and improved reasoning and accuracy."
      }},
      {{
         "title": "Skill Areas",
         "description":
         [,
            {{
               "title": "Reading & Writing",
               "description": "List these reading and writing skills: {rw_elevation_skills}"
            }},
            {{
               "title": "Math", 
               "description": "List these math skills: {math_elevation_skills}"
            }}
         ]
      }},
      {{
         "title": "Practice Methods",
         "description": 
         [
            {{
               "title": "Reading & Writing",
               "description": "For each Reading & Writing skill, create ONE tactical, specific, and actionable practice method that seamlessly integrates: the study tips and recommended exercises from the skill's summary in {math_elevation_skill_summary_objects}, the appropriate practice level guidance from {rw_elevation_skills_with_level_message}, the student's strengths ({persona_strengths}), areas for improvement ({persona_challenges}), and growth strategies ({growth_strategies}). Draw from the skill's key concepts and avoid the common mistakes listed. Each method should be a single, concrete practice activity that directly addresses the skill needs.

               Format as: '<skill_name>': 'One specific, tactical practice method that naturally incorporates the skill's study tips, recommended exercises, level requirements, and student profile into a concrete, actionable activity.'"
            }},
            {{
               "title": "Math",
               "description": "For each Math skill, create ONE tactical, specific, and actionable practice method that seamlessly integrates: the skill-specific strategies and tips from {math_elevation_skill_summary_objects}, the appropriate practice level guidance from {math_elevation_skills_with_level_message}, the student's strengths ({persona_strengths}), areas for improvement ({persona_challenges}), and growth strategies ({growth_strategies}). Each method should be a single, concrete practice activity that directly addresses the skill needs.

               Format as: '<skill_name>': 'One specific, tactical practice method that naturally incorporates the skill guidance, level requirements, and students profile into a concrete, actionable activity.'"
            }}
         ]
      }}
      {{
         "title": "Weekly Structure",
         "description": "Provide a generic overview of the weekly routine focused on balancing Conceptual Mastery and Full-Length Practice. Explain how each weekday will include focused dual-skill practice (one Math and one Reading & Writing skill), starting with the weakest skills early in the week, midweek focus on moderate skills, Fridays for review, {elevation_saturday_activity}, and one Flex Day for rest and adaptability."
      }},
      {{
         "title": "Flex Day Activities", 
         "description": "Suggest actionable, persona-aligned activities that support rest, reflection, cognitive flexibility, and low-pressure practice. Include reflection on errors, experimenting with new tools or techniques, mixed-skill challenges, physical or mindfulness rest activities, and goal-setting for the next week."
      }}
    ]
}}

**Requirements:**
- Return valid JSON only - no additional text
- Keep descriptions concise but personalized 
- Do not include any generic or vague advice. Use the data provided to personalize every recommendation.
- Make Flex Day Activities unique to the student's persona
"""

PEAK_PHASE_PROMPT = """

You are an expert SAT coach and behavioral science specialist. Write a personalized SAT Elevation Phase study plan, using the structured input provided.

Preferred Tone: {tone}

Your tone should be **{tone}**, while also remaining authentic, calm, and professional — never salesy or exaggerated. Match the student's persona thoughtfully but avoid frequently repeating their persona name. Speak to a smart, serious student. The report includes multiple sections and should remain motivational yet concise throughout.

Create a personalized SAT Peak Phase study plan for a student named {student_name}. This student is described as a "{persona_name}", with the following strengths: {persona_strengths}, faces these challenges: {persona_challenges}, and growth strategies: {growth_strategies}.

Here is the student's profile and data:
- Name: {student_name}
- Persona Name: {persona_name}
- Key Strengths: {persona_strengths}
- Areas of Improvement: {persona_challenges}
- Growth Strategies: {growth_strategies}

- Current SAT Score: {current_sat_score_total}
- Goal SAT Score: {goal_score}

- Reading & Writing Skill Accuracies (in priority order): {rw_peak_skills}
- Math Skill Accuracies (in priority order): {math_peak_skills}


Avoid lengthy explanations—prioritize clear, high-impact takeaways over broad commentary - keep it inspiring, focused, and straight to the point. Maintain consistent tone and phrasing across sections to support reliable and repeatable output.

The Peak Phase will take place from {peak_date_range}.

Instructions:
- Do not include '\\n'
- Data should be purely generated based on the Persona details.
- avoid bullet points, lists, or line breaks between sentences.

Purpose:
To simulate real test conditions, stabilize performance, and reinforce confidence. Focusing on mastery.

Key Focus:
- Confidence under pressure
- Endurance for full test conditions
- Mental and emotional control
- Pattern recognition
- Minimize score variance
- Lock in strategy

Using the above data, generate a **Peak Phase** study report divided into the following sections with these exact headings:

1. Weekly Goals  
2. Practice Methods  
3. Weekly Structure  
4. Flex Day Activities

Requirements for each section:

**CRITICAL: Return ONLY valid JSON in exactly this structure:**
Do not wrap the JSON response inside markdown code block tags like ```json or ``` — return only raw JSON :

{{
    title: "Peak Phase",
    description:
    [
      {{
         "title": "Weekly Goals",
         "description": "Summarize clear, specific, outcome-driven goals the student should achieve each week during the Peak Phase. Avoid mentioning how to achieve them or practice methods. Focus on measurable improvements in both Math and Reading & Writing, steady reduction of repeat mistakes, and improved reasoning and accuracy."
      }},
      {{
         "title": "Skill Areas",
         "description":
         [
            {{
               "title": "Reading & Writing",
               "description": "List these reading and writing skills: {rw_peak_skills}"
            }},
            {{
               "title": "Math", 
               "description": "List these math skills: {math_peak_skills}"
            }},
         ]
      }},
      {{
         "title": "Practice Methods",
         "description": 
         [
            {{
               "title": "Reading & Writing",
               "description": "For each Reading & Writing skill, create ONE tactical, specific, and actionable practice method that seamlessly integrates: the study tips and recommended exercises from the skill's summary in {rw_peak_skill_summary_objects}, the appropriate practice level guidance from {rw_peak_skills_with_level_message}, the student's strengths ({persona_strengths}), areas for improvement ({persona_challenges}), and growth strategies ({growth_strategies}). Draw from the skill's key concepts and avoid the common mistakes listed. Each method should be a single, concrete practice activity that directly addresses the skill needs.

               Format as: '<skill_name>': 'One specific, tactical practice method that naturally incorporates the skill's study tips, recommended exercises, level requirements, and student profile into a concrete, actionable activity.'"
            }},
            {{
               "title": "Math",
               "description": "For each Math skill, create ONE tactical, specific, and actionable practice method that seamlessly integrates: the skill-specific strategies and tips from {math_peak_skill_summary_objects}, the appropriate practice level guidance from {math_peak_skills_with_level_message}, the student's strengths ({persona_strengths}), areas for improvement ({persona_challenges}), and growth strategies ({growth_strategies}). Each method should be a single, concrete practice activity that directly addresses the skill needs.

               Format as: '<skill_name>': 'One specific, tactical practice method that naturally incorporates the skill guidance, level requirements, and students profile into a concrete, actionable activity.'"
            }}
         ]
      }},
      {{
         "title": "Weekly Structure",
         "description": "Provide a generic overview of the weekly routine focused on Focusing on Accuracy and Speed. Explain how each weekday will include focused dual-skill practice (one Math and one Reading & Writing skill), starting with the weakest skills early in the week, midweek focus on moderate skills, Fridays for review, {peak_saturday_activity}, and one Flex Day for rest and adaptability."
      }},
      {{
         "title": "Flex Day Activities", 
         "description": "Suggest actionable, persona-aligned activities that support rest, reflection, cognitive flexibility, and low-pressure practice. Include reflection on errors, experimenting with new tools or techniques, mixed-skill challenges, physical or mindfulness rest activities, and goal-setting for the next week."
      }}
    ]
}}

**Requirements:**
- Return valid JSON only - no additional text
- Keep descriptions concise but personalized 
- Do not include any generic or vague advice. Use the data provided to personalize every recommendation.
- Make Flex Day Activities unique to the student's persona
"""

TIPS_TO_MAKE_IT_WORK_BEST_PROMPT = """
You are an expert SAT coach and behavioral science specialist. Write only the “Tips to Make It Work Best” section of a personalized SAT Elevation Phase study plan for a student named {student_name}. This student is described as a "{persona_name}", with the following strengths: {persona_strengths}, faces these challenges: {persona_challenges}, and follows these growth strategies: {growth_strategies}.

Preferred Tone: {tone}

Your tone should be **{tone}**, while also remaining authentic, calm, and professional — never salesy or exaggerated. Match the student's persona thoughtfully but avoid frequently repeating their persona name. Speak to a smart, serious student. The report includes multiple sections and should remain motivational yet concise throughout.

Here is the student’s academic profile:
- Current SAT Score: {current_sat_score_total}
- Goal SAT Score: {goal_score}
- Phase Timelines: Foundation: {foundation_date_range}, Elevation: {elevation_date_range}, Peak: {peak_date_range}

Skill Summary Insights:
- Reading & Writing Skill Summaries: {rw_top_3_priority_skill_summary_objects}
- Math Skill Summaries: {math_top_3_priority_skills_summary_objects}

Your task:
Return ONLY the following JSON structure:
**CRITICAL: Return ONLY valid JSON in exactly this structure:**
Do not wrap the JSON response inside markdown code block tags like ```json or ``` — return only raw JSON:

{{
  "title": "TIPS TO MAKE IT WORK BEST FOR YOUR FOUNDATION PHASE",
  "description": [
    "Tip for RW Skill 1.",
    "Tip for RW Skill 2.",
    "Tip for RW Skill 3.",
    "Tip for Math Skill 1.",
    "Tip for Math Skill 2.",
    "Tip for Math Skill 3."
  ]
}}

Instructions:
- For each of the six skills (three from Reading & Writing and three from Math), write one actionable, personalized tip.
- Each tip must be grounded in the corresponding skill summary content (from {rw_top_3_priority_skill_summary_objects} and {math_top_3_priority_skills_summary_objects}).
- Align every tip with the student’s persona, strengths, challenges, and growth plan.
- Tips should promote SAT-specific behavioral improvements, including time management, error reflection, learning agility, strategic flexibility, and confidence under pressure.
- Avoid vague or repetitive suggestions. Every tip should feel unique, directly tied to the specific skill, and clearly actionable.
- Return only valid JSON in the structure above — no extra commentary or wrapping.
"""

WORDS_OF_ENCOURAGEMENT = """
You are an expert SAT coach and behavioral science specialist. Write only the “Words of Encouragement” section of a personalized SAT Elevation Phase study plan for a student named {student_name}. This student is described as a "{persona_name}", with the following strengths: {persona_strengths}, faces these challenges: {persona_challenges}, and follows these growth strategies: {growth_strategies}.

Preferred Tone: {tone}

Your tone should be **{tone}**, while also remaining authentic, calm, and professional — never salesy or exaggerated. Match the student's persona thoughtfully but avoid frequently repeating their persona name. Speak to a smart, serious student. The report includes multiple sections and should remain motivational yet concise throughout.

Here is the student’s academic profile:
- Current SAT Score: {current_sat_score_total}
- Goal SAT Score: {goal_score}
- Phase Timelines: Foundation: {foundation_date_range}, Elevation: {elevation_date_range}, Peak: {peak_date_range}
- Reading & Writing Skill Summaries: {rw_top_3_priority_skill_summary_objects}
- Math Skill Summaries: {math_top_3_priority_skills_summary_objects}

Your task:
Return ONLY the following JSON structure:
**CRITICAL: Return ONLY valid JSON in exactly this structure:**
Do not wrap the JSON response inside markdown code block tags like ```json or ``` — return only raw JSON:

{{
  "title": "THIS JOURNEY IS YOURS. PACE IT, OWN IT, PROGRESS WITH PURPOSE",
  "description": "Write a personalized motivational message between 100 and 150 words."
}}

Instructions:
- Your message must acknowledge the student’s persona, key strengths, and specific academic effort or skill growth based on the provided skill summaries.
- Reflect on both the personal growth journey and the technical work the student is doing (e.g. improving evidence-based reading, building algebraic confidence, managing time under pressure).
- Be empowering, sincere, and specific — no vague praise or generic quotes.
- Reinforce the student’s potential and momentum as they move through the Elevation Phase toward their SAT goal.
- Do not include any introductory or closing text. Output only valid JSON in the exact format above.
"""

STATIC_CTA = {
  "title": "STATIC CTA",
  "description": [
  "The study plan you’ve received points you in the right direction. But getting to your goal takes more than direction — it takes structure, discipline, and momentum.",
  "Sherpal’s full journey makes it easier to stay on track, go deeper, and reach higher - with support that’s built around you.",
  "Start your full journey at www.sherpalai.com Personalized. Engaging. Goal-driven."
  ]
}

FOOTER = {
  "title": "FOOTER",
  "description": [
  "Safe Harbor Statement:",
  "Sherpal is an AI-powered learning platform designed to personalize SAT preparation and student growth. While our tools are based on proven learning strategies and data-informed insights, we do not guarantee specific score outcomes. Student results depend on individual effort, consistency, and use of the program. All names, personas, and scenarios used in the platform are for educational purposes and are not predictive or diagnostic.",
  ]
}

# Helper Functions

def format_range(start, end):
    return f"{start.strftime('%Y-%m-%d')} - {end.strftime('%Y-%m-%d')}"
 
def get_three_month_study_phases(start_date_str: str):
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD."
 
    foundation_start = start_date
    foundation_end = foundation_start + timedelta(days=30)
 
    elevation_start = foundation_end + timedelta(days=1)
    elevation_end = elevation_start + timedelta(days=29)
 
    peak_start = elevation_end + timedelta(days=1)
    peak_end = peak_start + timedelta(days=29)
 
    return (
        format_range(foundation_start, foundation_end),
        format_range(elevation_start, elevation_end),
        format_range(peak_start, peak_end),
        peak_end.strftime('%Y-%m-%d')
    )
 
def get_custom_study_phases(today_str: str, planned_str: str):
    try:
        today = datetime.strptime(today_str, "%Y-%m-%d").date()
        planned = datetime.strptime(planned_str, "%Y-%m-%d").date()
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD."
 
    if planned <= today:
        return "Planned date must be after today's date."
 
    diff_days = (planned - today).days
 
    part = diff_days // 3
    remainder = diff_days % 3
 
    foundation_start = today
    foundation_end = foundation_start + timedelta(days=part + (1 if remainder > 0 else 0) - 1)
 
    elevation_start = foundation_end + timedelta(days=1)
    elevation_end = elevation_start + timedelta(days=part + (1 if remainder > 1 else 0) - 1)
 
    peak_start = elevation_end + timedelta(days=1)
    peak_end = planned
 
    return (
        format_range(foundation_start, foundation_end),
        format_range(elevation_start, elevation_end),
        format_range(peak_start, peak_end),
        peak_end.strftime('%Y-%m-%d')
    )
 
def get_study_plan(current_score: int, goal_score: int, today_date_str: str, planned_date_str: str) -> str:
    # Convert string to date
    try:
        today_date = datetime.strptime(today_date_str, "%Y-%m-%d").date()
        planned_date = datetime.strptime(planned_date_str, "%Y-%m-%d").date()
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD."
 
    score_diff = goal_score - current_score
    if score_diff < 0:
        return "Invalid input: Goal score must be higher than current score."
 
    days_gap = (planned_date - today_date).days
    if days_gap < 0:
        return "Invalid input: Planned date must be in the future."
   
    tone_confident_encouraging = "Use a confident and encouraging tone. Focus on fine-tuning and light improvements."
    tone_motivational_urgent = "Use a motivational tone with urgency. Emphasize structured habits and sustained effort."
    tone_serious_constructive = "Use serious, honest, and constructive tone. Highlight foundational review and disciplined rebuilding."
 
    duration_confident = "60"
    flex_duration_confident = "30"
 
    duration_ambitious = "90"
    flex_duration_ambitious = "60"
 
    duration_aggressive = "120"
    flex_duration_aggressive = "90"
 
    fifth_sentence = ""
 
    # Additionally, include these exact points at the end of the summary:
    conclusion = "Conclude the summary by adding these exact sentences: Considering your upcoming SAT exam date and target score, please write an email to info@sherpalai.com so we can assist you in tailoring your study plan. The default study plan is for three months of total preparation time."
 
    # Case 1: Any score difference and gap < 9 days
    if days_gap < 8:
 
        result = get_three_month_study_phases(today_date_str)
        if isinstance(result, str):
            return result
        else:
            foundation, elevation, peak, end_date = result
 
        duration = duration_confident
        flex_duration = flex_duration_confident
        tone = tone_confident_encouraging
        fifth_sentence = conclusion
       
        return foundation, elevation, peak, end_date, duration, flex_duration, tone, fifth_sentence
 
    # Case 2: 9–31 days
    if 8 <= days_gap <= 31:
        if score_diff <= 100:
 
            result = get_custom_study_phases(today_date_str, planned_date_str)
            if isinstance(result, str):
                return result
            else:
                foundation, elevation, peak, end_date = result
 
            duration = duration_confident
            flex_duration = flex_duration_confident
            tone = tone_confident_encouraging
 
            return foundation, elevation, peak, end_date, duration, flex_duration, tone, fifth_sentence
       
        elif 101 <= score_diff <= 250:
 
            result = get_custom_study_phases(today_date_str, planned_date_str)
            if isinstance(result, str):
                return result
            else:
                foundation, elevation, peak, end_date = result
 
            duration = duration_ambitious
            flex_duration= flex_duration_ambitious
            tone = tone_motivational_urgent
 
            return foundation, elevation, peak, end_date, duration, flex_duration, tone, fifth_sentence
       
        elif 251 <= score_diff <= 400:
 
            result = get_custom_study_phases(today_date_str, planned_date_str)
            if isinstance(result, str):
                return result
            else:
                foundation, elevation, peak, end_date = result
           
            duration= duration_aggressive
            flex_duration= flex_duration_aggressive
            tone = tone_serious_constructive
 
            return foundation, elevation, peak, end_date, duration, flex_duration, tone, fifth_sentence
       
        elif score_diff > 400:
 
            result = get_three_month_study_phases(today_date_str)
            if isinstance(result, str):
                return result
            else:
                foundation, elevation, peak, end_date = result
           
            duration = duration_confident
            flex_duration = flex_duration_confident
            tone = tone_confident_encouraging
            fifth_sentence = conclusion
           
            return foundation, elevation, peak, end_date, duration, flex_duration, tone, fifth_sentence
 
    # Case 3: 31–60 days
    if 31 < days_gap <= 60:
        if score_diff <= 500:
 
            result = get_custom_study_phases(today_date_str, planned_date_str)
            if isinstance(result, str):
                return result
            else:
                foundation, elevation, peak, end_date = result
 
            duration = duration_confident
            flex_duration = flex_duration_confident
            tone = tone_confident_encouraging
 
            return foundation, elevation, peak, end_date, duration, flex_duration, tone, fifth_sentence
        elif 501 <= score_diff <= 600:
 
            result = get_custom_study_phases(today_date_str, planned_date_str)
            if isinstance(result, str):
                return result
            else:
                foundation, elevation, peak, end_date = result
 
            duration = duration_ambitious
            flex_duration= flex_duration_ambitious
            tone = tone_motivational_urgent
 
            return foundation, elevation, peak, end_date, duration, flex_duration, tone, fifth_sentence
       
        elif 601 <= score_diff <= 700:
 
            result = get_custom_study_phases(today_date_str, planned_date_str)
            if isinstance(result, str):
                return result
            else:
                foundation, elevation, peak, end_date = result
 
            duration= duration_aggressive
            flex_duration= flex_duration_aggressive
            tone = tone_serious_constructive
 
            return foundation, elevation, peak, end_date, duration, flex_duration, tone, fifth_sentence
        elif score_diff > 700:
 
            result = get_three_month_study_phases(today_date_str)
            if isinstance(result, str):
                return result
            else:
                foundation, elevation, peak, end_date = result
 
            duration = duration_confident
            flex_duration = flex_duration_confident
            tone = tone_confident_encouraging
            fifth_sentence = conclusion
           
            return foundation, elevation, peak, end_date, duration, flex_duration, tone, fifth_sentence
 
    # Case 4: 61–90 days
    if 61 <= days_gap <= 90:
        if score_diff <= 800:
           
            result = get_custom_study_phases(today_date_str, planned_date_str)
            if isinstance(result, str):
                return result
            else:
                foundation, elevation, peak, end_date = result
 
            duration = duration_confident
            flex_duration = flex_duration_confident
            tone = tone_confident_encouraging
 
            return foundation, elevation, peak, end_date, duration, flex_duration, tone, fifth_sentence
       
        elif 801 <= score_diff <= 900:
 
            result = get_custom_study_phases(today_date_str, planned_date_str)
            if isinstance(result, str):
                return result
            else:
                foundation, elevation, peak, end_date = result
 
            duration = duration_ambitious
            flex_duration= flex_duration_ambitious
            tone = tone_motivational_urgent
 
            return foundation, elevation, peak, end_date, duration, flex_duration, tone, fifth_sentence
       
        elif 901 <= score_diff <= 1000:
 
            result = get_custom_study_phases(today_date_str, planned_date_str)
            if isinstance(result, str):
                return result
            else:
                foundation, elevation, peak, end_date = result
 
            duration= duration_aggressive
            flex_duration= flex_duration_aggressive
            tone = tone_serious_constructive
 
            return foundation, elevation, peak, end_date, duration, flex_duration, tone, fifth_sentence
        elif score_diff > 1000:
 
            result = get_three_month_study_phases(today_date_str)
            if isinstance(result, str):
                return result
            else:
                foundation, elevation, peak, end_date = result
 
            duration = duration_confident
            flex_duration = flex_duration_confident
            tone = tone_confident_encouraging
            fifth_sentence = conclusion
           
            return foundation, elevation, peak, end_date, duration, flex_duration, tone, fifth_sentence
 
    # Case 5: >90 days
    if days_gap > 90:
           
            result = get_custom_study_phases(today_date_str, planned_date_str)
            if isinstance(result, str):
                return result
            else:
                foundation, elevation, peak, end_date = result
 
            duration = duration_confident
            flex_duration = flex_duration_confident
            tone = tone_confident_encouraging
           
            return foundation, elevation, peak, end_date, duration, flex_duration, tone, fifth_sentence
 
    return "Unexpected case. Please review the inputs."
 
def get_domain_rankings(rw_domains, math_domains):
    # Weightage for each domain
    rw_weightage = {
        "Craft and Structure": 0.28,
        "Information and Ideas": 0.26,
        "Standard English Conventions": 0.26,
        "Expression of Ideas": 0.20
    }
 
    math_weightage = {
        "Algebra": 0.35,
        "Advanced Math": 0.35,
        "Problem-Solving and Data Analysis": 0.15,
        "Geometry and Trigonometry": 0.15
    }
 
    # Helper to compute domain info with priority score
    def process_domains(domains, weight_map):
        domain_info = []
        for d in domains:
            name = d["domain"]
            accuracy = d["accuracy"]
            weight = weight_map.get(name, 0)
            priority_score = (1 - accuracy) * weight
            domain_info.append({
                "name": name,
                "accuracy": accuracy,
                "weightage": weight,
                "priority_score": priority_score
            })
        return domain_info
 
    # Process each category
    rw_processed = process_domains(rw_domains, rw_weightage)
    math_processed = process_domains(math_domains, math_weightage)
 
    # Combine and sort all domains
    combined_domains = rw_processed + math_processed
 
    combined_ranking = sorted(
        combined_domains,
        key=lambda d: (-d['priority_score'], -d['weightage'], d['name'])
    )
 
    rw_ranking = sorted(
        rw_processed,
        key=lambda d: (-d['priority_score'], -d['weightage'], d['name'])
    )
 
    math_ranking = sorted(
        math_processed,
        key=lambda d: (-d['priority_score'], -d['weightage'], d['name'])
    )
 
    return combined_ranking, rw_ranking, math_ranking

def list_to_numbered_string(items):
    """Convert list of strings to a numbered string with newlines."""
    return "\n".join([f"{i + 1}. {item}." for i, item in enumerate(items)])

def get_realistic_improvement_expectation(current_score, goal_score):
    score_gap = goal_score - current_score
    # Calculate realistic improvement based on current level
    if current_score < 600:
        realistic_gain = min(200, score_gap)  # Cap at 200 for very low scores
    elif current_score < 800:
        realistic_gain = min(300, score_gap)  # Cap at 250 for low-mid scores
    elif current_score < 1000:
        realistic_gain = min(400, score_gap)  # Cap at 200 for mid scores
    elif current_score < 1200:
        realistic_gain = min(500, score_gap)  # Cap at 150 for high scores
    else:
        realistic_gain = min(600, score_gap)  # Cap at 100 for very high scores
    
    # Determine range
    lower_bound = max(50, realistic_gain - 50)
    upper_bound = realistic_gain
    
    return f"you can realistically expect to gain {lower_bound}-{upper_bound} points over the next few months"


GOAL_ACHIEVABILITY_ASSESSMENTS = {
    "gap_0_50": {
        "default": "Your target score of {goal_score} is well within reach with focused effort by {planned_sat_date}."
    },
    "gap_51_100": {
        "foundational": "Your target score of {goal_score} is achievable with consistent, structured preparation by {planned_sat_date}.",
        "developing": "Your target score of {goal_score} is well within reach with focused effort by {planned_sat_date}.",
        "solid": "Your target score of {goal_score} is very achievable with strategic practice by {planned_sat_date}.",
        "strong": "Your target score of {goal_score} is easily attainable with targeted improvements by {planned_sat_date}.",
        "advanced": "Your target score of {goal_score} is well within reach with fine-tuning by {planned_sat_date}."
    },
    "gap_101_200": {
        "foundational": "Your target score of {goal_score} is challenging but achievable with intensive, long-term preparation by {planned_sat_date}.",
        "developing": "Your target score of {goal_score} is achievable with dedicated preparation and strategic improvements by {planned_sat_date}.",
        "solid": "Your target score of {goal_score} is attainable with focused effort and consistent practice by {planned_sat_date}.",
        "strong": "Your target score of {goal_score} is achievable with strategic preparation by {planned_sat_date}.",
        "advanced": "Your target score of {goal_score} is well within reach with targeted optimization by {planned_sat_date}."
    },
    "gap_201_300": {
        "foundational": "Your target score of {goal_score} is extremely ambitious and may require extending your timeline beyond {planned_sat_date} or setting intermediate milestones.",
        "developing": "Your target score of {goal_score} is highly ambitious and will require exceptional dedication and comprehensive preparation by {planned_sat_date}.",
        "solid": "Your target score of {goal_score} is ambitious and will require intensive, strategic preparation over an extended period by {planned_sat_date}.",
        "strong": "Your target score of {goal_score} is challenging but achievable with comprehensive preparation by {planned_sat_date}.",
        "advanced": "Your target score of {goal_score} is ambitious and will require intensive optimization across all areas by {planned_sat_date}."
    },
    "gap_301_500": {
        "foundational": "Your target score of {goal_score} represents an extraordinary leap that would require complete transformation of your test-taking abilities well beyond {planned_sat_date}.",
        "developing": "Your target score of {goal_score} is exceptionally ambitious and may require reassessing your timeline or setting intermediate goals before {planned_sat_date}.",
        "solid": "Your target score of {goal_score} represents a significant challenge that demands exceptional commitment and may require extending beyond {planned_sat_date}.",
        "strong": "Your target score of {goal_score} is extremely ambitious and will require comprehensive, intensive preparation by {planned_sat_date}.",
        "advanced": "Your target score of {goal_score} is highly ambitious and will require exceptional dedication and strategic preparation by {planned_sat_date}."
    },
    "gap_501_plus": {
        "foundational": "Your target score of {goal_score} would require a complete transformation that is unrealistic by {planned_sat_date}. Consider setting intermediate milestones of 200-300 point improvements.",
        "developing": "Your target score of {goal_score} represents an extraordinary challenge that would likely require multiple test cycles and intermediate goals before {planned_sat_date}.",
        "solid": "Your target score of {goal_score} is exceptionally ambitious and would require reassessing your timeline and setting progressive milestones beyond {planned_sat_date}.",
        "strong": "Your target score of {goal_score} represents an extraordinary leap requiring exceptional preparation that may extend well beyond {planned_sat_date}.",
        "advanced": "Your target score of {goal_score} is exceptionally ambitious and would require intensive preparation with consideration for extending your timeline beyond {planned_sat_date}."
    }
}


def get_goal_achievability_assessment(current_score, goal_score, planned_sat_date):
    score_gap = goal_score - current_score

    # Determine current level
    if current_score < 400:
        current_level = "foundational"
    elif current_score < 600:
        current_level = "developing"
    elif current_score < 800:
        current_level = "solid"
    elif current_score < 1000:
        current_level = "strong"
    else:
        current_level = "advanced"

    # Select appropriate range key
    if score_gap <= 50:
        message_template = GOAL_ACHIEVABILITY_ASSESSMENTS["gap_0_50"]["default"]
    elif score_gap <= 100:
        message_template = GOAL_ACHIEVABILITY_ASSESSMENTS["gap_51_100"][current_level]
    elif score_gap <= 200:
        message_template = GOAL_ACHIEVABILITY_ASSESSMENTS["gap_101_200"][current_level]
    elif score_gap <= 300:
        message_template = GOAL_ACHIEVABILITY_ASSESSMENTS["gap_201_300"][current_level]
    elif score_gap <= 500:
        message_template = GOAL_ACHIEVABILITY_ASSESSMENTS["gap_301_500"][current_level]
    else:
        message_template = GOAL_ACHIEVABILITY_ASSESSMENTS["gap_501_plus"][current_level]

    return message_template.format(goal_score=goal_score, planned_sat_date=planned_sat_date)


CURRENT_LEVEL_ASSESSMENTS = {
    "gap_0_100": {
        "foundational": "your scores show a foundational level with clear, achievable growth ahead",
        "developing": "your performance demonstrates a developing foundation with realistic improvement potential",
        "solid": "your results reflect a solid base that's well-positioned for your target",
        "advanced": "your performance indicates an advanced level with fine-tuning needed for your target"
    },
    "gap_101_300": {
        "foundational": "your scores indicate a foundational level requiring focused, sustained effort",
        "developing": "your performance shows a developing foundation that needs considerable strengthening",
        "solid": "your results demonstrate a solid base with significant improvement needed",
        "advanced": "your performance indicates an advanced level with meaningful optimization ahead"
    },
    "gap_301_600": {
        "foundational": "your scores show a foundational level with substantial, long-term growth required",
        "developing": "your performance indicates a developing foundation requiring comprehensive skill building",
        "solid": "your results demonstrate a solid base that needs extensive development for your ambitious target",
        "advanced": "your performance shows an advanced level with considerable refinement needed"
    },
    "gap_601_plus": {
        "foundational": "your scores indicate a foundational level with exceptional growth required for your highly ambitious target",
        "developing": "your performance shows a developing foundation requiring transformative improvement for your ambitious goal", 
        "solid": "your results demonstrate a solid base, though your target represents a significant leap requiring intensive development",
        "advanced": "your performance indicates an advanced level, though your target requires exceptional refinement and optimization"
    }
}


def get_current_level_assessment(current_score, goal_score):
    score_gap = goal_score - current_score

    # Determine base level from current score
    if current_score < 700:
        base_level = "foundational"
    elif current_score < 1000:
        base_level = "developing"
    elif current_score < 1300:
        base_level = "solid"
    else:
        base_level = "advanced"

    # Select the correct assessment group
    if score_gap <= 100:
        assessment_group = "gap_0_100"
    elif score_gap <= 300:
        assessment_group = "gap_101_300"
    elif score_gap <= 600:
        assessment_group = "gap_301_600"
    else:
        assessment_group = "gap_601_plus"

    return CURRENT_LEVEL_ASSESSMENTS[assessment_group][base_level]


def get_top_and_bottom_skills(skills_data, skill_accuracy_data):
    # Sort by priority (ascending)
    sorted_skills = sorted(skills_data, key=lambda x: int(x["priority"]))
 
    # Helper: Find accuracy from skill_accuracy_data by name
    def get_accuracy(skill_name):
        for item in skill_accuracy_data:
            if item.get("name") == skill_name:
                return item.get("accuracy", "N/A")
        return "N/A"
 
    # Format skill name + accuracy
    def format_with_accuracy(skill_name):
        accuracy = get_accuracy(skill_name)
        return f"{skill_name} ({accuracy}%)"
 
    # Top & bottom 3 skill names
    top_3_names = [skill["name"] for skill in sorted_skills[:3]]
    bottom_3_skills = sorted_skills[-3:]  # Full skill objects for bottom 3
    bottom_3_names = [skill["name"] for skill in bottom_3_skills]
 
    # Format top and bottom 3 with accuracy
    top_3 = [format_with_accuracy(name) for name in top_3_names]
    bottom_3 = [format_with_accuracy(name) for name in bottom_3_names]
 
    # Extract bottom 3 resources
    bottom_3_resources = [
        {
            skill.get("name"): skill.get("educational_resources", [])
        }
        for skill in bottom_3_skills
    ]
 
    return top_3, bottom_3, bottom_3_resources
 

def extract_skills(report, skill_type):
    tabs = report.get("tabs", [])
    target_tab = next((tab for tab in tabs if tab.get("tab_name") == "Focus Area"), None)
 
 
    for subject in target_tab.get("subjects", []):
        if subject.get("subject") == skill_type:
            sections = subject.get("sections", [])
            for section in sections:
                if section.get("section_title") == "Optimizing Problem-Solving: Strengthening Core SAT Math Skills for Maximum Impact":
                    return section.get("section_details", [])
                elif section.get("section_title") == "Targeted Skill Refinement: Enhancing Efficiency & Accuracy in SAT Reading & Writing":
                    return section.get("section_details", [])
    return []

def extract_overall_assessment(report, skill_type):

    tabs = report.get("tabs", [])
    target_tab = next((tab for tab in tabs if tab.get("tab_name") == "Overall Assessment"), None)
    for subject in target_tab.get("subjects", []):
        if subject.get("subject") == skill_type:
            sections = subject.get("sections", [])
            for section in sections:
                if section.get("section_title") == "Skill Performance (Overall)":
                    top_skills = []
                    bottom_skills = []
                    section_details = section.get("section_details", [])
                    for detail in section_details:
                        skill_name = detail.get("name")
                        weightage = detail.get("weightage")
                        formatted_skill = f"{skill_name} - {weightage}%"
                        if detail.get("is_top"):
                            top_skills.append(formatted_skill)
                        else:
                            bottom_skills.append(formatted_skill)
                    return top_skills, bottom_skills


def extract_rw_and_math_skills(report):
    rw_skills = []
    math_skills = []
 
    tabs = report.get("tabs", [])
    target_tab = next((tab for tab in tabs if tab.get("tab_name") == "Accuracy Assessment"), None)
 
    for subject in target_tab.get("subjects", []):
        subject_name = subject.get("subject")
        sections = subject.get("sections", [])
        skill_section = next(
            (sec for sec in sections if sec.get("section_title") == "Skill Performance (Accuracy)"),
            None
        )
 
        skills = skill_section.get("section_details", []) if skill_section else []
       
        if subject_name == "RW":
            rw_skills = skills
        elif subject_name == "Math":
            math_skills = skills
 
    return rw_skills, math_skills

def get_bottom_three_resources(bottom_three_skills):
    bottom_three_resources = []
    for each_skill in bottom_three_skills:
        links = [
            resource["link"]
            for resource in each_skill.get("educational_resources", [])
            if isinstance(resource, dict) and "link" in resource
        ]
        bottom_three_resources.append({each_skill["name"]: links})
    
    return bottom_three_resources


LEVEL_MESSAGES = {
    "fundamental": "- Focus on building foundational understanding with basic concepts and simple practice problems",
    "developing": "- Work with medium-difficulty questions to strengthen core skills and identify common patterns", 
    "proficient": "- Practice challenging problems and complex applications to refine advanced techniques",
    "advanced": "- Master the most difficult question types and work on speed optimization under timed conditions"
}


def get_skills_in_range_with_level_message(skills_data, start, end, skill_accuracy_data):
    def get_accuracy_for_skill(skill_name):
        for item in skill_accuracy_data:
            if item.get("name") == skill_name:
                return item.get("accuracy", None)
        return None  # if not found

    def get_level_message(accuracy):
        if accuracy is None:
            return "(Accuracy data not available)"
        elif accuracy < 50:
            return LEVEL_MESSAGES["fundamental"]
        elif 51 <= accuracy <= 65:
            return LEVEL_MESSAGES["developing"]
        elif 66 <= accuracy <= 80:
            return LEVEL_MESSAGES["proficient"]
        else:  # accuracy > 80
            return LEVEL_MESSAGES["advanced"]

    sorted_skills = sorted(skills_data, key=lambda x: int(x["priority"]))

    selected_skills = sorted_skills[start - 1:end]

    skill_descriptions = []
    for skill in selected_skills:
        skill_name = skill["name"]
        accuracy = get_accuracy_for_skill(skill_name)
        level_message = get_level_message(accuracy)
        skill_descriptions.append(f"{skill_name} {level_message}")

    return skill_descriptions


def get_skill_summary_objects(skills_data, start, end):
    sorted_skills = sorted(skills_data, key=lambda x: int(x["priority"]))

    selected_skills = sorted_skills[start - 1:end]

    skill_summary_objects = []
    for skill in selected_skills:
        summary = ""
        edu_resources = skill.get("educational_resources", [])
        if isinstance(edu_resources, list) and len(edu_resources) > 0:
            summary = edu_resources[0].get("summary", "")

        skill_summary_objects.append({
            "skill_name": skill.get("name", ""),
            "skill_summary": summary
        })

    return skill_summary_objects



def get_skills_in_range(skills_data, start, end):
    sorted_skills = sorted(skills_data, key=lambda x: int(x["priority"]))
 
    selected_skills = sorted_skills[start - 1:end]
 
    skill_names = [skill["name"] for skill in selected_skills]
 
    return skill_names

from datetime import datetime

def get_saturday_activities(foundation_date_range):

    statements = {
        "foundation": "",
        "elevation": "",
        "peak": ""
    }

    statement1 = "Saturdays for concentrating on fundamental concepts through targeted skill-building and conceptual reinforcement"
    statement2 = "Alternating Saturdays: One Saturday for a full-length practice session with comprehensive review, and the next Saturday for concentrating on fundamental concepts through targeted skill-building and conceptual reinforcement."
    statement3 = "Saturdays for 1 full-length practice session followed by comprehensive review of answers and understanding mistakes"
    statement4 = "Saturdays for 2 full-length practice sessions focusing on accuracy and speed optimization, with detailed review and mistake analysis after each session"

    # Helper function to calculate weeks difference
    def get_weeks_difference(date_range_str):
        if not date_range_str:
            return 0
        try:
            start_date_str, end_date_str = date_range_str.split(" - ")
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            return (end_date - start_date).days // 7
        except ValueError:
            return 0 # Handle invalid date range format

    # Foundation Phase
    foundation_weeks = get_weeks_difference(foundation_date_range)
    if foundation_weeks >= 2:
        statements["foundation"] = statement2
    else:
        statements["foundation"] = statement1

    statements["elevation"] = statement3
    statements["peak"] = statement4

    return statements

def split_skills_into_phases(rw_skills_length, math_skills_length):
    def get_phase_ranges(total_skills):
        # Calculate base size and remainder
        base_size = total_skills // 3
        remainder = total_skills % 3

        # Distribute remainder to phases
        foundation_size = base_size + (1 if remainder > 0 else 0)
        elevation_size = base_size + (1 if remainder > 1 else 0)
        peak_size = total_skills - foundation_size - elevation_size

        # Compute ranges with start/end keys
        foundation_start = 1
        foundation_end = foundation_start + foundation_size - 1

        elevation_start = foundation_end + 1
        elevation_end = elevation_start + elevation_size - 1

        peak_start = elevation_end + 1
        peak_end = total_skills

        return {
            "foundation": {
                "start_skill": foundation_start,
                "end_skill": foundation_end
            },
            "elevation": {
                "start_skill": elevation_start,
                "end_skill": elevation_end
            },
            "peak": {
                "start_skill": peak_start,
                "end_skill": peak_end
            }
        }

    return {
        "rw_phases": get_phase_ranges(rw_skills_length),
        "math_phases": get_phase_ranges(math_skills_length)
    }

# Template Function

def generate_template_from_folder(json_data, prompt) -> str:
    
    data = json_data
 
    report_data = data.get("report", {})
 
    student = report_data.get("user", {})
    persona = report_data.get("persona", {})
    report = report_data.get("sat_readiness_report", {})
 
 
    todays_date = datetime.today().strftime('%Y-%m-%d')
 
    rw_skills = extract_skills(report,"RW")         # each rw skill -> priority, name, educational_resources
    math_skills = extract_skills(report,"Math")     # each math skill -> priority, name, educational_resources

    phase_wise_skill_ranges = split_skills_into_phases(len(rw_skills), len(math_skills))
    rw_foundation_skill_start = phase_wise_skill_ranges["rw_phases"]["foundation"]["start_skill"]
    rw_foundation_skill_end = phase_wise_skill_ranges["rw_phases"]["foundation"]["end_skill"]
    rw_elevation_skill_start = phase_wise_skill_ranges["rw_phases"]["elevation"]["start_skill"]
    rw_elevation_skill_end = phase_wise_skill_ranges["rw_phases"]["elevation"]["end_skill"]
    rw_peak_skill_start = phase_wise_skill_ranges["rw_phases"]["peak"]["start_skill"]
    rw_peak_skill_end = phase_wise_skill_ranges["rw_phases"]["peak"]["end_skill"]

    math_foundation_skill_start = phase_wise_skill_ranges["math_phases"]["foundation"]["start_skill"]
    math_foundation_skill_end = phase_wise_skill_ranges["math_phases"]["foundation"]["end_skill"]
    math_elevation_skill_start = phase_wise_skill_ranges["math_phases"]["elevation"]["start_skill"]
    math_elevation_skill_end = phase_wise_skill_ranges["math_phases"]["elevation"]["end_skill"]
    math_peak_skill_start = phase_wise_skill_ranges["math_phases"]["peak"]["start_skill"]
    math_peak_skill_end = phase_wise_skill_ranges["math_phases"]["peak"]["end_skill"]

    rw_skills_accuraccy, math_skills_accuraccy = extract_rw_and_math_skills(report)     # skill name, accuracy

    rw_top_skills , rw_bottom_skills = extract_overall_assessment(report, "RW")
    math_top_skills , math_bottom_skills = extract_overall_assessment(report, "Math")


    rw_top_3, rw_bottom_3, rw_bottom_three_resources = get_top_and_bottom_skills(rw_skills, rw_skills_accuraccy)
    math_top_3, math_bottom_3, math_bottom_three_resources= get_top_and_bottom_skills(math_skills, math_skills_accuraccy)


    rw_foundation_skills_with_level_message = get_skills_in_range_with_level_message(rw_skills, rw_foundation_skill_start, rw_foundation_skill_end, rw_skills_accuraccy)
    rw_elevation_skills_with_level_message = get_skills_in_range_with_level_message(rw_skills, rw_elevation_skill_start, rw_elevation_skill_end, rw_skills_accuraccy)
    rw_peak_skills_with_level_message = get_skills_in_range_with_level_message(rw_skills, rw_peak_skill_start, rw_peak_skill_end, rw_skills_accuraccy)

    rw_foundation_skills = get_skills_in_range(rw_skills, rw_foundation_skill_start, rw_foundation_skill_end)
    rw_elevation_skills = get_skills_in_range(rw_skills, rw_elevation_skill_start, rw_elevation_skill_end)
    rw_peak_skills = get_skills_in_range(rw_skills, rw_peak_skill_start, rw_peak_skill_end)

    rw_top_3_priority_skill_summary_objects = get_skill_summary_objects(rw_skills,1,3)
    rw_foundation_skill_summary_objects = get_skill_summary_objects(rw_skills,rw_foundation_skill_start, rw_foundation_skill_end)
    rw_elevation_skill_summary_objects = get_skill_summary_objects(rw_skills, rw_elevation_skill_start, rw_elevation_skill_end)
    rw_peak_skill_summary_objects = get_skill_summary_objects(rw_skills, rw_peak_skill_start, rw_peak_skill_end)
 
    math_foundation_skills_with_level_message = get_skills_in_range_with_level_message(math_skills, math_foundation_skill_start, math_foundation_skill_end, math_skills_accuraccy)
    math_elevation_skills_with_level_message = get_skills_in_range_with_level_message(math_skills, math_elevation_skill_start, math_elevation_skill_end, math_skills_accuraccy)
    math_peak_skills_with_level_message = get_skills_in_range_with_level_message(math_skills, math_peak_skill_start, math_peak_skill_end, math_skills_accuraccy)

    math_foundation_skills = get_skills_in_range(math_skills, math_foundation_skill_start, math_foundation_skill_end)
    math_elevation_skills = get_skills_in_range(math_skills,math_elevation_skill_start, math_elevation_skill_end)
    math_peak_skills = get_skills_in_range(math_skills, math_peak_skill_start, math_peak_skill_end)

    math_top_3_priority_skills_summary_objects = get_skill_summary_objects(math_skills,1,3)
    math_foundation_skill_summary_objects = get_skill_summary_objects(math_skills, math_foundation_skill_start, math_foundation_skill_end)
    math_elevation_skill_summary_objects  = get_skill_summary_objects(math_skills, math_elevation_skill_start, math_elevation_skill_end)
    math_peak_skill_summary_objects = get_skill_summary_objects(math_skills, math_peak_skill_start, math_peak_skill_end)

    current_level_assessment = get_current_level_assessment(report["sat_score"], student["goal_score"])
 
    result = get_study_plan(report["sat_score"], student["goal_score"], todays_date, student["planned_sat_date"])
    if isinstance(result, str):
        print("Error:", result)
    else:
        foundation, elevation, peak, end_date, duration, flex_duration, tone, fifth_sentence = result

    saturday_activities = get_saturday_activities(foundation)

    foundation_start_date, foundation_end_date = foundation.split(" - ")    
    elevation_start_date, elevation_end_date = elevation.split(" - ")
    peak_start_date, peak_end_date = peak.split(" - ")

    target_end_date = student["planned_sat_date"]
    planned_date = datetime.strptime(student["planned_sat_date"], "%Y-%m-%d").date()
    peak_date = datetime.strptime(peak_end_date, "%Y-%m-%d").date()

    if planned_date != peak_date:
        target_end_date = peak_end_date

    goal_achievability_assessment = get_goal_achievability_assessment(report["sat_score"], student["goal_score"],target_end_date)
 
    template_data = {
        "student_name": student['preferred_name'],
        "planned_sat_date": target_end_date,
        "today_date": todays_date,
        "persona_name": persona["persona_name"],
        "persona_strengths": list_to_numbered_string(persona["key_strengths"]),
        "persona_challenges": list_to_numbered_string(persona["areas_of_improvement"]),
        "growth_strategies": persona["growth_strategies"],
        "current_sat_score_total":report["sat_score"],
        "current_sat_accuracy": report["accuracy_index"],
        "current_sat_time_management": report["time_management"],
        "goal_score": student["goal_score"],
        "tone":tone,

        "math_top_3": list_to_numbered_string(math_top_3),
        "math_bottom_3": list_to_numbered_string(math_bottom_3),
        "math_bottom_three_resources": math_bottom_three_resources,

        "rw_top_3": list_to_numbered_string(rw_top_3),
        "rw_bottom_3": list_to_numbered_string(rw_bottom_3),
        "rw_bottom_three_resources":rw_bottom_three_resources,

        "foundation_date_range": foundation,
        "elevation_date_range": elevation,
        "peak_date_range": peak,
    
        "foundation_start_date": foundation_start_date,
        "foundation_end_date": foundation_end_date,
        "elevation_start_date": elevation_start_date,
        "elevation_end_date": elevation_end_date,
        "peak_start_date": peak_start_date,
        "peak_end_date": peak_end_date,

        "rw_foundation_skills": rw_foundation_skills,
        "rw_elevation_skills": rw_elevation_skills,
        "rw_peak_skills": rw_peak_skills,
        "rw_foundation_skill_summary_objects": rw_foundation_skill_summary_objects,
        "rw_elevation_skill_summary_objects": rw_elevation_skill_summary_objects,
        "rw_peak_skill_summary_objects": rw_peak_skill_summary_objects,
        "rw_foundation_skills_with_level_message": list_to_numbered_string(rw_foundation_skills_with_level_message),
        "rw_elevation_skills_with_level_message": list_to_numbered_string(rw_elevation_skills_with_level_message),
        "rw_peak_skills_with_level_message": list_to_numbered_string(rw_peak_skills_with_level_message),

        "math_foundation_skills": math_foundation_skills,
        "math_elevation_skills": math_elevation_skills,
        "math_peak_skills": math_peak_skills,
        "math_foundation_skill_summary_objects": math_foundation_skill_summary_objects,
        "math_elevation_skill_summary_objects": math_elevation_skill_summary_objects,
        "math_peak_skill_summary_objects": math_peak_skill_summary_objects,
        "math_foundation_skills_with_level_message": list_to_numbered_string(math_foundation_skills_with_level_message),
        "math_elevation_skills_with_level_message": list_to_numbered_string(math_elevation_skills_with_level_message),
        "math_peak_skills_with_level_message": list_to_numbered_string(math_peak_skills_with_level_message),

        "rw_skills_accuraccy": rw_skills_accuraccy,
        "math_skills_accuraccy": math_skills_accuraccy,
        "rw_top_3_priority_skill_summary_objects": rw_top_3_priority_skill_summary_objects,
        "math_top_3_priority_skills_summary_objects": math_top_3_priority_skills_summary_objects,

        "current_level_assessment": current_level_assessment,
        "goal_achievability_assessment": goal_achievability_assessment,
        "rw_top_skills":rw_top_skills,
        "rw_bottom_skills": rw_bottom_skills,
        "math_top_skills":math_top_skills,
        "math_bottom_skills": math_bottom_skills,
        "foundational_saturday_activity":saturday_activities["foundation"],
        "elevation_saturday_activity":saturday_activities["elevation"],
        "peak_saturday_activity":saturday_activities["peak"],

    } 
    return prompt.format(**template_data)
 
# Invoke LLM

def invoke_llm_with_prompt(prompt: str, json_data) -> dict:
    formatted_prompt = generate_template_from_folder(json_data, prompt)
    response = llm.invoke(formatted_prompt)
    content = response.content if hasattr(response, "content") else response
    return json.loads(content)

# Wrapper Method

def wrapper(prompt, json_data):
    result = invoke_llm_with_prompt(prompt, json_data)
    prompt_name = ''

    if prompt == EXECUTIVE_SUMMARY_PROMPT:
        prompt_name = "executive_summary"
    elif prompt == FOUNDATION_PHASE_PROMPT:
        prompt_name = "foundation_pahse"
    elif prompt == ELEVATION_PHASE_PROMPT:
        prompt_name = "elevation_phase"
    elif prompt == PEAK_PHASE_PROMPT:
        prompt_name = "peak_phase"
    elif prompt == TIPS_TO_MAKE_IT_WORK_BEST_PROMPT:
        prompt_name = "tips"
    elif prompt == WORDS_OF_ENCOURAGEMENT:
        prompt_name = "words_of_encouragement"

    return (result, prompt_name)

#Parallel Processing

from concurrent.futures import ThreadPoolExecutor, as_completed
import time  # for timing and simulation (if needed)

def invoke_and_save_response(json_data) -> dict:
    prompts = [
        EXECUTIVE_SUMMARY_PROMPT,
        FOUNDATION_PHASE_PROMPT,
        ELEVATION_PHASE_PROMPT,
        PEAK_PHASE_PROMPT,
        TIPS_TO_MAKE_IT_WORK_BEST_PROMPT,
        WORDS_OF_ENCOURAGEMENT
    ]

    start = time.time()

    # Initialize result variables

    with ThreadPoolExecutor(max_workers=len(prompts)) as executor:
        futures = [executor.submit(wrapper, prompt, json_data)
                   for prompt in prompts]

        for future in as_completed(futures):
            
            result, prompt_name = future.result()

            if prompt_name == "executive_summary":
                EXECUTIVE_SUMMARY = result
            elif prompt_name == "foundation_pahse":
                FOUNDATION_PHASE = result
            elif prompt_name == "elevation_phase":
                ELEVATION_PHASE = result
            elif prompt_name == "peak_phase":
                PEAK_PHASE = result
            elif prompt_name == "tips":
                TIPS_TO_MAKE_IT_WORK_BEST = result
            elif prompt_name == "words_of_encouragement":
                THIS_JOURNEY_OF_YOURS = result

    end = time.time()
    print(f"All prompts completed in {end - start:.2f} seconds")
    response = {
        "EXECUTIVE_SUMMARY": EXECUTIVE_SUMMARY,
        "FOUNDATION_PHASE": FOUNDATION_PHASE,
        "ELEVATION_PHASE": ELEVATION_PHASE,
        "PEAK_PHASE": PEAK_PHASE,
        "TIPS_TO_MAKE_IT_WORK_BEST": TIPS_TO_MAKE_IT_WORK_BEST,
        "THIS_JOURNEY_OF_YOURS": THIS_JOURNEY_OF_YOURS
    }
    return response


folders = ["Jevinn"]#,"Lakshmi", "Meenakshi", "RohanBharathwaj","SaiSaahas", "Tara", "Toni","Vaishnavi", "Zoha"]#,"RohanByali", "Aarthi", "Abhinav", "Amrita", "Anirudh", "GouriPradeep", "GovindPotti", "Ishan", "IshanaPotti"]



with open(r"C:\Users\Manideep S\Downloads\L@\SAT Paid Report\Users_data\Aarthi\Input_data.json", "r") as f:
    json_data = json.load(f)

response = invoke_and_save_response(json_data)

EXECUTIVE_SUMMARY = response["EXECUTIVE_SUMMARY"]

FOUNDATION_PHASE = response["FOUNDATION_PHASE"]

ELEVATION_PHASE = response["ELEVATION_PHASE"]

PEAK_PHASE_PROMPT = response["PEAK_PHASE"]

TIPS_TO_MAKE_IT_WORK_BEST = response["TIPS_TO_MAKE_IT_WORK_BEST"]

THIS_JOURNEY_OF_YOURS = response["THIS_JOURNEY_OF_YOURS"]

STATIC_CTA = STATIC_CTA

FOOTER = FOOTER

print(f"""
{EXECUTIVE_SUMMARY}\n{FOUNDATION_PHASE}\n{ELEVATION_PHASE}\n{PEAK_PHASE_PROMPT}\n{TIPS_TO_MAKE_IT_WORK_BEST}\n{THIS_JOURNEY_OF_YOURS}\n{STATIC_CTA}\n{FOOTER}""")


