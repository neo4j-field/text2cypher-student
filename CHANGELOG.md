## Next

### Fixed

### Changed

* `CypherQuery` nodes are now removed from graph schema when generating Cypher
* All graphs and subgraphs have Input, Main and Output states

### Added

* Add validator to prevent write clauses from being executed during Text2Cypher
* Add final answer validator node that will send generated follow up questions to fill gaps in the response
