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

### Running the Systems
```bash
# Run COMPLETE agentic system (RECOMMENDED)
python main_agentic.py

# Run demo mode with predefined topic
python main_agentic.py demo

# Test complete system functionality
python test_agentic_system.py

# Run legacy system (basic version)
python main.py

# Test legacy system
python test_system.py
```

### Python Environment
- Python 3.11.6
- Uses virtual environment in `langgraph_env/`

## Architecture Overview

This is a **complete multi-agent research system** that solves the Smart Content Research Assistant challenge using LangGraph with 4 specialized agents and smart cost optimization.

### Complete Challenge Solution

**🎯 Challenge Requirements Met:**
- ✅ Multi-agent architecture with LangGraph  
- ✅ Human-in-the-loop validation with console commands
- ✅ Smart cost optimization (3 model tiers based on task complexity)
- ✅ Complete workflow: Research → Curation → Reporting
- ✅ Web search integration (Wikipedia + mock web sources)
- ✅ Structured markdown report generation

### Agent Architecture

**SupervisorAgent (Project Coordinator)**
- Orchestrates complete workflow across 6 stages
- Manages human validation with rich command interface
- Routes tasks to appropriate agents based on complexity

**InvestigatorAgent (Research Specialist)**  
- Generates initial research outlines using cost-optimized models
- Creates structured 6-element research frameworks
- Handles user feedback integration

**CuratorAgent (Content Analyst)**
- Performs deep analysis of approved research elements
- Integrates multi-source web research (Wikipedia + web)
- Synthesizes insights and generates analysis reports

**ReporterAgent (Report Writer)**
- Generates professional markdown reports with premium models
- Creates executive summaries, detailed analysis, and recommendations
- Includes quality assessment and structured formatting

### Smart Cost Optimization

**Cost Optimizer System (`research_agent/tools/cost_optimizer.py`)**
- **Simple tasks** → `gpt-3.5-turbo` (outlines, summaries)
- **Medium tasks** → `gpt-4o-mini` (research, analysis)  
- **Complex tasks** → `gpt-4` (final reports, synthesis)
- Dynamic model selection based on task type and content length
- Real-time cost estimation and optimization logging

### State Management

**AgenticResearchState** (Enhanced state for complete workflow)
- Comprehensive tracking: decisions, quality metrics, inter-agent messages
- Research context with synthesis notes and source management
- Strategic context for workflow optimization

**Legacy ResearchState** (Basic validation workflow)
- Simple outline approval workflow
- Maintained for backward compatibility

### Web Search Integration

**WebSearchClient (`research_agent/tools/web_search.py`)**
- Wikipedia API integration for academic sources
- Mock web search (Tavily-ready for production)
- Multi-source result aggregation and summarization
- Comprehensive search with source attribution

### Workflow Stages

**Complete Agentic Workflow (`research_agent/workflows/agentic_workflow.py`)**
1. **Topic Collection** - Interactive topic specification
2. **Outline Generation** - Investigator creates research framework  
3. **Human Validation** - Rich command interface (approve, modify, reject)
4. **Content Curation** - Deep analysis with web search integration
5. **Report Generation** - Professional markdown report with metrics
6. **Completion** - Quality assessment and file export options

### Human-in-the-Loop Commands

**Interactive Validation Interface:**
- `approve` - Approve complete outline
- `approve 1,3,5` - Approve specific elements
- `remove 2,4` - Remove unwanted elements  
- `change 1 to "new title"` - Modify element titles
- `add "new element"` - Add additional research areas
- `reject` - Regenerate complete outline

### Configuration

**Settings (`research_agent/config/settings.py`)**
- OpenAI API key validation and model configuration
- Cost optimization parameters
- Agent retry and timeout settings

### Key Dependencies

- **langgraph**: Multi-agent workflow orchestration
- **openai**: GPT integration with cost optimization
- **wikipedia**: Academic source integration  
- **requests**: Web search capabilities
- **beautifulsoup4**: HTML parsing for web sources

## Development Notes

### Running the System
- Complete system: `python main_agentic.py`
- All tests must pass: `python test_agentic_system.py`
- Requires OPENAI_API_KEY environment variable
- Interactive console-based operation (no web UI)

### Architecture Patterns
- Immutable state management across agent transitions
- Cost-aware model selection for each task type
- Comprehensive error handling with fallback strategies
- Quality metrics and workflow optimization tracking

### Testing Strategy
- Component-level tests for all agents and tools
- Integration tests for complete workflow
- Cost optimization validation
- Web search functionality verification

This system fully implements the Smart Content Research Assistant challenge requirements with a production-ready multi-agent architecture.