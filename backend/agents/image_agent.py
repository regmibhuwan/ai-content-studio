"""
Image Agent

Generates cover images using DALL-E.
Sixth and final agent in the content creation pipeline.
"""

from typing import Dict, Any

from backend.agents.base import BaseAgent, AgentResponse


class ImageAgent(BaseAgent):
    """
    Agent specialized in generating cover images.

    Uses DALL-E 3 to create relevant, high-quality images based on
    article content and topic.
    """

    def __init__(self):
        """Initialize Image Agent."""
        super().__init__(name="ImageAgent")

    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Generate cover image for article.

        Args:
            input_data: Must contain:
                - topic (str): Article topic
                - edited_content or content (str, optional): For context
                - include_image (bool, optional): Whether to generate image

        Returns:
            AgentResponse with image URL
        """
        # Check if image generation is requested
        if not input_data.get("include_image", True):
            self.log_info("Image generation skipped (include_image=False)")
            return AgentResponse(
                status="success",
                data={"image_url": None, "skipped": True},
                message="Image generation skipped per configuration",
            )

        topic = input_data.get("topic")
        if not topic:
            return AgentResponse(
                status="error",
                error="Missing required field: topic",
                message="Image agent requires topic",
            )

        # Get content for context (prefer edited version)
        content = input_data.get("edited_content") or input_data.get("content", "")

        self.log_info(f"Generating cover image for topic: '{topic}'")

        try:
            # Generate DALL-E prompt from content
            image_prompt = await self._create_image_prompt(topic, content)

            self.log_debug(f"Image prompt: {image_prompt[:100]}...")

            # Generate image using DALL-E
            image_url = await self._generate_image(image_prompt)

            self.log_info(f"Image generated successfully: {image_url[:50]}...")

            return AgentResponse(
                status="success",
                data={
                    "image_url": image_url,
                    "image_prompt": image_prompt,
                    "image_model": self.settings.image_model,
                },
                message="Cover image generated successfully",
            )

        except Exception as e:
            self.log_error(f"Image generation failed: {str(e)}")
            # Image generation is non-critical, return success with null URL
            return AgentResponse(
                status="success",  # Still success, just no image
                data={
                    "image_url": None,
                    "error": str(e),
                    "message": "Image generation failed but workflow continues",
                },
                message=f"Image generation failed: {str(e)}",
            )

    async def _create_image_prompt(self, topic: str, content: str) -> str:
        """
        Create DALL-E prompt from article content.

        Args:
            topic: Article topic
            content: Article content (optional)

        Returns:
            str: DALL-E image prompt
        """
        # If we have content, use it for context; otherwise use topic only
        if content and len(content) > 100:
            # Use LLM to extract visual concepts from content
            content_preview = content[:1000]  # First 1000 chars

            system_prompt = """You are an expert at creating image prompts for DALL-E.

Create a detailed, visual image prompt that:
1. Captures the essence of the article
2. Is professional and high-quality
3. Is descriptive and specific
4. Avoids text/words in the image
5. Uses artistic/photographic styles
6. Is appropriate for article cover art

Format: Single paragraph, 2-3 sentences, descriptive.

Examples:
- "A modern, minimalist illustration of artificial intelligence..."
- "Professional photograph of a diverse team collaborating..."
- "Abstract digital art representing data flowing through networks..."

Do NOT include meta-commentary. Output only the image prompt."""

            user_prompt = f"""Create a DALL-E image prompt for an article cover image.

Article Topic: {topic}

Article Content Preview:
{content_preview}

Generate a detailed image prompt that would create a compelling cover image for this article."""

            prompt = await self._call_llm(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=300,
            )

            return prompt.strip()
        else:
            # Fallback: Create simple prompt from topic
            return self._create_simple_prompt(topic)

    def _create_simple_prompt(self, topic: str) -> str:
        """
        Create simple image prompt from topic only.

        Args:
            topic: Article topic

        Returns:
            str: Basic image prompt
        """
        # Simple prompt construction
        prompt = f"A professional, modern illustration representing {topic}. "
        prompt += "High quality, clean design, suitable for article cover art. "
        prompt += "Vibrant colors, abstract or minimalist style."

        return prompt

    async def _generate_image(self, prompt: str) -> str:
        """
        Generate image using DALL-E API.

        Args:
            prompt: Image generation prompt

        Returns:
            str: URL of generated image
        """
        self.log_debug(f"Calling DALL-E with model: {self.settings.image_model}")

        # Call OpenAI Images API
        response = await self.llm_client.images.generate(
            model=self.settings.image_model,
            prompt=prompt,
            size=self.settings.image_size,
            quality="standard",  # or "hd" for higher quality (more expensive)
            n=1,  # Number of images to generate
        )

        # Extract image URL from response
        image_url = response.data[0].url

        return image_url

    def _validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate required input fields."""
        super()._validate_input(input_data)

        if "topic" not in input_data:
            raise ValueError("ImageAgent requires 'topic' in input_data")

