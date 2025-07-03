# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up OpenAI API key (required)
export OPENAI_API_KEY="your-api-key-here"
```

### Running the System
```bash
# Run main application
python main.py

# Test system functionality
python test_system.py
```

### Python Environment
- Python 3.11.6
- Uses virtual environment in `langgraph_env/`

## Architecture Overview

This is a multi-agent research system built with LangGraph that uses OpenAI GPT-4 for intelligent research and content generation.

### Core Components

**State Management (research_agent/models/state.py)**
- `ResearchState`: TypedDict defining shared state across all agents
- Tracks user queries, research outlines, approvals, and results

**Agent System (research_agent/agents/)**
- `BaseAgent`: Abstract base class with logging functionality
- `SupervisorAgent`: Coordinates workflow decisions and agent routing
- `InvestigatorAgent`: Generates research outlines and conducts detailed research using OpenAI

**Workflow Engine (research_agent/workflows/research_workflow.py)**
- Uses LangGraph StateGraph for orchestrating agent interactions
- Implements conditional routing based on state
- Includes human approval node for research outline validation

**OpenAI Integration (research_agent/tools/openai_client.py)**
- Handles OpenAI API calls with error handling
- Configured for GPT-4 model with system prompts for research expertise

### Workflow Flow

1. **Supervisor** receives user query and decides next action
2. **Investigator** generates structured research outline
3. **Human Approval** validates/approves the outline (interactive input)
4. **Investigator** conducts detailed research based on approved outline
5. **Supervisor** finalizes process and displays results

### Configuration

Settings are centralized in `research_agent/config/settings.py`:
- OpenAI API key validation
- Model configuration (default: gpt-4)
- Retry and timeout settings

### Key Dependencies

- **langgraph**: Workflow orchestration with state graphs
- **openai**: GPT-4 integration for research generation
- **requests**: HTTP client functionality
- **beautifulsoup4**: HTML parsing capabilities

## Development Notes

- The system requires OPENAI_API_KEY environment variable
- Interactive human approval is built into the workflow
- Error handling includes fallback research outlines
- All agents inherit from BaseAgent for consistent logging
- State is immutable and passed between agents via StateGraph