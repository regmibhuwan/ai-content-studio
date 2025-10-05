"""
Editor Agent

Reviews and improves article content quality.
Fourth agent in the content creation pipeline.
"""

from typing import Dict, Any

from backend.agents.base import BaseAgent, AgentResponse


class EditorAgent(BaseAgent):
    """
    Agent specialized in editing and improving content.

    Performs multi-pass editing to improve:
    - Grammar and spelling
    - Flow and coherence
    - Factual accuracy
    - Tone consistency
    - Readability
    """

    def __init__(self):
        """Initialize Editor Agent."""
        super().__init__(name="EditorAgent")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Edit and improve article content.

        Args:
            input_data: Must contain:
                - content (str): Draft article content
                - topic (str): Article topic
                - research_data (dict, optional): For fact-checking
                - tone (str, optional): Expected tone
                - target_audience (str, optional): Target audience

        Returns:
            AgentResponse with edited content and change summary
        """
        # Extract required data
        content = input_data.get("content")
        topic = input_data.get("topic")

        if not content or not topic:
            return AgentResponse(
                status="error",
                error="Missing required fields: content or topic",
                message="Editor agent requires content and topic",
            )

        research_data = input_data.get("research_data", {})
        tone = input_data.get("tone", "professional")
        target_audience = input_data.get("target_audience", "general")

        self.log_info(f"Editing article for topic: '{topic}'")
        self.log_debug(f"Content length: {len(content)} characters")

        try:
            # Perform comprehensive editing
            edited_content = await self._edit_content(
                content=content,
                topic=topic,
                research_synthesis=research_data.get("synthesis", ""),
                tone=tone,
                target_audience=target_audience,
            )

            # Analyze improvements made
            improvements = self._analyze_changes(content, edited_content)

            self.log_info(f"Editing complete. {improvements['summary']}")

            return AgentResponse(
                status="success",
                data={
                    "edited_content": edited_content,
                    "original_length": len(content),
                    "edited_length": len(edited_content),
                    "improvements": improvements,
                },
                message=f"Content edited successfully. {improvements['summary']}",
            )

        except Exception as e:
            self.log_error(f"Editing failed: {str(e)}")
            return AgentResponse(
                status="error",
                error=str(e),
                message="Failed to edit content",
            )

    async def _edit_content(
        self,
        content: str,
        topic: str,
        research_synthesis: str,
        tone: str,
        target_audience: str,
    ) -> str:
        """
        Perform comprehensive content editing using LLM.

        Args:
            content: Original article content
            topic: Article topic
            research_synthesis: Research context for fact-checking
            tone: Expected tone
            target_audience: Target audience

        Returns:
            str: Edited and improved content
        """
        system_prompt = f"""You are an expert editor reviewing and improving article content.

Editing Checklist:
1. Grammar & Spelling: Fix all errors
2. Flow & Coherence: Improve transitions, logical flow
3. Clarity: Simplify complex sentences, remove jargon (unless appropriate for {target_audience})
4. Tone: Ensure consistent {tone} tone throughout
5. Accuracy: Verify claims align with research context
6. Engagement: Strengthen opening and closing
7. Structure: Ensure proper heading hierarchy
8. Readability: Vary sentence length, use active voice

What to KEEP:
- The core message and key points
- Technical accuracy
- Markdown formatting
- Overall structure

What to IMPROVE:
- Awkward phrasing
- Redundancy
- Weak transitions
- Passive voice
- Unclear statements

Output ONLY the edited article content, no meta-commentary."""

        user_prompt = f"""Edit and improve the following article about "{topic}".

Research Context (for fact-checking):
{research_synthesis[:500] if research_synthesis else 'No research context available'}

Article to Edit:
{content}

Provide the edited version with improvements to grammar, flow, clarity, and engagement."""

        edited = await self._call_llm(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.3,  # Lower temp for precise editing
            max_tokens=3500,
        )

        return edited.strip()

    def _analyze_changes(self, original: str, edited: str) -> Dict[str, Any]:
        """
        Analyze what changed between original and edited versions.

        Args:
            original: Original content
            edited: Edited content

        Returns:
            Dict with change analysis
        """
        original_words = len(original.split())
        edited_words = len(edited.split())
        word_diff = edited_words - original_words

        original_paras = original.count("\n\n")
        edited_paras = edited.count("\n\n")

        # Simple change detection
        if word_diff > 50:
            change_type = "expanded"
        elif word_diff < -50:
            change_type = "condensed"
        else:
            change_type = "refined"

        summary = f"{change_type.capitalize()} content"
        if abs(word_diff) > 10:
            summary += f" ({abs(word_diff)} words {'added' if word_diff > 0 else 'removed'})"

        return {
            "change_type": change_type,
            "word_difference": word_diff,
            "original_words": original_words,
            "edited_words": edited_words,
            "paragraph_count": edited_paras,
            "summary": summary,
        }

    def _validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate required input fields."""
        super()._validate_input(input_data)

        if "content" not in input_data:
            raise ValueError("EditorAgent requires 'content' in input_data")

        if "topic" not in input_data:
            raise ValueError("EditorAgent requires 'topic' in input_data")

        # Validate content is not empty
        if not input_data.get("content", "").strip():
            raise ValueError("Content cannot be empty")

