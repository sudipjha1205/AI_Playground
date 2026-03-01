"""
Personality Analyzer Tools - MCP-style structured tools for personality profiling.
"""
import logging
from tools.base_tool import ToolResult, extract_code_block, safe_json_parse, strip_code_blocks

logger = logging.getLogger(__name__)

DEFAULT_ANALYSIS_STATE = {
    "phase": "interviewing",
    "questions_asked": 0,
    "current_question": 1,
    "responses_collected": 0,
    "report_ready": False,
    "big_five": {
        "openness": None,
        "conscientiousness": None,
        "extraversion": None,
        "agreeableness": None,
        "neuroticism": None
    },
    "archetype": None,
    "mbti_type": None
}


def parse_personality_response(raw_response: str) -> ToolResult:
    """
    Tool: Parse and validate personality analyzer agent response.
    Extracts analysis_state JSON and PSYCHE narrative.
    """
    tool_name = "parse_personality_response"
    
    try:
        analysis_state_raw = extract_code_block(raw_response, "analysis_state")
        
        if analysis_state_raw:
            analysis_state = safe_json_parse(analysis_state_raw, DEFAULT_ANALYSIS_STATE.copy())
        else:
            analysis_state = DEFAULT_ANALYSIS_STATE.copy()
            logger.warning("No analysis_state block found")
        
        # Validate and set defaults
        analysis_state.setdefault("phase", "interviewing")
        analysis_state.setdefault("questions_asked", 0)
        analysis_state.setdefault("current_question", 1)
        analysis_state.setdefault("responses_collected", 0)
        analysis_state.setdefault("report_ready", False)
        analysis_state.setdefault("big_five", {})
        analysis_state.setdefault("archetype", None)
        analysis_state.setdefault("mbti_type", None)
        
        narrative = strip_code_blocks(raw_response)
        
        big_five = analysis_state.get("big_five", {})
        progress_pct = (analysis_state["questions_asked"] / 5) * 100
        
        return ToolResult(
            success=True,
            data={
                "narrative": narrative,
                "analysis_state": analysis_state,
                "phase": analysis_state["phase"],
                "questions_asked": analysis_state["questions_asked"],
                "current_question": analysis_state["current_question"],
                "report_ready": analysis_state["report_ready"],
                "big_five": big_five,
                "archetype": analysis_state["archetype"],
                "mbti_type": analysis_state["mbti_type"],
                "progress_pct": progress_pct,
                "questions_left": max(0, 5 - analysis_state["questions_asked"])
            },
            tool_name=tool_name
        )
    except Exception as e:
        logger.error(f"Error in {tool_name}: {e}")
        return ToolResult(
            success=False,
            data={"narrative": raw_response, "analysis_state": DEFAULT_ANALYSIS_STATE.copy()},
            error=str(e),
            tool_name=tool_name
        )


def format_big_five_chart(big_five: dict) -> ToolResult:
    """Tool: Format Big Five scores for display."""
    traits = {
        "openness": ("Openness", "🎨", "Creativity & curiosity"),
        "conscientiousness": ("Conscientiousness", "📋", "Organization & discipline"),
        "extraversion": ("Extraversion", "⚡", "Social energy & assertiveness"),
        "agreeableness": ("Agreeableness", "💫", "Cooperation & empathy"),
        "neuroticism": ("Neuroticism", "🌊", "Emotional sensitivity")
    }
    
    formatted = []
    for key, (label, emoji, desc) in traits.items():
        score = big_five.get(key)
        if score is not None:
            formatted.append({
                "trait": label,
                "emoji": emoji,
                "description": desc,
                "score": int(score),
                "key": key
            })
    
    return ToolResult(
        success=True,
        data={"traits": formatted, "count": len(formatted)},
        tool_name="format_big_five_chart"
    )
