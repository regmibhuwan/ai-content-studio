"""
Setup verification script.

Checks that all dependencies are installed and configurations are correct.
Run this before starting development or testing.
"""

import sys
from typing import List, Tuple


def check_imports() -> List[Tuple[str, bool, str]]:
    """Check if all required packages can be imported."""
    packages = [
        ("langgraph", "LangGraph workflow engine"),
        ("langchain", "LangChain framework"),
        ("langchain_openai", "OpenAI integration"),
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("sqlalchemy", "Database ORM"),
        ("aiosqlite", "Async SQLite"),
        ("tavily", "Tavily search API"),
        ("openai", "OpenAI client"),
        ("streamlit", "Streamlit UI"),
        ("httpx", "HTTP client"),
        ("markdown", "Markdown processing"),
        ("beautifulsoup4", "HTML parsing"),
    ]

    results = []
    for package, description in packages:
        try:
            __import__(package)
            results.append((package, True, description))
        except ImportError as e:
            results.append((package, False, f"{description} - ERROR: {str(e)}"))

    return results


def check_env_file() -> Tuple[bool, str]:
    """Check if .env file exists and has required keys."""
    import os
    from pathlib import Path

    env_path = Path(".env")
    
    if not env_path.exists():
        return False, ".env file not found. Copy .env.example to .env and add your API keys."

    # Try to load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        openai_key = os.getenv("OPENAI_API_KEY")
        tavily_key = os.getenv("TAVILY_API_KEY")
        
        if not openai_key or openai_key == "your_openai_api_key_here":
            return False, "OPENAI_API_KEY not configured in .env"
        
        if not tavily_key or tavily_key == "your_tavily_api_key_here":
            return False, "TAVILY_API_KEY not configured in .env"
        
        return True, "Environment variables configured correctly"
    
    except Exception as e:
        return False, f"Error loading .env: {str(e)}"


def check_project_structure() -> Tuple[bool, str]:
    """Check if project structure is correct."""
    from pathlib import Path

    required_dirs = [
        "backend",
        "backend/agents",
        "frontend",
        "utils",
        "tests",
        "data",
    ]

    required_files = [
        "backend/__init__.py",
        "backend/config.py",
        "backend/database.py",
        "backend/schemas.py",
        "backend/agents/__init__.py",
        "backend/agents/base.py",
        "backend/agents/research_agent.py",
        "backend/agents/workflow.py",
        "utils/__init__.py",
        "utils/logger.py",
        "utils/helpers.py",
        "requirements.txt",
    ]

    missing = []

    for dir_path in required_dirs:
        if not Path(dir_path).is_dir():
            missing.append(f"Directory: {dir_path}")

    for file_path in required_files:
        if not Path(file_path).is_file():
            missing.append(f"File: {file_path}")

    if missing:
        return False, f"Missing items:\n  - " + "\n  - ".join(missing)

    return True, "Project structure is correct"


def check_config() -> Tuple[bool, str]:
    """Check if configuration loads correctly."""
    try:
        from backend.config import get_settings
        settings = get_settings()
        
        # Try to access key settings
        _ = settings.openai_api_key
        _ = settings.tavily_api_key
        _ = settings.llm_model
        
        return True, f"Configuration loaded (Model: {settings.llm_model})"
    
    except Exception as e:
        return False, f"Configuration error: {str(e)}"


def main():
    """Run all checks and display results."""
    print("\n" + "="*70)
    print("AI CONTENT STUDIO - SETUP VERIFICATION")
    print("="*70 + "\n")

    all_passed = True

    # Check 1: Python version
    print("[1] Python Version")
    print("-" * 70)
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"   [OK] Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"   [FAIL] Python {version.major}.{version.minor}.{version.micro} (Requires Python 3.10+)")
        all_passed = False
    print()

    # Check 2: Package imports
    print("[2] Required Packages")
    print("-" * 70)
    import_results = check_imports()
    failed_imports = []
    
    for package, success, description in import_results:
        if success:
            print(f"   [OK]   {package:20s} - {description}")
        else:
            print(f"   [FAIL] {package:20s} - {description}")
            failed_imports.append(package)
            all_passed = False
    
    if failed_imports:
        print(f"\n   [!] Run: pip install -r requirements.txt")
    print()

    # Check 3: Project structure
    print("[3] Project Structure")
    print("-" * 70)
    structure_ok, structure_msg = check_project_structure()
    if structure_ok:
        print(f"   [OK] {structure_msg}")
    else:
        print(f"   [FAIL] {structure_msg}")
        all_passed = False
    print()

    # Check 4: Environment file
    print("[4] Environment Configuration")
    print("-" * 70)
    env_ok, env_msg = check_env_file()
    if env_ok:
        print(f"   [OK] {env_msg}")
    else:
        print(f"   [FAIL] {env_msg}")
        all_passed = False
    print()

    # Check 5: Configuration loading
    print("[5] Configuration Loading")
    print("-" * 70)
    config_ok, config_msg = check_config()
    if config_ok:
        print(f"   [OK] {config_msg}")
    else:
        print(f"   [FAIL] {config_msg}")
        all_passed = False
    print()

    # Final summary
    print("="*70)
    if all_passed:
        print("[SUCCESS] ALL CHECKS PASSED - Ready to run!")
        print("\nNext steps:")
        print("  1. Initialize database: python -c \"from backend.database import init_db; import asyncio; asyncio.run(init_db())\"")
        print("  2. Run tests: python test_workflow.py")
        print("  3. Start development!")
    else:
        print("[FAILED] SOME CHECKS FAILED - Fix the issues above before proceeding")
        print("\nCommon fixes:")
        print("  - Install packages: pip install -r requirements.txt")
        print("  - Create .env file: copy .env.example .env (Windows) or cp .env.example .env (Mac/Linux)")
        print("  - Add API keys to .env file")
    print("="*70 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())

