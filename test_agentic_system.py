"""
Script de prueba para verificar el sistema agéntico completo
"""
import os
import sys

def test_imports():
    """Prueba que todos los módulos se puedan importar correctamente"""
    print("🧪 Testing imports...")
    
    try:
        # Test cost optimizer
        from research_agent.tools.cost_optimizer import CostOptimizer
        print("✅ CostOptimizer imported")
        
        # Test web search
        from research_agent.tools.web_search import WebSearchClient
        print("✅ WebSearchClient imported")
        
        # Test all agents
        from research_agent.agents.supervisor import SupervisorAgent
        from research_agent.agents.investigator import InvestigatorAgent
        from research_agent.agents.curator import CuratorAgent
        from research_agent.agents.reporter import ReporterAgent
        print("✅ All agents imported")
        
        # Test agentic state
        from research_agent.models.agentic_state import AgenticResearchState
        print("✅ AgenticResearchState imported")
        
        # Test agentic workflow
        from research_agent.workflows.agentic_workflow import AgenticResearchWorkflow
        print("✅ AgenticResearchWorkflow imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_cost_optimizer():
    """Prueba el sistema de optimización de costos"""
    print("\n🧪 Testing cost optimizer...")
    
    try:
        from research_agent.tools.cost_optimizer import CostOptimizer
        
        # Test different task types
        tasks = ["outline", "research", "analysis", "report"]
        for task in tasks:
            model = CostOptimizer.get_optimal_model(task)
            cost = CostOptimizer.estimate_cost(task, 1000)
            print(f"   {task}: {model} (${cost:.4f} for 1K tokens)")
        
        print("✅ Cost optimizer working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Cost optimizer error: {e}")
        return False

def test_web_search():
    """Prueba el sistema de búsqueda web"""
    print("\n🧪 Testing web search...")
    
    try:
        from research_agent.tools.web_search import WebSearchClient
        
        client = WebSearchClient()
        
        # Test Wikipedia search
        results = client._search_wikipedia("artificial intelligence", 2)
        print(f"   Wikipedia found {len(results)} results")
        
        # Test comprehensive search
        search_results = client.search_comprehensive("machine learning", 2)
        print(f"   Comprehensive search: {search_results['summary']}")
        
        print("✅ Web search working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Web search error: {e}")
        return False

def test_agents_creation():
    """Prueba la creación de todos los agentes"""
    print("\n🧪 Testing agent creation...")
    
    try:
        from research_agent.agents.supervisor import SupervisorAgent
        from research_agent.agents.investigator import InvestigatorAgent
        from research_agent.agents.curator import CuratorAgent
        from research_agent.agents.reporter import ReporterAgent
        
        # Create all agents
        supervisor = SupervisorAgent()
        investigator = InvestigatorAgent()
        curator = CuratorAgent()
        reporter = ReporterAgent()
        
        print(f"   ✅ {supervisor.name} created")
        print(f"   ✅ {investigator.name} created")
        print(f"   ✅ {curator.name} created")
        print(f"   ✅ {reporter.name} created")
        
        print("✅ All agents created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Agent creation error: {e}")
        return False

def test_workflow_creation():
    """Prueba la creación del workflow agéntico"""
    print("\n🧪 Testing workflow creation...")
    
    try:
        from research_agent.workflows.agentic_workflow import AgenticResearchWorkflow
        
        workflow = AgenticResearchWorkflow()
        print(f"   ✅ Workflow created with {len(workflow.workflow.nodes)} nodes")
        
        # Test workflow summary
        summary = workflow.get_workflow_summary()
        print(f"   ✅ Workflow has {len(summary['agents'])} agents")
        print(f"   ✅ Workflow has {len(summary['workflow_stages'])} stages")
        
        print("✅ Workflow creation successful")
        return True
        
    except Exception as e:
        print(f"❌ Workflow creation error: {e}")
        return False

def test_configuration():
    """Prueba la configuración del sistema"""
    print("\n🧪 Testing configuration...")
    
    try:
        from research_agent.config.settings import Settings
        
        # Check if API key is configured
        if Settings.OPENAI_API_KEY:
            print("   ✅ OpenAI API Key configured")
        else:
            print("   ⚠️  OpenAI API Key not configured (expected for testing)")
        
        print(f"   ✅ Model: {Settings.OPENAI_MODEL}")
        print(f"   ✅ Max retries: {Settings.MAX_RETRIES}")
        print(f"   ✅ Timeout: {Settings.TIMEOUT}")
        
        print("✅ Configuration accessible")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Función principal de testing"""
    print("🚀 TESTING AGENTIC RESEARCH SYSTEM")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Cost Optimizer", test_cost_optimizer),
        ("Web Search", test_web_search),
        ("Agent Creation", test_agents_creation),
        ("Workflow Creation", test_workflow_creation),
        ("Configuration", test_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        print("\n💡 To run the complete system:")
        print("   python main_agentic.py")
        print("\n💡 To run demo mode:")
        print("   python main_agentic.py demo")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\n🔧 Common issues:")
        print("   - Make sure OPENAI_API_KEY is configured if you want to test with real API")
        print("   - Check that all dependencies are installed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)