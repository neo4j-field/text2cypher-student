# Professional Services Retreat | GenAI Workshop

## Background

This workshop is based on the `ps-genai-agents` intenral project. `ps-genai-agents` refactors and builds on the work done for the Honda GenAI POC and aims to develop LLM agents that are able to work with a variety of datasets. 

These agents are built using the `LangGraph` library which lets us define workflows within a graph architecture. These workflows may contain a variety of retrieval tools such as vector search and Text2Cypher. We may also implement tools for tasks such as generating charts or domain-specific word look ups.

You can find the project on GitHub [here](https://github.com/neo4j-field/ps-genai-agents)

## Dependency Set Up

In order to run the code in this workshop we will have to install `Python 3.10` or greater and `Poetry` to manage our dependencies. We also use `Graphviz` to visualize our agent architecture. While this isn't required, it's useful in understanding how agents work.


### Python

We'll need `Python` $\ge$ 3.10 to run the project.

To install `Python` click on this [link](https://www.python.org/downloads/) and follow the instructions on the page.

### Poetry

This project uses `Poetry` to manage dependencies. 

You can find the install instructions [here](https://python-poetry.org/docs/#installing-with-pipx)

### Graphviz

`Graphviz` is optional and only required to visualize the graph architecture. If you skip this install, then make sure to skip any notebook cells that handle visualization.

You can find install instructions [here](https://graphviz.org/download/)

Once installed we can install the `Python` package `pygraphviz`. 

For Mac we can run the following command from the Terminal: (Assumes `Poetry` installed)

```
poetry run python3 -m pip install -U --no-cache-dir  \
            --config-settings="--global-option=build_ext" \
            --config-settings="--global-option=-I$(brew --prefix graphviz)/include/" \
            --config-settings="--global-option=-L$(brew --prefix graphviz)/lib/" \
            pygraphviz
```

For Windows / Linux - you'll have to do some research on how to properly install this. `¯\_(ツ)_/¯`

## Workshop Set Up

Once we have `Python` and `Poetry` installed, we can install our project dependencies. 

Run either of the following from the command line to install dependencies to a `Poetry` managed virtual environment. 

```
make workshop
```

OR 

```
poetry install --with ui
```

`ps-genai-agents` uses a `Makefile`  to organize initialization, formatting and testing. Both of the above commands will perform the same function. 

If we don't receive any errors then we can continue to the next step.


