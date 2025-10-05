"""
SEO Agent

Optimizes content for search engines.
Fifth agent in the content creation pipeline.
"""

from typing import Dict, Any, List
import re

from backend.agents.base import BaseAgent, AgentResponse
from utils.helpers import extract_keywords


class SEOAgent(BaseAgent):
    """
    Agent specialized in SEO optimization.

    Analyzes content and generates:
    - SEO-optimized title
    - Meta description
    - Keywords
    - Heading structure analysis
    - Optimization recommendations
    """

    def __init__(self):
        """Initialize SEO Agent."""
        super().__init__(name="SEOAgent")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Optimize content for search engines.

        Args:
            input_data: Must contain:
                - edited_content or content (str): Article content to optimize
                - topic (str): Main topic/keyword
                - target_audience (str, optional): Target audience

        Returns:
            AgentResponse with SEO metadata
        """
        # Extract content (prefer edited version)
        content = input_data.get("edited_content") or input_data.get("content")
        topic = input_data.get("topic")

        if not content or not topic:
            return AgentResponse(
                status="error",
                error="Missing required fields: content or topic",
                message="SEO agent requires content and topic",
            )

        target_audience = input_data.get("target_audience", "general")

        self.log_info(f"Optimizing SEO for topic: '{topic}'")

        try:
            # Extract current headings
            headings = self._extract_headings(content)

            # Generate SEO metadata using LLM
            seo_data = await self._generate_seo_metadata(
                content=content,
                topic=topic,
                headings=headings,
                target_audience=target_audience,
            )

            # Extract keywords from content
            content_keywords = extract_keywords(content, max_keywords=15)

            # Combine LLM keywords with extracted keywords
            all_keywords = list(set(seo_data["keywords"] + content_keywords[:5]))

            # Compile final SEO metadata
            seo_meta = {
                "title": seo_data["title"],
                "meta_description": seo_data["meta_description"],
                "keywords": all_keywords[:15],  # Top 15 keywords
                "primary_keyword": topic,
                "headings": headings,
                "heading_count": len(headings),
                "word_count": len(content.split()),
                "recommendations": seo_data.get("recommendations", []),
            }

            self.log_info(f"SEO optimization complete. Title: '{seo_meta['title']}'")

            return AgentResponse(
                status="success",
                data=seo_meta,
                message=f"SEO metadata generated with {len(all_keywords)} keywords",
            )

        except Exception as e:
            self.log_error(f"SEO optimization failed: {str(e)}")
            return AgentResponse(
                status="error",
                error=str(e),
                message="Failed to generate SEO metadata",
            )

    async def _generate_seo_metadata(
        self,
        content: str,
        topic: str,
        headings: List[str],
        target_audience: str,
    ) -> Dict[str, Any]:
        """
        Generate SEO metadata using LLM.

        Args:
            content: Article content
            topic: Main topic
            headings: Extracted headings
            target_audience: Target audience

        Returns:
            Dict with title, description, keywords, recommendations
        """
        # Truncate content for prompt (use first 1500 chars + last 500 chars)
        content_preview = content[:1500]
        if len(content) > 2000:
            content_preview += "\n\n[...]\n\n" + content[-500:]

        headings_text = "\n".join([f"- {h}" for h in headings[:10]])

        system_prompt = """You are an SEO expert optimizing web content.

Generate SEO metadata following these rules:

1. Title (50-60 characters):
   - Include primary keyword naturally
   - Compelling and click-worthy
   - Accurate to content
   - Not clickbait

2. Meta Description (150-160 characters):
   - Summarize article value
   - Include primary keyword
   - Call-to-action if appropriate
   - Enticing but accurate

3. Keywords (10-15):
   - Mix of short and long-tail keywords
   - Relevant to content
   - Include topic variations
   - Consider search intent

4. Recommendations (3-5):
   - Specific, actionable SEO improvements
   - Based on current content analysis

Output as JSON format:
{
  "title": "SEO title here",
  "meta_description": "Description here",
  "keywords": ["keyword1", "keyword2", ...],
  "recommendations": ["rec1", "rec2", ...]
}"""

        user_prompt = f"""Analyze this article and generate SEO metadata.

Topic: {topic}
Target Audience: {target_audience}

Current Headings:
{headings_text}

Article Content:
{content_preview}

Generate optimized SEO metadata as JSON."""

        response = await self._call_llm(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.4,  # Lower temp for structured output
            max_tokens=800,
        )

        # Parse JSON response
        try:
            import json
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                seo_data = json.loads(json_match.group())
            else:
                # Fallback parsing
                seo_data = self._parse_seo_response_fallback(response, topic)
        except Exception as e:
            self.log_debug(f"JSON parsing failed, using fallback: {e}")
            seo_data = self._parse_seo_response_fallback(response, topic)

        return seo_data

    def _parse_seo_response_fallback(self, response: str, topic: str) -> Dict[str, Any]:
        """
        Fallback parser if JSON extraction fails.

        Args:
            response: LLM response text
            topic: Article topic

        Returns:
            Dict with SEO metadata
        """
        lines = response.split("\n")

        seo_data = {
            "title": f"{topic} - Complete Guide",
            "meta_description": f"Learn about {topic} in this comprehensive guide.",
            "keywords": [topic.lower()],
            "recommendations": ["Add more internal links", "Optimize images with alt text"],
        }

        # Try to extract title
        for line in lines:
            if "title" in line.lower() and ":" in line:
                title = line.split(":", 1)[1].strip().strip('"\'')
                if 30 < len(title) < 70:
                    seo_data["title"] = title
                break

        # Try to extract description
        for line in lines:
            if "description" in line.lower() and ":" in line:
                desc = line.split(":", 1)[1].strip().strip('"\'')
                if 50 < len(desc) < 180:
                    seo_data["meta_description"] = desc
                break

        return seo_data

    def _extract_headings(self, content: str) -> List[str]:
        """
        Extract all headings from markdown content.

        Args:
            content: Markdown content

        Returns:
            List of heading texts
        """
        headings = []

        # Match markdown headings (# to ######)
        heading_pattern = r'^(#{1,6})\s+(.+)$'

        for line in content.split("\n"):
            match = re.match(heading_pattern, line.strip())
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                headings.append(f"{'  ' * (level-1)}H{level}: {text}")

        return headings

    def _validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate required input fields."""
        super()._validate_input(input_data)

        # Need either edited_content or content
        if not input_data.get("edited_content") and not input_data.get("content"):
            raise ValueError("SEOAgent requires 'edited_content' or 'content' in input_data")

        if "topic" not in input_data:
            raise ValueError("SEOAgent requires 'topic' in input_data")

