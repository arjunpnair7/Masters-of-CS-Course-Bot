# AIzaSyDTut2h63P0E3ERSwYmG2IzwHIUPQGqsho

import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key='AIzaSyDTut2h63P0E3ERSwYmG2IzwHIUPQGqsho'
,temperature=0.001)


CYPHER_PROMPT = """

I have given schema information below.  First, extract important keywords and phrases from the students query that relate to computer science topics. 


Second, replace the extracted keywords with a generalized form to result in a better search. Replace phrases with the base form of each individual word.

For example, replacing 'car' with the word 'vehicle' or 'vehicles' is a good idea. For example, replacing a very specific phrase like 'self-driving' with 'autonomous' is a good idea.

Third, decide an appropriate value for the categories field based on the instruction given in the schema section.

Fourth, please generate an appropriate cypher query based on the student query which will be given below. As part of the cypher query, check to see if the keywords exist in the course name and course description. Only check if the keywords exist in description and name, never do that for any other field. USE OR RATHER THAN AND.

Schema:

There are no relationships in graph. There are course nodes with the following property labels:
category, course name, course number, credits, description, link, prereq, breadth, depth.


For the categories field, these are the only available categories. Map the user's request to one of the categories below where each line is a category. Always include the N/A category in your query as well. Map the user's request to one of these categories. Always refer to the category by using the full string.

For example, n.category = 'Architecture, Compilers, Parallel Computing' is okay but n.category = 'Compilers, Parallel Computing' is unacceptable:

'Architecture, Compilers, Parallel Computing'
'Artificial Intelligence'
'Bioinformatics and Computational Biology'
'Computers and Education'
'Database and Information Systems'
'Interactive Computing'
'Programming Languages, Formal Methods, Software Engineering'
'Scientific Computing'
'Security and Privacy'
'Systems and Networking'
'Theoretical Computer Science'
'N/A'

Examples:

'Can you reccomend some functional programming courses?':

MATCH (Course:Course)
WHERE Course.category = 'Programming Languages, Formal Methods, Software Engineering' OR Course.category = 'N/A'
RETURN Course.category, Course.`course name`, Course.`course number`, Course.credits, Course.description, Course.link, Course.prereq, Course.breadth, Course.depth

'Can you reccomend some NLP courses?'

MATCH (Course:Course)
WHERE Course.category = 'Artificial Intelligence' OR Course.category = 'N/A'
RETURN Course.category, Course.`course name`, Course.`course number`, Course.credits, Course.description, Course.link, Course.prereq, Course.breadth, Course.depth

For 500 level classes, do not filter on category and only look for range 500 to 599. Example:

'Give me some 500 level AI courses'

MATCH (Course:Course)
WHERE Course.`course number` >= 'CS500' AND Course.`course number` <= 'CS599'
RETURN Course.category, Course.`course name`, Course.`course number`, Course.credits, Course.description, Course.link, Course.prereq, Course.breadth, Course.depth



If you are unsure about the mapping, just return all of the courses.

Question:
{query}

"""

cypher_generation_prompt = PromptTemplate(
    template=CYPHER_PROMPT,
    input_variables=["question"],
)

graph = Neo4jGraph(
    url="neo4j+s://a6901ded.databases.neo4j.io",
    username="neo4j",
    password="xEGNhX6aYUxJtIZ-FKoOtGzJYSA7qr8igqdq1cljQ34",
)

cypher_chain = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    cypher_prompt=cypher_generation_prompt,
    verbose=True,
    return_intermediate_steps=True
)



# cypher_result = cypher_chain.invoke({"query": "I am kind of interested in cybersecurity and artificial intelligence. Can you recommend some courses?"})


# Create the analysis prompt
ANALYSIS_PROMPT = """

Instructions:
Pretend that you are a friendly, optimistic college advisor advising students on courses on a masters of computer science program. You are provided all relevant course information under the Course Information section of this prompt. 

Extract generalized forms of the keywords and phrases from the student's query and compare with the course description to determine the course reccomendations most relevent to the student's query.


All student queries are in the context of computer science.

If you cannot find an exact match, generalize the user's request and return those types of requests. If you do this, notify the user.

ALWAYS give the course reccomendations using the following template. This template data should only be filled in based on the course information provided to you. DO NOT USE YOUR PRIOR TRAINING DATA FOR THIS:

[Course number] - [Course Name]
[Link to course]
[Amount of credit cours] credit hours
Prereq: [Course prereqs]
Category: [Course Category]
Reason: [Justification fo reccomending this course]

...

Notes:


At the beginning of each response, rephrase their prompt. Always include any prerequisites for your reccomendations. Your response should be exclusively based on the data provided to you in the 'Course Information' section.


Student query:

{question}


Course Information: 
{info}

"""

analysis_prompt = ChatPromptTemplate.from_template(ANALYSIS_PROMPT)
prompt = "Tell me some courses that can teach me about reinforcement learning"
# Create a composed chain with piping
composed_chain = (
    cypher_chain 
    | (lambda output: {'info': output, "question": output['query']})
    | analysis_prompt 
    | llm 
    | StrOutputParser()
)

# Invoke the composed chain
results = composed_chain.invoke({"query": prompt})
print(results)

print("\n\n")

# print(cypher_result)