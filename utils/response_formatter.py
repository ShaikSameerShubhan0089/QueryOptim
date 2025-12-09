import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Formats AI agent outputs into structured, user-friendly responses."""

    @staticmethod
    def format_analysis(
        original_query: str,
        schema_context: Dict[str, Any],
        explain_plan: Any,
        sample_rows: Any,
        optimizer_output: Dict[str, Any],
        cost_output: Dict[str, Any],
        schema_output: Dict[str, Any],
        data_validator_output: Dict[str, Any],
        database: str
    ) -> Dict[str, Any]:
        """Format all agent outputs into a comprehensive response."""

        return {
            "status": "success",
            "database": database,
            "original_query": original_query,
            "summary": ResponseFormatter._extract_summary(optimizer_output),
            "optimization": ResponseFormatter._format_optimizer(optimizer_output),
            "cost_analysis": ResponseFormatter._format_cost_advisor(cost_output),
            "schema_improvements": ResponseFormatter._format_schema_advisor(schema_output),
            "data_quality": ResponseFormatter._format_data_validator(data_validator_output),
            "technical_details": {
                "explain_plan": explain_plan,
                "sample_rows": sample_rows,
                "schema_context": schema_context
            }
        }

    @staticmethod
    def _extract_summary(optimizer_output: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key summary from optimizer."""
        if optimizer_output.get("status") == "error":
            return {
                "status": "error",
                "message": optimizer_output.get("details", {}).get("error", "Unknown error")
            }

        details = optimizer_output.get("details", {})
        return {
            "status": "success",
            "performance_impact": details.get("estimated_impact", "unknown"),
            "optimization_reason": details.get("why_faster", "Analysis in progress"),
            "key_recommendations": details.get("recommendations", [])[:3]
        }

    @staticmethod
    def _format_optimizer(optimizer_output: Dict[str, Any]) -> Dict[str, Any]:
        """Format Query Optimizer output."""
        if optimizer_output.get("status") == "error":
            return {
                "status": "error",
                "error": optimizer_output.get("details", {}).get("error", "Unknown error")
            }

        details = optimizer_output.get("details", {})
        return {
            "status": "success",
            "optimized_query": details.get("optimized_query", "No optimization available"),
            "performance_impact": details.get("estimated_impact", "unknown"),
            "why_faster": details.get("why_faster", ""),
            "recommendations": details.get("recommendations", []),
            "warnings": details.get("warnings", []),
            "engine_advice": details.get("engine_advice", []),
            "materialization_advice": details.get("materialization_advice", [])
        }

    @staticmethod
    def _format_cost_advisor(cost_output: Dict[str, Any]) -> Dict[str, Any]:
        """Format Cost Advisor output."""
        if cost_output.get("status") == "error":
            return {
                "status": "error",
                "error": cost_output.get("details", {}).get("error", "Unable to estimate cost")
            }

        details = cost_output.get("details", {})
        return {
            "status": "success",
            "estimated_cost": details.get("estimated_cost", "unknown"),
            "cost_saving_tips": details.get("cost_saving_tips", []),
            "warnings": details.get("warnings", [])
        }

    @staticmethod
    def _format_schema_advisor(schema_output: Dict[str, Any]) -> Dict[str, Any]:
        """Format Schema Advisor output."""
        if schema_output.get("status") == "error":
            return {
                "status": "error",
                "error": schema_output.get("details", {}).get("error", "Unable to analyze schema")
            }

        if schema_output.get("status") == "unsafe":
            return {
                "status": "unsafe",
                "message": "Query contains unsafe operations",
                "safe_query": schema_output.get("safe_query", ""),
                "reasoning": schema_output.get("details", {}).get("reasoning", "")
            }

        details = schema_output.get("details", {})
        return {
            "status": "success",
            "recommended_indexes": details.get("recommended_indexes", []),
            "schema_changes": details.get("schema_changes", []),
            "warnings": details.get("warnings", [])
        }

    @staticmethod
    def _format_data_validator(validator_output: Dict[str, Any]) -> Dict[str, Any]:
        """Format Data Validator output."""
        if validator_output.get("status") == "error":
            return {
                "status": "error",
                "error": validator_output.get("details", {}).get("error", "Unable to validate data")
            }

        details = validator_output.get("details", {})
        return {
            "status": "success",
            "issues": details.get("issues", []),
            "confidence": details.get("confidence", "unknown"),
            "reasoning": details.get("reasoning", "")
        }

    @staticmethod
    def format_error(error_message: str, agent_name: str = "System") -> Dict[str, Any]:
        """Format error response."""
        return {
            "status": "error",
            "agent": agent_name,
            "error": error_message
        }
