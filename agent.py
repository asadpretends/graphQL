import os
import logging 
import requests
from typing import Dict,List,Any,Optional
from dotenv import load_dotenv
from langchain_openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from langchain.schema import HumanMessage, SystemMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

prompt = """

        You are an agent that translates natural language queries into GraphQL queries.
        You have access to a Jobs API with the following schema:

        {schema}

        Translate the following natural language query into a valid GraphQL query:
        query : {query}

        First, think through what information is being requested and what fields you need to access.
        Then, construct a proper GraphQL query that will retrieve the necessary information.
        Return only the final GraphQL query without explanation.
         """

class GraphQLAgent:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY","api-key")
        api_version = os.getenv("OPENAI_API_VERSION")
        endpoint = os.getenv("OPENAI_API_ENDPOINT")

        self.credentials = AzureKeyCredential(api_key)
        
        self.llm = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
            azure_ad_token_provider=self.credentials,
            temperature=0,
        )

        self.graphql_url = os.getenv("GRAPHQL_API_URL")
        self.schema = self.fetch_schema()

    
    def fetch_schema(self) -> str:
        
        try:
            schema_url = "https://jluatgraphqlapi-atc2asbnb5gxbehw.westeurope-01.azurewebsites.net/graphql-v2/schema.graphql"
            response = requests.get(schema_url)
            response.raise_for_status()

            return response.text
        
        except Exception as e:
            logger.error(f"Failed to fetch GraphQL schema: {e}")

    def generate_graphql_query(self, query:str) -> str:

        system_message = f"""
        You are an expert GraphQL query builder.
        Your task is to translate natural language qustions into valid GraphQL queries.
        Use the following GraphQL schema:

        {self.schema}

        Return only the valid GraphQL query without any explanation.
        """

        messages = [

            SystemMessage(content=system_message),
            HumanMessage(content=f"Question: {query}")

        ]

        response = self.llm.invoke(messages)

        query_text = response.content

        logger.info(f"Generated GraphQL query: {query_text}")

        return query_text
    
    def execute_graphql_query(self, query:str) -> Dict[str, Any]:

        try:
            response = requests.post(
                self.graphql_url,
                json={"query": query},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Failed to execute GraphQL query: {e}")
            
            return {"error": f"Failed to execute query: {str(e)}"}
        
    def format_response(self, data: Dict[str, Any], query:str) -> str:

        system_message = """
        You are a helpful assistant that formats GraphQL API responses into human-readable text.
        Provide a concise summary of the data, focusing on the key information requested.
        Make sure your response is natural, conversational, and directly answers the original question.                        
                        """
        
        data_str = str(data)
        
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=f"Orignal question: {query}\n API response data: {data_str}")        
                    ]
        response = self.llm.invoke(messages)
        
        return response.content
    
    def process_query(self, query: str) -> Dict[str,str]:
        
        try:
            graphql_query = self.generate_graphql_query(query)

            result = self.execute_graphql_query(graphql_query)

            answer = self.format_response(result,query)

            return {"answer": answer}
        
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {"answer": f"Sorry, Error Encountered: {str(e)}"}