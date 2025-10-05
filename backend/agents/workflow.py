"""
LangGraph Workflow Orchestration

Coordinates all agents in the content creation pipeline using LangGraph's StateGraph.
Manages state flow between agents and handles the overall execution.
"""

from typing import TypedDict, Dict, Any, Optional, List
from langgraph.graph import StateGraph, END

from backend.agents.research_agent import ResearchAgent
from backend.agents.outline_agent import OutlineAgent
from backend.agents.writer_agent import WriterAgent
from backend.agents.editor_agent import EditorAgent
from backend.agents.seo_agent import SEOAgent
from backend.agents.image_agent import ImageAgent
from utils.logger import get_logger

logger = get_logger(__name__)


# Define the shared state structure
class ContentCreationState(TypedDict, total=False):
    """
    Shared state passed between all agents in the workflow.

    This TypedDict defines all fields that can be present in the state.
    Agents read from and write to this state as the workflow progresses.
    """
    # Input fields
    topic: str
    tone: str
    target_audience: str
    min_words: int
    include_image: bool
    seo_optimize: bool

    # Agent outputs
    research_data: Optional[Dict[str, Any]]
    outline: Optional[str]
    content: Optional[str]
    edited_content: Optional[str]
    seo_meta: Optional[Dict[str, Any]]
    image_url: Optional[str]

    # Metadata
    current_agent: Optional[str]
    agent_logs: List[Dict[str, Any]]
    errors: List[str]
    status: str  # pending, processing, completed, failed


class ContentCreationWorkflow:
    """
    LangGraph-based workflow for orchestrating content creation agents.

    Manages the flow: Research → Outline → Writer → Editor → SEO → Image
    """

    def __init__(self):
        """Initialize workflow with all agents."""
        self.logger = logger
        
        # Initialize all agents
        self.research_agent = ResearchAgent()
        self.outline_agent = OutlineAgent()
        self.writer_agent = WriterAgent()
        self.editor_agent = EditorAgent()
        self.seo_agent = SEOAgent()
        self.image_agent = ImageAgent()
        
        # Build the workflow graph
        self.graph = self._build_graph()
        self.compiled_workflow = self.graph.compile()

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph StateGraph defining the agent workflow.

        Returns:
            StateGraph: Compiled workflow graph
        """
        # Create state graph with our state schema
        workflow = StateGraph(ContentCreationState)

        # Add nodes (each agent is a node)
        # Note: Node names must not conflict with state keys
        workflow.add_node("research_step", self._research_node)
        workflow.add_node("outline_step", self._outline_node)
        workflow.add_node("writer_step", self._writer_node)
        workflow.add_node("editor_step", self._editor_node)
        workflow.add_node("seo_step", self._seo_node)
        workflow.add_node("image_step", self._image_node)

        # Define edges (workflow flow)
        workflow.set_entry_point("research_step")  # Start with research
        workflow.add_edge("research_step", "outline_step")
        workflow.add_edge("outline_step", "writer_step")
        workflow.add_edge("writer_step", "editor_step")
        workflow.add_edge("editor_step", "seo_step")
        workflow.add_edge("seo_step", "image_step")
        workflow.add_edge("image_step", END)  # End after image generation

        return workflow

    # Node functions - each wraps an agent
    async def _research_node(self, state: ContentCreationState) -> ContentCreationState:
        """
        Research agent node - gathers web sources and information.

        Args:
            state: Current workflow state

        Returns:
            Updated state with research_data
        """
        logger.info("=== RESEARCH NODE START ===")
        state["current_agent"] = "ResearchAgent"

        try:
            # Prepare input for research agent
            input_data = {
                "topic": state["topic"],
                "tone": state.get("tone", "professional"),
                "target_audience": state.get("target_audience", "general"),
            }

            # Execute research agent
            response = await self.research_agent.run(input_data)

            # Update state with results
            if response.is_success():
                state["research_data"] = response.data
                
                # Log execution
                state.setdefault("agent_logs", []).append({
                    "agent": "ResearchAgent",
                    "status": "success",
                    "message": response.message,
                    "execution_time": response.execution_time,
                })
                
                logger.info(f"Research completed: {response.message}")
            else:
                # Handle error
                state.setdefault("errors", []).append(
                    f"ResearchAgent failed: {response.error}"
                )
                state["status"] = "failed"
                logger.error(f"Research failed: {response.error}")

        except Exception as e:
            logger.error(f"Research node exception: {str(e)}")
            state.setdefault("errors", []).append(f"Research node error: {str(e)}")
            state["status"] = "failed"

        logger.info("=== RESEARCH NODE END ===")
        return state

    async def _outline_node(self, state: ContentCreationState) -> ContentCreationState:
        """
        Outline agent node - creates content structure.

        Args:
            state: Current workflow state

        Returns:
            Updated state with outline
        """
        logger.info("=== OUTLINE NODE START ===")
        state["current_agent"] = "OutlineAgent"

        try:
            # Prepare input for outline agent
            input_data = {
                "research_data": state.get("research_data"),
                "topic": state["topic"],
                "tone": state.get("tone", "professional"),
                "target_audience": state.get("target_audience", "general"),
                "min_words": state.get("min_words", 800),
            }

            # Execute outline agent
            response = await self.outline_agent.run(input_data)

            # Update state with results
            if response.is_success():
                state["outline"] = response.data["outline"]
                
                # Log execution
                state.setdefault("agent_logs", []).append({
                    "agent": "OutlineAgent",
                    "status": "success",
                    "message": response.message,
                    "execution_time": response.execution_time,
                    "num_sections": response.data.get("num_sections", 0),
                })
                
                logger.info(f"Outline created: {response.message}")
            else:
                # Handle error
                state.setdefault("errors", []).append(
                    f"OutlineAgent failed: {response.error}"
                )
                logger.error(f"Outline failed: {response.error}")

        except Exception as e:
            logger.error(f"Outline node exception: {str(e)}")
            state.setdefault("errors", []).append(f"Outline node error: {str(e)}")

        logger.info("=== OUTLINE NODE END ===")
        return state

    async def _writer_node(self, state: ContentCreationState) -> ContentCreationState:
        """
        Writer agent node - generates article content.

        Args:
            state: Current workflow state

        Returns:
            Updated state with content
        """
        logger.info("=== WRITER NODE START ===")
        state["current_agent"] = "WriterAgent"

        try:
            # Prepare input for writer agent
            input_data = {
                "outline": state.get("outline"),
                "research_data": state.get("research_data"),
                "topic": state["topic"],
                "tone": state.get("tone", "professional"),
                "target_audience": state.get("target_audience", "general"),
                "min_words": state.get("min_words", 800),
            }

            # Execute writer agent
            response = await self.writer_agent.run(input_data)

            # Update state with results
            if response.is_success():
                state["content"] = response.data["content"]
                
                # Log execution
                state.setdefault("agent_logs", []).append({
                    "agent": "WriterAgent",
                    "status": "success",
                    "message": response.message,
                    "execution_time": response.execution_time,
                    "word_count": response.data.get("word_count", 0),
                })
                
                logger.info(f"Content written: {response.message}")
            else:
                # Handle error
                state.setdefault("errors", []).append(
                    f"WriterAgent failed: {response.error}"
                )
                logger.error(f"Writer failed: {response.error}")

        except Exception as e:
            logger.error(f"Writer node exception: {str(e)}")
            state.setdefault("errors", []).append(f"Writer node error: {str(e)}")

        logger.info("=== WRITER NODE END ===")
        return state

    async def _editor_node(self, state: ContentCreationState) -> ContentCreationState:
        """
        Editor agent node - reviews and improves content.

        Args:
            state: Current workflow state

        Returns:
            Updated state with edited_content
        """
        logger.info("=== EDITOR NODE START ===")
        state["current_agent"] = "EditorAgent"

        try:
            # Prepare input for editor agent
            input_data = {
                "content": state.get("content"),
                "topic": state["topic"],
                "research_data": state.get("research_data"),
                "tone": state.get("tone", "professional"),
                "target_audience": state.get("target_audience", "general"),
            }

            # Execute editor agent
            response = await self.editor_agent.run(input_data)

            # Update state with results
            if response.is_success():
                state["edited_content"] = response.data["edited_content"]
                
                # Log execution
                state.setdefault("agent_logs", []).append({
                    "agent": "EditorAgent",
                    "status": "success",
                    "message": response.message,
                    "execution_time": response.execution_time,
                    "improvements": response.data.get("improvements", {}),
                })
                
                logger.info(f"Content edited: {response.message}")
            else:
                # Handle error
                state.setdefault("errors", []).append(
                    f"EditorAgent failed: {response.error}"
                )
                logger.error(f"Editor failed: {response.error}")

        except Exception as e:
            logger.error(f"Editor node exception: {str(e)}")
            state.setdefault("errors", []).append(f"Editor node error: {str(e)}")

        logger.info("=== EDITOR NODE END ===")
        return state

    async def _seo_node(self, state: ContentCreationState) -> ContentCreationState:
        """
        SEO agent node - optimizes for search engines.

        Args:
            state: Current workflow state

        Returns:
            Updated state with seo_meta
        """
        logger.info("=== SEO NODE START ===")
        state["current_agent"] = "SEOAgent"

        # Skip SEO if not requested
        if not state.get("seo_optimize", True):
            logger.info("SEO optimization skipped per configuration")
            state.setdefault("agent_logs", []).append({
                "agent": "SEOAgent",
                "status": "skipped",
                "message": "SEO optimization disabled",
            })
            logger.info("=== SEO NODE END ===")
            return state

        try:
            # Prepare input for SEO agent
            input_data = {
                "edited_content": state.get("edited_content"),
                "content": state.get("content"),
                "topic": state["topic"],
                "target_audience": state.get("target_audience", "general"),
            }

            # Execute SEO agent
            response = await self.seo_agent.run(input_data)

            # Update state with results
            if response.is_success():
                state["seo_meta"] = response.data
                
                # Log execution
                state.setdefault("agent_logs", []).append({
                    "agent": "SEOAgent",
                    "status": "success",
                    "message": response.message,
                    "execution_time": response.execution_time,
                    "keywords_count": len(response.data.get("keywords", [])),
                })
                
                logger.info(f"SEO optimized: {response.message}")
            else:
                # Handle error
                state.setdefault("errors", []).append(
                    f"SEOAgent failed: {response.error}"
                )
                logger.error(f"SEO failed: {response.error}")

        except Exception as e:
            logger.error(f"SEO node exception: {str(e)}")
            state.setdefault("errors", []).append(f"SEO node error: {str(e)}")

        logger.info("=== SEO NODE END ===")
        return state

    async def _image_node(self, state: ContentCreationState) -> ContentCreationState:
        """
        Image agent node - generates cover image.

        Args:
            state: Current workflow state

        Returns:
            Updated state with image_url
        """
        logger.info("=== IMAGE NODE START ===")
        state["current_agent"] = "ImageAgent"

        try:
            # Prepare input for image agent
            input_data = {
                "topic": state["topic"],
                "edited_content": state.get("edited_content"),
                "content": state.get("content"),
                "include_image": state.get("include_image", True),
            }

            # Execute image agent
            response = await self.image_agent.run(input_data)

            # Update state with results
            if response.is_success():
                state["image_url"] = response.data.get("image_url")
                
                # Log execution
                state.setdefault("agent_logs", []).append({
                    "agent": "ImageAgent",
                    "status": "success" if response.data.get("image_url") else "skipped",
                    "message": response.message,
                    "execution_time": response.execution_time,
                    "image_generated": bool(response.data.get("image_url")),
                })
                
                logger.info(f"Image agent completed: {response.message}")
            else:
                # Handle error (non-critical)
                state.setdefault("errors", []).append(
                    f"ImageAgent failed: {response.error}"
                )
                logger.warning(f"Image generation failed: {response.error}")

        except Exception as e:
            logger.error(f"Image node exception: {str(e)}")
            state.setdefault("errors", []).append(f"Image node error: {str(e)}")

        logger.info("=== IMAGE NODE END ===")
        return state

    async def run(self, initial_state: Dict[str, Any]) -> ContentCreationState:
        """
        Execute the complete workflow.

        Args:
            initial_state: Initial state with user input (topic, tone, etc.)

        Returns:
            Final state after all agents have executed
        """
        logger.info("🚀 Starting content creation workflow...")
        
        # Initialize state
        state: ContentCreationState = {
            **initial_state,
            "status": "processing",
            "agent_logs": [],
            "errors": [],
        }

        try:
            # Run the compiled workflow
            final_state = await self.compiled_workflow.ainvoke(state)
            
            # Update final status
            if not final_state.get("errors"):
                final_state["status"] = "completed"
                logger.info("✅ Workflow completed successfully!")
            else:
                final_state["status"] = "failed"
                logger.error(f"❌ Workflow failed with {len(final_state['errors'])} errors")

            return final_state

        except Exception as e:
            logger.error(f"Workflow execution error: {str(e)}")
            state["status"] = "failed"
            state.setdefault("errors", []).append(f"Workflow error: {str(e)}")
            return state


# Convenience function for external use
async def create_article(
    topic: str,
    tone: str = "professional",
    target_audience: str = "general",
    min_words: int = 800,
    include_image: bool = True,
    seo_optimize: bool = True,
) -> ContentCreationState:
    """
    High-level function to create an article using the workflow.

    Args:
        topic: Article topic
        tone: Writing tone
        target_audience: Target audience
        min_words: Minimum word count
        include_image: Whether to generate image
        seo_optimize: Whether to apply SEO

    Returns:
        Final state with all generated content
    """
    workflow = ContentCreationWorkflow()
    
    initial_state = {
        "topic": topic,
        "tone": tone,
        "target_audience": target_audience,
        "min_words": min_words,
        "include_image": include_image,
        "seo_optimize": seo_optimize,
    }
    
    return await workflow.run(initial_state)

