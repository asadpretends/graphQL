# LLM-Powered GraphQL Agent

This project provides a service that translates natural language queries into GraphQL requests against a Jobs API and returns the results in human-readable text.

## Features

- Translates natural language to GraphQL queries using OpenAI's language models
- Executes GraphQL queries against the provided Jobs API
- Returns formatted, human-readable responses
- Packaged as a Docker container for easy deployment

## Setup & Installation

### Prerequisites

- Python 3.9+
- Docker Desktop (for container build and run)
- OpenAI API key (Azure-based)

### Environment Variables

Create a `.env` file based on the provided `.env.example`:

