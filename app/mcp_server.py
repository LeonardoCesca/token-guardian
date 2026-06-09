from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from app.models.schemas import AnalyzePromptRequest, CompareModelsRequest
from app.services.analyzer_service import analyze_prompt, compare_models
from app.services.optimizer_service import optimize_prompt


mcp = FastMCP("token-guardian")


@mcp.tool()
def analyze_prompt_tool(
    provider: str,
    model: str,
    prompt: str,
    estimated_output_tokens: int | None = None,
) -> dict[str, object]:
    response = analyze_prompt(
        AnalyzePromptRequest(
            provider=provider,
            model=model,
            prompt=prompt,
            estimated_output_tokens=estimated_output_tokens,
        )
    )
    return response.model_dump()


@mcp.tool()
def compare_models_tool(
    prompt: str,
    estimated_output_tokens: int | None = None,
) -> dict[str, object]:
    response = compare_models(
        CompareModelsRequest(
            prompt=prompt,
            estimated_output_tokens=estimated_output_tokens,
        )
    )
    return response.model_dump()


@mcp.tool()
def optimize_prompt_tool(prompt: str) -> dict[str, object]:
    response = optimize_prompt(prompt)
    return response.model_dump()


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
