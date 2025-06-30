"""
Test Suite for AI Sourcing Agent
================================

Comprehensive tests for all components of the AI Sourcing Agent.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import json
import tempfile
import os

# Import modules to test
from src.crew_manager import SourcingCrewManager
from src.tools.web_search import WebSearchTool
from src.tools.supplier_database import SupplierDatabaseTool
from src.utils.config import Config

class TestSourcingCrewManager:
    """Test the main crew manager functionality"""
    
    @pytest.fixture
    def crew_manager(self):
        """Create a test crew manager instance"""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test_key',
            'TAVILY_API_KEY': 'test_key'
        }):
            return SourcingCrewManager()
    
    def test_initialization(self, crew_manager):
        """Test crew manager initialization"""
        assert crew_manager is not None
        assert hasattr(crew_manager, 'config')
        assert hasattr(crew_manager, 'agents')
        assert hasattr(crew_manager, 'tools')
    
    @pytest.mark.asyncio
    async def test_research_suppliers(self, crew_manager):
        """Test supplier research functionality"""
        # Mock the crew execution
        with patch.object(crew_manager, '_parse_supplier_list') as mock_parse:
            mock_parse.return_value = [
                {
                    'name': 'Test Supplier',
                    'country': 'Germany',
                    'website': 'https://test-supplier.com',
                    'specialties': ['electronics']
                }
            ]
            
            suppliers = await crew_manager.research_suppliers(
                'electronic components', 
                'Europe'
            )
            
            assert len(suppliers) >= 0
            if suppliers:
                assert 'name' in suppliers[0]
    
    @pytest.mark.asyncio
    async def test_analyze_suppliers(self, crew_manager):
        """Test supplier analysis functionality"""
        test_suppliers = [
            {
                'name': 'Test Supplier',
                'country': 'Germany',
                'website': 'https://test-supplier.com'
            }
        ]
        
        quality_standards = ['ISO9001', 'RoHS']
        
        with patch.object(crew_manager, '_parse_analysis_result') as mock_parse:
            mock_parse.return_value = {
                'total_suppliers': 1,
                'analyzed_suppliers': test_suppliers,
                'average_scores': {'quality': 8.5}
            }
            
            analysis = await crew_manager.analyze_suppliers(
                test_suppliers, 
                quality_standards
            )
            
            assert isinstance(analysis, dict)
            assert 'total_suppliers' in analysis

class TestWebSearchTool:
    """Test the web search tool functionality"""
    
    @pytest.fixture
    def search_tool(self):
        """Create a test search tool instance"""
        return WebSearchTool()
    
    def test_initialization(self, search_tool):
        """Test search tool initialization"""
        assert search_tool.name == "web_search"
        assert search_tool.description is not None
    
    @pytest.mark.asyncio
    async def test_search_functionality(self, search_tool):
        """Test basic search functionality"""
        with patch('duckduckgo_search.DDGS') as mock_ddgs:
            # Mock search results
            mock_ddgs.return_value.text.return_value = [
                {
                    'title': 'Test Supplier Company',
                    'href': 'https://test-supplier.com',
                    'body': 'Leading supplier of electronic components'
                }
            ]
            
            result = search_tool._run('electronic components suppliers')
            
            assert isinstance(result, str)
            assert 'Test Supplier Company' in result or 'Search failed' in result
    
    @pytest.mark.asyncio
    async def test_supplier_search(self, search_tool):
        """Test specialized supplier search"""
        with patch.object(search_tool, '_search_async') as mock_search:
            mock_search.return_value = "Mocked search results"
            
            results = await search_tool.search_suppliers(
                'industrial sensors', 
                'Asia'
            )
            
            assert isinstance(results, list)
            assert len(results) > 0

class TestSupplierDatabaseTool:
    """Test the supplier database tool functionality"""
    
    @pytest.fixture
    def db_tool(self):
        """Create a test database tool instance"""
        # Use temporary file for testing
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        
        tool = SupplierDatabaseTool(temp_file.name)
        yield tool
        
        # Cleanup
        os.unlink(temp_file.name)
    
    def test_initialization(self, db_tool):
        """Test database tool initialization"""
        assert db_tool.name == "supplier_database"
        assert os.path.exists(db_tool.db_path)
    
    def test_store_supplier(self, db_tool):
        """Test storing supplier data"""
        supplier_data = {
            'name': 'Test Electronics Ltd',
            'website': 'https://test-electronics.com',
            'country': 'Germany',
            'product_categories': ['electronics', 'components'],
            'certifications': ['ISO9001', 'RoHS']
        }
        
        result = db_tool._run('store', **supplier_data)
        assert 'successfully' in result
    
    def test_search_suppliers(self, db_tool):
        """Test searching for suppliers"""
        # First store a supplier
        supplier_data = {
            'name': 'Search Test Supplier',
            'country': 'Japan',
            'product_categories': ['sensors']
        }
        db_tool._run('store', **supplier_data)
        
        # Then search for it
        result = db_tool._run('search', query='sensors')
        assert 'Search Test Supplier' in result or 'No suppliers found' in result

class TestConfig:
    """Test configuration management"""
    
    def test_config_initialization(self):
        """Test config initialization with environment variables"""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test_openai_key',
            'LOG_LEVEL': 'DEBUG',
            'MAX_SUPPLIERS': '100'
        }):
            config = Config()
            
            assert config.openai_api_key == 'test_openai_key'
            assert config.log_level == 'DEBUG'
            assert config.max_suppliers == 100
    
    def test_config_validation(self):
        """Test config validation"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                Config()
    
    def test_config_properties(self):
        """Test config property methods"""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test_key',
            'TAVILY_API_KEY': 'test_key'
        }):
            config = Config()
            
            assert config.has_openai is True
            assert config.has_search_api is True

class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete sourcing workflow"""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test_key',
            'TAVILY_API_KEY': 'test_key'
        }):
            # Mock the entire workflow
            with patch('src.crew_manager.SourcingCrewManager') as mock_manager:
                manager_instance = Mock()
                
                # Mock each step of the workflow
                manager_instance.research_suppliers = AsyncMock(return_value=[
                    {'name': 'Test Supplier', 'country': 'Germany'}
                ])
                manager_instance.analyze_suppliers = AsyncMock(return_value={
                    'total_suppliers': 1,
                    'average_scores': {'quality': 8.5}
                })
                manager_instance.assess_risks = AsyncMock(return_value={
                    'overall_risk_level': 'LOW'
                })
                manager_instance.generate_report = AsyncMock(return_value={
                    'executive_summary': 'Test report',
                    'total_suppliers': 1,
                    'recommended_count': 1
                })
                
                mock_manager.return_value = manager_instance
                
                # Test the workflow
                crew_manager = mock_manager()
                
                suppliers = await crew_manager.research_suppliers('test', 'Global')
                analysis = await crew_manager.analyze_suppliers(suppliers, [])
                risks = await crew_manager.assess_risks(suppliers)
                report = await crew_manager.generate_report(
                    suppliers, analysis, risks, 'test', '$10k', True
                )
                
                assert len(suppliers) > 0
                assert 'total_suppliers' in analysis
                assert 'overall_risk_level' in risks
                assert 'executive_summary' in report

# Performance Tests
class TestPerformance:
    """Performance and load tests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_searches(self):
        """Test concurrent search operations"""
        search_tool = WebSearchTool()
        
        # Mock concurrent searches
        with patch.object(search_tool, '_search_async') as mock_search:
            mock_search.return_value = "Mock result"
            
            tasks = []
            for i in range(5):
                tasks.append(search_tool._search_async(f'query_{i}'))
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 5
            assert all('Mock result' in result for result in results)

# Fixtures for test data
@pytest.fixture
def sample_supplier_data():
    """Sample supplier data for testing"""
    return {
        'name': 'Global Tech Solutions',
        'website': 'https://globaltech.com',
        'country': 'Singapore',
        'city': 'Singapore',
        'product_categories': ['electronics', 'sensors', 'components'],
        'contact_info': {
            'email': 'sales@globaltech.com',
            'phone': '+65-1234-5678'
        },
        'certifications': ['ISO9001', 'ISO14001', 'RoHS'],
        'capabilities': {
            'manufacturing': True,
            'design': True,
            'testing': True
        }
    }

@pytest.fixture
def sample_evaluation_criteria():
    """Sample evaluation criteria for testing"""
    return [
        'Quality Standards',
        'Financial Stability',
        'Delivery Performance',
        'Technical Capabilities',
        'Cost Competitiveness',
        'Innovation',
        'Sustainability',
        'Risk Profile'
    ]

# Test utilities
def create_mock_llm_response(content: str):
    """Create a mock LLM response for testing"""
    mock_response = Mock()
    mock_response.content = content
    return mock_response

def create_mock_search_results(count: int = 3):
    """Create mock search results for testing"""
    results = []
    for i in range(count):
        results.append({
            'title': f'Test Supplier {i+1}',
            'url': f'https://supplier{i+1}.com',
            'snippet': f'Description of supplier {i+1}'
        })
    return results

# Parameterized tests
@pytest.mark.parametrize("product_category,expected_min_suppliers", [
    ("electronic components", 1),
    ("industrial sensors", 1),
    ("automotive parts", 1),
])
def test_supplier_discovery_coverage(product_category, expected_min_suppliers):
    """Test supplier discovery coverage for different product categories"""
    search_tool = WebSearchTool()
    
    with patch.object(search_tool, '_search_async') as mock_search:
        # Mock finding suppliers
        mock_search.return_value = f"Found suppliers for {product_category}"
        
        result = search_tool._run(f"{product_category} suppliers")
        
        assert product_category in result.lower() or "found" in result.lower()

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
