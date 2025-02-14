from setuptools import setup, find_packages

setup(
    name="deep-research",
    version="0.1.0",
    packages=find_packages(),
    package_dir={"": "src"},
    install_requires=[
        "langchain>=0.2.0",
        "langchain-openai>=0.2.0",
        "httpx>=0.27.0",
        "beautifulsoup4>=4.12.3",
        "markdown2>=2.4.12",
        "pydantic>=2.7.1",
        "python-frontmatter>=1.0.0",
        "redis>=5.0.1",
        "langchain-core>=0.2.0",
        "firecrawl-py>=0.1.0",
        "streamlit>=1.31.0"
    ]
)
