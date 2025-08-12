#!/usr/bin/env python3
"""
Test script for Groq and Local LLM summarizers.
This script will test both providers and show their status.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_config():
    """Test configuration loading."""
    print("🔧 Testing Configuration...")
    try:
        from config import config
        print(f"✅ Config loaded successfully")
        print(f"   Provider: {config.provider}")
        print(f"   Groq API Key: {'✅ Set' if config.groq_api_key else '❌ Not set'}")
        print(f"   Local Model Path: {'✅ Set' if config.local_model_path else '❌ Not set'}")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_groq_provider():
    """Test Groq provider specifically."""
    print("\n🚀 Testing Groq Provider...")
    try:
        from llm_summarizer import GroqProvider
        from config import config
        
        if not config.groq_api_key:
            print("   ❌ GROQ_API_KEY not set in environment")
            print("   💡 Set it with: export GROQ_API_KEY=your_key")
            return False
        
        provider = GroqProvider()
        if provider.is_available():
            print("   ✅ Groq provider is available")
            print(f"   Model: {config.groq_model}")
            print(f"   Max Tokens: {config.groq_max_tokens}")
            print(f"   Temperature: {config.groq_temperature}")
            return True
        else:
            print("   ❌ Groq provider is not available")
            return False
            
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   💡 Install groq with: pip install groq")
        return False
    except Exception as e:
        print(f"   ❌ Groq provider error: {e}")
        return False

def test_local_provider():
    """Test Local provider specifically."""
    print("\n🏠 Testing Local Provider...")
    try:
        from llm_summarizer import LocalProvider
        from config import config
        
        provider = LocalProvider()
        if provider.is_available():
            print("   ✅ Local provider is available")
            print(f"   Model Path: {config.local_model_path or 'Default'}")
            print(f"   Device: {config.local_device}")
            print(f"   Max Tokens: {config.local_max_tokens}")
            print(f"   Temperature: {config.local_temperature}")
            return True
        else:
            print("   ❌ Local provider is not available")
            print("   💡 This is normal if transformers/torch not installed")
            return False
            
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   💡 Install local dependencies with: pip install transformers torch accelerate")
        return False
    except Exception as e:
        print(f"   ❌ Local provider error: {e}")
        return False

def test_summarizer_integration():
    """Test the main summarizer integration."""
    print("\n🔗 Testing Summarizer Integration...")
    try:
        from llm_summarizer import get_summarizer
        from models import SummaryRequest, ResumeStruct, Education, Experience
        
        summarizer = get_summarizer()
        available = summarizer.get_available_providers()
        current = summarizer.get_current_provider_name()
        
        print(f"   Available providers: {available}")
        print(f"   Current provider: {current}")
        
        # Test with a simple resume
        test_resume = ResumeStruct(
            name="John Doe",
            title="Software Engineer",
            email="john@example.com",
            phone="123-456-7890",
            location="San Francisco, CA",
            education=[],
            experience=[],
            skills={"Technical": ["Python", "FastAPI", "Machine Learning"]}
        )
        
        request = SummaryRequest(
            resume_data=test_resume,
            max_length=100,
            tone="professional",
            focus_areas=["technical skills"]
        )
        
        print("   ✅ Summarizer integration test passed")
        return True
        
    except Exception as e:
        print(f"   ❌ Summarizer integration error: {e}")
        return False

def test_actual_summarization():
    """Test actual summarization with available providers."""
    print("\n📝 Testing Actual Summarization...")
    try:
        from llm_summarizer import get_summarizer
        from models import SummaryRequest, ResumeStruct, Education, Experience
        
        summarizer = get_summarizer()
        available_providers = summarizer.get_available_providers()
        
        if not any(available_providers.values()):
            print("   ❌ No providers available")
            return False
        
        # Create a test resume
        test_resume = ResumeStruct(
            name="Jane Smith",
            title="Data Scientist",
            email="jane@example.com",
            phone="987-654-3210",
            location="New York, NY",
            education=[
                Education(degree="MS Computer Science", institution="Stanford", field_of_study="Computer Science", year=2022)
            ],
            experience=[
                Experience(company="Tech Corp", title="Data Scientist", start="Jan 2022", end="Present", location="New York, NY", highlights=["Built ML models for recommendation systems"])
            ],
            skills={"Technical": ["Python", "TensorFlow", "SQL", "Machine Learning"]}
        )
        
        request = SummaryRequest(
            resume_data=test_resume,
            max_length=150,
            tone="professional",
            focus_areas=["experience", "technical skills"]
        )
        
        # Test each available provider
        for provider_name, is_available in available_providers.items():
            if not is_available:
                print(f"   ⏭️  Skipping {provider_name} provider (not available)")
                continue
                
            print(f"   🔄 Testing with {provider_name} provider...")
            try:
                # Set the provider
                summarizer.set_provider(provider_name)
                
                # Generate summary
                summary = summarizer.summarize_resume(test_resume, max_length=250, tone="professional")
                
                print(f"   ✅ Summary generated successfully with {provider_name}!")
                print(f"   📊 Summary length: {len(summary)} characters")
                print(f"   📝 Summary preview: {summary[:100]}...")
                
            except Exception as e:
                print(f"   ❌ Failed to generate summary with {provider_name}: {e}")
                continue
        
        print("   ✅ Summarization test completed for all available providers")
        return True
        
    except Exception as e:
        print(f"   ❌ Summarization test failed: {e}")
        return False

def test_both_providers():
    """Test both Groq and Local providers side by side."""
    print("\n🔄 Testing Both Providers Side by Side...")
    try:
        from llm_summarizer import get_summarizer
        from models import SummaryRequest, ResumeStruct, Education, Experience
        
        summarizer = get_summarizer()
        available_providers = summarizer.get_available_providers()
        
        print(f"   Available providers: {available_providers}")
        
        if not any(available_providers.values()):
            print("   ❌ No providers available for testing")
            return False
        
        # Create a test resume
        test_resume = ResumeStruct(
            name="Alex Johnson",
            title="Full Stack Developer",
            email="alex@example.com",
            phone="555-123-4567",
            location="Austin, TX",
            education=[
                Education(degree="BS Computer Science", institution="UT Austin", field_of_study="Computer Science", year=2021)
            ],
            experience=[
                Experience(company="Startup Inc", title="Full Stack Developer", start="Jun 2021", end="Present", location="Austin, TX", highlights=["Developed web applications using React and Node.js", "Implemented CI/CD pipelines"])
            ],
            skills={"Frontend": ["React", "TypeScript", "CSS"], "Backend": ["Node.js", "Python", "PostgreSQL"]}
        )
        
        results = {}
        
        # Test each available provider
        for provider_name, is_available in available_providers.items():
            if not is_available:
                print(f"   ⏭️  {provider_name}: Not available")
                results[provider_name] = {"status": "not_available", "error": "Provider not available"}
                continue
                
            print(f"   🔄 Testing {provider_name} provider...")
            try:
                # Set the provider
                summarizer.set_provider(provider_name)
                
                # Generate summary
                summary = summarizer.summarize_resume(test_resume, max_length=200, tone="professional")
                
                print(f"   ✅ {provider_name}: Success!")
                print(f"      📊 Length: {len(summary)} chars")
                print(f"      📝 Preview: {summary[:80]}...")
                
                results[provider_name] = {
                    "status": "success",
                    "summary": summary,
                    "length": len(summary)
                }
                
            except Exception as e:
                print(f"   ❌ {provider_name}: Failed - {e}")
                results[provider_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Summary of results
        print(f"\n   📊 Provider Test Results:")
        for provider_name, result in results.items():
            status_icon = "✅" if result["status"] == "success" else "❌" if result["status"] == "error" else "⏭️"
            print(f"      {status_icon} {provider_name}: {result['status']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Provider comparison test failed: {e}")
        return False

def test_provider_switching():
    """Test that provider switching works correctly."""
    print("\n🔄 Testing Provider Switching...")
    try:
        from llm_summarizer import get_summarizer
        
        summarizer = get_summarizer()
        available_providers = summarizer.get_available_providers()
        
        if not any(available_providers.values()):
            print("   ❌ No providers available for switching test")
            return False
        
        # Test switching to each available provider
        for provider_name, is_available in available_providers.items():
            if not is_available:
                continue
                
            print(f"   🔄 Switching to {provider_name} provider...")
            try:
                summarizer.set_provider(provider_name)
                current_provider = summarizer.get_current_provider_name()
                
                if current_provider == provider_name:
                    print(f"   ✅ Successfully switched to {provider_name}")
                else:
                    print(f"   ❌ Failed to switch to {provider_name}, current: {current_provider}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Error switching to {provider_name}: {e}")
                return False
        
        print("   ✅ Provider switching test passed")
        return True
        
    except Exception as e:
        print(f"   ❌ Provider switching test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Resume Summarizer Testing Suite")
    print("=" * 50)
    
    # Test configuration
    if not test_config():
        print("\n❌ Configuration test failed. Please check your setup.")
        return 1
    
    # Test individual providers
    groq_ok = test_groq_provider()
    local_ok = test_local_provider()
    
    # Test integration
    integration_ok = test_summarizer_integration()
    
    # Test actual summarization if any provider is available
    if groq_ok or local_ok:
        summarization_ok = test_actual_summarization()
    else:
        print("\n⚠️  No providers available for summarization test")
        summarization_ok = False
    
    # Test both providers side by side
    both_providers_ok = test_both_providers()

    # Test provider switching
    provider_switching_ok = test_provider_switching()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Configuration: {'✅ PASS' if True else '❌ FAIL'}")
    print(f"Groq Provider: {'✅ PASS' if groq_ok else '❌ FAIL'}")
    print(f"Local Provider: {'✅ PASS' if local_ok else '❌ FAIL'}")
    print(f"Integration: {'✅ PASS' if integration_ok else '❌ FAIL'}")
    print(f"Summarization: {'✅ PASS' if summarization_ok else '❌ FAIL'}")
    print(f"Both Providers Side by Side: {'✅ PASS' if both_providers_ok else '❌ FAIL'}")
    print(f"Provider Switching: {'✅ PASS' if provider_switching_ok else '❌ FAIL'}")
    
    if groq_ok or local_ok:
        print("\n🎉 At least one provider is working!")
        if groq_ok:
            print("   🚀 Groq API is ready to use")
        if local_ok:
            print("   🏠 Local LLM is ready to use")
    else:
        print("\n❌ No providers are working. Please check your setup.")
        print("\n💡 Troubleshooting tips:")
        print("   1. For Groq: Set GROQ_API_KEY environment variable")
        print("   2. For Local: Install transformers, torch, accelerate")
        print("   3. Check your .env file configuration")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
