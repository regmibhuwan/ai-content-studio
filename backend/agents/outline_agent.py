"""
Outline Agent

Creates structured content outlines from research data.
Second agent in the content creation pipeline.
"""

from typing import Dict, Any

from backend.agents.base import BaseAgent, AgentResponse


class OutlineAgent(BaseAgent):
    """
    Agent specialized in creating structured content outlines.

    Analyzes research findings and organizes them into a logical,
    hierarchical outline that will guide the writing process.
    """

    def __init__(self):
        """Initialize Outline Agent."""
        super().__init__(name="OutlineAgent")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a structured outline from research data.

        Args:
            input_data: Must contain:
                - research_data (dict): Research findings with sources and synthesis
                - topic (str): Article topic
                - tone (str, optional): Writing tone
                - target_audience (str, optional): Target audience
                - min_words (int, optional): Target word count for planning depth

        Returns:
            AgentResponse with outline as markdown string
        """
        # Extract required data
        research_data = input_data.get("research_data")
        topic = input_data.get("topic")
        
        if not research_data or not topic:
            return AgentResponse(
                status="error",
                error="Missing required fields: research_data or topic",
                message="Outline agent requires research data and topic",
            )

        tone = input_data.get("tone", "professional")
        target_audience = input_data.get("target_audience", "general")
        min_words = input_data.get("min_words", 800)

        self.log_info(f"Creating outline for topic: '{topic}'")
        self.log_debug(f"Parameters: tone={tone}, audience={target_audience}, target_words={min_words}")

        try:
            # Extract research synthesis and key findings
            synthesis = research_data.get("synthesis", "")
            sources = research_data.get("sources", [])
            key_findings = research_data.get("key_findings", [])

            # Create outline using LLM
            outline = await self._generate_outline(
                topic=topic,
                synthesis=synthesis,
                key_findings=key_findings,
                num_sources=len(sources),
                tone=tone,
                target_audience=target_audience,
                min_words=min_words,
            )

            # Validate outline structure
            if not self._validate_outline(outline):
                self.log_error("Generated outline failed validation")
                return AgentResponse(
                    status="error",
                    error="Invalid outline structure",
                    message="Failed to generate proper outline format",
                )

            self.log_info(f"Outline created with {outline.count('##')} main sections")

            return AgentResponse(
                status="success",
                data={
                    "outline": outline,
                    "num_sections": outline.count("##"),
                    "estimated_paragraphs": outline.count("-"),
                },
                message=f"Outline created with {outline.count('##')} sections",
            )

        except Exception as e:
            self.log_error(f"Outline generation failed: {str(e)}")
            return AgentResponse(
                status="error",
                error=str(e),
                message="Failed to generate outline",
            )

    async def _generate_outline(
        self,
        topic: str,
        synthesis: str,
        key_findings: list,
        num_sources: int,
        tone: str,
        target_audience: str,
        min_words: int,
    ) -> str:
        """
        Generate structured outline using LLM.

        Args:
            topic: Article topic
            synthesis: Research synthesis
            key_findings: List of key findings
            num_sources: Number of sources available
            tone: Writing tone
            target_audience: Target audience
            min_words: Minimum word count (affects depth)

        Returns:
            str: Markdown-formatted outline
        """
        # Compile key findings into text
        findings_text = "\n".join(
            [
                f"- {finding.get('finding', '')[:200]}"
                for finding in key_findings[:10]  # Limit to top 10
            ]
        )

        # Determine depth based on word count
        if min_words < 500:
            depth = "brief, with 3-4 main sections"
        elif min_words < 1000:
            depth = "moderate, with 4-5 main sections"
        else:
            depth = "comprehensive, with 5-7 main sections"

        system_prompt = f"""You are an expert content strategist creating article outlines.

Your outline should:
1. Be {depth}
2. Use hierarchical structure (## for main sections, - for sub-points)
3. Be tailored for {target_audience} audience
4. Match a {tone} tone
5. Flow logically from introduction to conclusion
6. Be specific and actionable (not vague headings)

Format:
## Section Title
- Key point 1
- Key point 2

Do NOT include meta-commentary. Output only the outline."""

        user_prompt = f"""Topic: {topic}

Research Synthesis:
{synthesis}

Key Findings from {num_sources} sources:
{findings_text}

Create a detailed, well-structured outline for an article on this topic.
Target word count: ~{min_words} words

The outline should organize the research findings into a logical flow that will guide the writing process."""

        outline = await self._call_llm(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.4,  # Lower temp for structured output
            max_tokens=1500,
        )

        return outline.strip()

    def _validate_outline(self, outline: str) -> bool:
        """
        Validate that outline has proper structure.

        Args:
            outline: Generated outline

        Returns:
            bool: True if valid, False otherwise
        """
        # Check for minimum content
        if not outline or len(outline) < 50:
            return False

        # Check for section headers (##)
        if outline.count("##") < 2:
            self.log_debug("Outline has fewer than 2 main sections")
            return False

        # Check for sub-points (-)
        if outline.count("-") < 3:
            self.log_debug("Outline has fewer than 3 sub-points")
            return False

        return True

    def _validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate required input fields."""
        super()._validate_input(input_data)

        if "research_data" not in input_data:
            raise ValueError("OutlineAgent requires 'research_data' in input_data")

        if "topic" not in input_data:
            raise ValueError("OutlineAgent requires 'topic' in input_data")

