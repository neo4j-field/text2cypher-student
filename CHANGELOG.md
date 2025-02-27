## Next

### Fixed

* Fixed bugs in Cypher query vector store creation
* Fixed bug in Cypher query sim search retriever

### Changed

* `CypherQuery` nodes are now removed from graph schema when generating Cypher
* All graphs and subgraphs have Input, Main and Output states
* Make all agent workflow nodes async
* rename `query_parser` node to `planner` node
* Tool Selection node now uses LLM to decide which tool to use

### Added

* Add validator to prevent write clauses from being executed during Text2Cypher
* Add final answer validator node that will send generated follow up questions to fill gaps in the response
* Add LangGraph Studio implementation
* Add Similarity Search for Cypher example retrieval in the `adv_t2c_with_viz.ipynb` example
* updated README
* Add ingest code and embeddings data for IQS data
* Add BBC Good Food recipes data
* Add support for generic Cypher executor
    * This enables pre written Cypher tools to be used
* Add example notebook demonstrating the multi tool agent with Text2Cypher and predefined Cypher tools
