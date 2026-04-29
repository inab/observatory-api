import pytest
from fastapi import HTTPException

from app.helpers.fairsoft_evaluation import fairsoft_evaluation


@pytest.fixture
def tool_metadata():
    return {
        "name": "substrafl",
        "type": ["lib"],
        "version": ["0.47.0"],
        "source": ["github"],
        "repository": ["https://github.com/Substra/substrafl"],
        "webpage": ["https://docs.substra.org/"],
        "license": [
            {
                "name": "Apache License 2.0",
                "url": "http://choosealicense.com/licenses/apache-2.0/",
            }
        ],
        "documentation": [
            {
                "type": "readme",
                "url": "https://github.com/Substra/substrafl/blob/main/README.md",
            },
            {
                "type": "contributing",
                "url": "https://github.com/Substra/substrafl/blob/main/CONTRIBUTING.md",
            },
        ],
        "authors": [
            {
                "name": "Substra contributors",
                "type": "person",
            }
        ],
    }


@pytest.mark.asyncio
async def test_fairsoft_evaluation_runs_successfully(tool_metadata):
    result = await fairsoft_evaluation(
        tool_metadata=tool_metadata,
        prepare=False,
    )

    assert isinstance(result, dict)

    assert "result" in result
    assert "logs" in result
    assert "feedback" in result

    scores = result["result"]

    assert scores["name"] == "substrafl"
    assert scores["version"] == ["0.47.0"]

    for key in ["F", "A", "I", "R"]:
        assert key in scores
        assert isinstance(scores[key], float | int)
        assert 0 <= scores[key] <= 1

    assert isinstance(result["logs"], dict)
    assert isinstance(result["feedback"], dict)


