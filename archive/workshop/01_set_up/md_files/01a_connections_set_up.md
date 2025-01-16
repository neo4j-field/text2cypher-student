# Professional Services Retreat | GenAI Workshop

## Background

This workshop is based on the `ps-genai-agents` intenral project. `ps-genai-agents` refactors and builds on the work done for the Honda GenAI POC and aims to develop LLM agents that are able to work with a variety of datasets.

These agents are built using the `LangGraph` library which lets us define workflows within a graph architecture. These workflows may contain a variety of retrieval tools such as vector search and Text2Cypher. We may also implement tools for tasks such as generating charts or domain-specific word look ups.

You can find the project on GitHub [here](https://github.com/neo4j-field/ps-genai-agents)

## .env File

Ensure that you've place the provided `.env` file in the project root directory. This will allow the project to connect to both the IQS and Patient Journey Aura instances. It also contains an OpenAI API key that we will be using. This key will only be valid for the duration of the retreat.
