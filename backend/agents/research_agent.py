"""
Research Agent

Performs web research using Tavily API to gather sources and information for article creation.
First agent in the content creation pipeline.
"""

from typing import Dict, Any, List
from tavily import TavilyClient

from backend.agents.base import BaseAgent, AgentResponse
from backend.config import get_settings

settings = get_settings()


class ResearchAgent(BaseAgent):
    """
    Agent specialized in web research and source gathering.

    Uses Tavily API to:
    - Search the web for relevant content
    - Extract key information and quotes
    - Identify authoritative sources
    - Compile research findings
    """

    def __init__(self):
        """Initialize Research Agent with Tavily client."""
        super().__init__(name="ResearchAgent")
        self.tavily_client = TavilyClient(api_key=settings.tavily_api_key)
        self.max_results = 5  # Number of search results to retrieve

    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Execute web research for the given topic.

        Args:
            input_data: Must contain:
                - topic (str): Article topic to research
                - target_audience (str, optional): Target audience
                - tone (str, optional): Desired tone

        Returns:
            AgentResponse with research data including sources and key findings
        """
        topic = input_data.get("topic")
        if not topic:
            return AgentResponse(
                status="error",
                error="Missing required field: topic",
                message="Research agent requires a topic",
            )

        self.log_info(f"Researching topic: '{topic}'")

        try:
            # Perform web search using Tavily
            search_results = await self._search_web(topic)

            # Extract and structure key information
            research_data = await self._process_search_results(
                search_results, topic, input_data
            )

            # Use LLM to synthesize findings
            synthesis = await self._synthesize_research(research_data, topic)

            # Compile final research output
            final_data = {
                "sources": research_data["sources"],
                "key_findings": research_data["key_findings"],
                "synthesis": synthesis,
                "search_query": topic,
                "num_sources": len(research_data["sources"]),
            }

            return AgentResponse(
                status="success",
                data=final_data,
                message=f"Research completed with {len(research_data['sources'])} sources",
            )

        except Exception as e:
            self.log_error(f"Research failed: {str(e)}")
            return AgentResponse(
                status="error",
                error=str(e),
                message="Failed to complete research",
            )

    async def _search_web(self, query: str) -> Dict[str, Any]:
        """
        Search the web using Tavily API.

        Args:
            query: Search query

        Returns:
            Dict containing search results from Tavily
        """
        self.log_debug(f"Executing Tavily search for: {query}")

        # Tavily search with context extraction
        response = self.tavily_client.search(
            query=query,
            search_depth="advanced",  # Use advanced search for better results
            max_results=self.max_results,
            include_answer=True,  # Get AI-generated answer
            include_raw_content=False,  # Don't need full HTML
        )

        self.log_debug(f"Tavily returned {len(response.get('results', []))} results")
        return response

    async def _process_search_results(
        self,
        search_results: Dict[str, Any],
        topic: str,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Process and structure search results.

        Args:
            search_results: Raw results from Tavily
            topic: Original search topic
            input_data: Additional context

        Returns:
            Dict with structured sources and key findings
        """
        sources = []
        key_findings = []

        # Process each search result
        for idx, result in enumerate(search_results.get("results", []), 1):
            source = {
                "id": idx,
                "title": result.get("title", "Untitled"),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "score": result.get("score", 0.0),
            }
            sources.append(source)

            # Extract key finding from content
            if result.get("content"):
                key_findings.append(
                    {
                        "source_id": idx,
                        "finding": result["content"][:300],  # First 300 chars
                    }
                )

        # Add Tavily's AI-generated answer if available
        if search_results.get("answer"):
            key_findings.insert(
                0,
                {
                    "source_id": 0,
                    "finding": search_results["answer"],
                    "type": "ai_summary",
                },
            )

        return {
            "sources": sources,
            "key_findings": key_findings,
        }

    async def _synthesize_research(
        self,
        research_data: Dict[str, Any],
        topic: str,
    ) -> str:
        """
        Use LLM to synthesize research findings into coherent summary.

        Args:
            research_data: Structured research data
            topic: Article topic

        Returns:
            str: Synthesized research summary
        """
        # Compile all findings into prompt
        findings_text = "\n\n".join(
            [
                f"Source {f['source_id']}: {f['finding']}"
                for f in research_data["key_findings"]
            ]
        )

        system_prompt = """You are a research analyst. Synthesize the provided research findings into a clear, 
organized summary. Focus on:
1. Main themes and concepts
2. Key facts and statistics
3. Different perspectives or viewpoints
4. Gaps or areas needing more information

Be concise but comprehensive."""

        user_prompt = f"""Topic: {topic}

Research Findings:
{findings_text}

Please synthesize these findings into a structured summary that will help guide article creation."""

        synthesis = await self._call_llm(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,  # Lower temperature for factual synthesis
        )

        return synthesis

    def _validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate that required fields are present."""
        super()._validate_input(input_data)
        
        if "topic" not in input_data:
            raise ValueError("ResearchAgent requires 'topic' in input_data")
        
        if not isinstance(input_data["topic"], str) or not input_data["topic"].strip():
            raise ValueError("Topic must be a non-empty string")

