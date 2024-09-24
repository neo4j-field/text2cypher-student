import warnings

from langchain.prompts import PromptTemplate

from .queries import get_example_queries


def create_cypher_prompt(
    graph_schema: str,
    examples_yaml_path: str = "queries/queries.yml",
) -> str:
    """
    Construct the prompt template for text2cypher generation.
    This prompt should be used with the GraphCypherQAChain LangChain class.

    Parameters
    ----------
    examples_yaml_path : str
        The path to a YAML file containing examples. By default = queries/queries.yml

    Returns
    -------
    FewShotPromptTemplate
        The final cypher prompt.
    """

    example_prompt = PromptTemplate(
        input_variables=["human", "assistant"],
        template="Human: {human}\nAssistant: {assistant}\n\n",
    )

    examples = get_example_queries(file_path=examples_yaml_path)

    if len(examples) < 1:
        warnings.warn("No Cypher examples found for Cypher prompt.")

    prefix = f"""You are an expert Neo4j Cypher translator who understands the question in english and convert to Cypher strictly based on the Neo4j Schema provided and following the instructions below:
    <instructions>
    * Use aliases to refer the node or relationship in the generated Cypher query
    * Generate Cypher query compatible ONLY for Neo4j Version 5
    * Do not use EXISTS in the cypher. Use alias when using the WITH keyword
    * Only use SIZE when checking the size of a list
    * Use only Nodes and relationships mentioned in the schema
    * Always do a case-insensitive and fuzzy search for any properties related search. Eg: to search for a Company name use `toLower(c.name) contains 'neo4j'`
    * Cypher is NOT SQL. So, do not mix and match the syntaxes
    * Ensure that null results are filtered out before running aggregations!
    * Do not include any header
    * Do not wrap in backticks (```)
    * Return only Cypher
    </instructions>

    Strictly use this Schema for Cypher generation:
    <schema>
    {graph_schema}
    </schema>

    The samples below follow the instructions and the schema mentioned above. So, please follow the same when you generate the cypher:
    <samples>

    """

    suffix = """</samples>

    Human: {query_text}
    Assistant:
    """

    examples_str = ""
    for ex in examples:
        examples_str += example_prompt.format(**ex)

    return f"""{prefix}
{examples_str}
{suffix}"""
