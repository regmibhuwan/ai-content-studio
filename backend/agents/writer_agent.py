"""
Writer Agent

Expands outline into full article content.
Third agent in the content creation pipeline.
"""

from typing import Dict, Any

from backend.agents.base import BaseAgent, AgentResponse
from utils.helpers import count_words


class WriterAgent(BaseAgent):
    """
    Agent specialized in writing full article content.

    Takes a structured outline and research data, then expands
    each section into well-written paragraphs that meet the
    target word count and style requirements.
    """

    def __init__(self):
        """Initialize Writer Agent."""
        super().__init__(name="WriterAgent")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Write full article content from outline.

        Args:
            input_data: Must contain:
                - outline (str): Structured outline
                - research_data (dict): Research findings for reference
                - topic (str): Article topic
                - tone (str, optional): Writing tone
                - target_audience (str, optional): Target audience
                - min_words (int, optional): Minimum word count

        Returns:
            AgentResponse with full article content
        """
        # Extract required data
        outline = input_data.get("outline")
        research_data = input_data.get("research_data")
        topic = input_data.get("topic")

        if not outline or not research_data or not topic:
            return AgentResponse(
                status="error",
                error="Missing required fields: outline, research_data, or topic",
                message="Writer agent requires outline, research data, and topic",
            )

        tone = input_data.get("tone", "professional")
        target_audience = input_data.get("target_audience", "general")
        min_words = input_data.get("min_words", 800)

        self.log_info(f"Writing article for topic: '{topic}'")
        self.log_debug(f"Target: {min_words}+ words, {tone} tone, {target_audience} audience")

        try:
            # Extract research context
            synthesis = research_data.get("synthesis", "")
            sources = research_data.get("sources", [])

            # Generate article content
            content = await self._write_article(
                topic=topic,
                outline=outline,
                synthesis=synthesis,
                sources=sources,
                tone=tone,
                target_audience=target_audience,
                min_words=min_words,
            )

            # Count words in generated content
            word_count = count_words(content)

            # Check if word count meets minimum
            if word_count < min_words * 0.8:  # Allow 20% flexibility
                self.log_info(f"Initial draft has {word_count} words, expanding...")
                # Expand content if too short
                content = await self._expand_content(
                    content=content,
                    topic=topic,
                    target_words=min_words,
                    current_words=word_count,
                )
                word_count = count_words(content)

            self.log_info(f"Article written: {word_count} words")

            return AgentResponse(
                status="success",
                data={
                    "content": content,
                    "word_count": word_count,
                    "meets_minimum": word_count >= min_words * 0.8,
                },
                message=f"Article written with {word_count} words",
            )

        except Exception as e:
            self.log_error(f"Article writing failed: {str(e)}")
            return AgentResponse(
                status="error",
                error=str(e),
                message="Failed to write article",
            )

    async def _write_article(
        self,
        topic: str,
        outline: str,
        synthesis: str,
        sources: list,
        tone: str,
        target_audience: str,
        min_words: int,
    ) -> str:
        """
        Write full article content using LLM.

        Args:
            topic: Article topic
            outline: Structured outline to follow
            synthesis: Research synthesis
            sources: List of source data
            tone: Writing tone
            target_audience: Target audience
            min_words: Minimum word count

        Returns:
            str: Full article in Markdown format
        """
        # Compile source references
        source_refs = "\n".join(
            [
                f"{i+1}. {src.get('title', 'Untitled')} - {src.get('url', 'No URL')}"
                for i, src in enumerate(sources[:5])  # Top 5 sources
            ]
        )

        system_prompt = f"""You are an expert content writer creating high-quality articles.

Writing Guidelines:
- Tone: {tone}
- Audience: {target_audience}
- Length: At least {min_words} words
- Format: Markdown with proper headings (# for title, ## for sections)
- Style: Clear, engaging, informative
- Structure: Follow the provided outline closely
- Citations: Naturally incorporate research findings
- Flow: Smooth transitions between sections

Quality Requirements:
- Use concrete examples and specific details
- Avoid fluff and filler content
- Write in active voice
- Use varied sentence structure
- Include relevant statistics or facts from research
- Make content actionable when appropriate

Do NOT include meta-commentary or notes. Output only the article content."""

        user_prompt = f"""Write a comprehensive article on the following topic.

Topic: {topic}

Outline to Follow:
{outline}

Research Context:
{synthesis}

Reference Sources:
{source_refs}

Write the complete article now, ensuring it's at least {min_words} words and follows the outline structure."""

        content = await self._call_llm(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,  # Balanced creativity
            max_tokens=3000,  # Allow longer content
        )

        return content.strip()

    async def _expand_content(
        self,
        content: str,
        topic: str,
        target_words: int,
        current_words: int,
    ) -> str:
        """
        Expand content if it's too short.

        Args:
            content: Current article content
            topic: Article topic
            target_words: Target word count
            current_words: Current word count

        Returns:
            str: Expanded content
        """
        shortfall = target_words - current_words

        system_prompt = """You are an expert content editor tasked with expanding an article.

Add more depth by:
- Elaborating on key points with examples
- Adding relevant details and explanations
- Including more context where appropriate
- Expanding on implications or applications
- Adding transitions and connecting thoughts

Maintain:
- The same tone and style
- Logical flow and structure
- Quality (no fluff or redundancy)"""

        user_prompt = f"""The following article about "{topic}" is currently {current_words} words but needs to be at least {target_words} words.

Expand it by approximately {shortfall} words while maintaining quality and coherence.

Current Article:
{content}

Output the expanded version."""

        expanded = await self._call_llm(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.6,
            max_tokens=3500,
        )

        return expanded.strip()

    def _validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate required input fields."""
        super()._validate_input(input_data)

        if "outline" not in input_data:
            raise ValueError("WriterAgent requires 'outline' in input_data")

        if "research_data" not in input_data:
            raise ValueError("WriterAgent requires 'research_data' in input_data")

        if "topic" not in input_data:
            raise ValueError("WriterAgent requires 'topic' in input_data")

