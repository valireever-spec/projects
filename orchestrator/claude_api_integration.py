"""
Real Claude API Integration - Phase 3 Orchestrator Component

Integrates with Anthropic Claude API (Opus 4.8) for intelligent requirement analysis.
Replaces mock analysis with real AI-powered design decisions.
"""

import logging
import os
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from collections import defaultdict
import time

logger = logging.getLogger(__name__)

try:
    from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    logger.warning("Anthropic SDK not installed, Claude API unavailable")


class ModelType(Enum):
    """Available Claude models."""
    OPUS_4_8 = "claude-opus-4-8-20250514"
    SONNET_4_6 = "claude-sonnet-4-6-20250514"
    HAIKU_4_5 = "claude-haiku-4-5-20251001"


@dataclass
class TokenUsage:
    """Token usage statistics."""
    input_tokens: int
    output_tokens: int
    total_tokens: int = None
    timestamp: str = None

    def __post_init__(self):
        if self.total_tokens is None:
            self.total_tokens = self.input_tokens + self.output_tokens
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class AnalysisResponse:
    """Response from Claude analysis."""
    requirement_id: str
    requirement_title: str
    decisions: List[Dict]
    implementation_tasks: List[str]
    estimated_effort_hours: float
    risks: List[str]
    model: str
    tokens_used: TokenUsage
    confidence: float  # 0-1 scale


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_requests_per_minute: int = 5):
        """Initialize rate limiter.

        Args:
            max_requests_per_minute: Max requests allowed per minute
        """
        self.max_requests = max_requests_per_minute
        self.request_times = []
        self.lock_until = 0

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()

        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]

        if len(self.request_times) >= self.max_requests:
            wait_time = 60 - (now - self.request_times[0])
            if wait_time > 0:
                logger.warning(f"Rate limit: waiting {wait_time:.1f}s")
                time.sleep(wait_time)

        self.request_times.append(time.time())


class ClaudeAPIClient:
    """Client for real Claude API with error handling."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-opus-4-8-20250514"):
        """Initialize Claude API client.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use

        Raises:
            ValueError: If API key not found
        """
        if not HAS_ANTHROPIC:
            raise RuntimeError("Anthropic SDK not installed. Install with: pip install anthropic")

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No API key provided. Set ANTHROPIC_API_KEY environment variable or pass api_key parameter."
            )

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.rate_limiter = RateLimiter(max_requests_per_minute=5)
        self.total_tokens = 0
        self.total_requests = 0
        self.total_cost = 0.0

        logger.info(f"Initialized ClaudeAPIClient with model {model}")

    def _estimate_cost(self, tokens_used: TokenUsage) -> float:
        """Estimate cost for token usage.

        Args:
            tokens_used: Token usage info

        Returns:
            Estimated cost in USD
        """
        # Pricing as of 2024 (approximate)
        if "opus" in self.model.lower():
            input_price = 0.015 / 1000  # $15 per 1M input tokens
            output_price = 0.045 / 1000  # $45 per 1M output tokens
        elif "sonnet" in self.model.lower():
            input_price = 0.003 / 1000  # $3 per 1M input tokens
            output_price = 0.015 / 1000  # $15 per 1M output tokens
        else:
            input_price = 0.00080 / 1000  # $0.80 per 1M input tokens
            output_price = 0.0024 / 1000  # $2.40 per 1M output tokens

        cost = (tokens_used.input_tokens * input_price) + (tokens_used.output_tokens * output_price)
        return cost

    def analyze_requirement(self, requirement_id: str, title: str, description: str,
                           acceptance_criteria: str = "", requirement_type: str = "feature") -> Optional[AnalysisResponse]:
        """Analyze requirement using real Claude API.

        Args:
            requirement_id: Unique requirement ID
            title: Requirement title
            description: Requirement description
            acceptance_criteria: Acceptance criteria
            requirement_type: Type (feature, bugfix, refactor, optimization)

        Returns:
            AnalysisResponse with decisions and tasks, or None on error
        """
        try:
            self.rate_limiter.wait_if_needed()

            prompt = self._build_analysis_prompt(
                title, description, acceptance_criteria, requirement_type
            )

            logger.info(f"Calling Claude Opus for requirement: {requirement_id}")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse response
            response_text = response.content[0].text
            parsed = self._parse_analysis_response(response_text)

            # Track usage
            tokens_used = TokenUsage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens
            )

            cost = self._estimate_cost(tokens_used)
            self.total_tokens += tokens_used.total_tokens
            self.total_cost += cost
            self.total_requests += 1

            logger.info(
                f"Analysis complete: {tokens_used.total_tokens} tokens, ${cost:.4f}"
            )

            return AnalysisResponse(
                requirement_id=requirement_id,
                requirement_title=title,
                decisions=parsed.get('decisions', []),
                implementation_tasks=parsed.get('tasks', []),
                estimated_effort_hours=parsed.get('effort', 16.0),
                risks=parsed.get('risks', []),
                model=self.model,
                tokens_used=tokens_used,
                confidence=0.95
            )

        except (APIConnectionError, APIError) as e:
            logger.error(f"Claude API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error analyzing requirement: {e}")
            return None

    def _build_analysis_prompt(self, title: str, description: str,
                              acceptance_criteria: str, req_type: str) -> str:
        """Build prompt for Claude analysis.

        Args:
            title: Requirement title
            description: Requirement description
            acceptance_criteria: Acceptance criteria
            req_type: Requirement type

        Returns:
            Formatted prompt
        """
        prompt = f"""Analyze this software requirement and provide design guidance.

Requirement Type: {req_type}
Title: {title}
Description: {description}

Acceptance Criteria:
{acceptance_criteria if acceptance_criteria else "Not specified"}

Provide your analysis in the following JSON format (no markdown, just raw JSON):
{{
  "decisions": [
    {{"title": "decision 1", "rationale": "why", "confidence": 0.95}},
    {{"title": "decision 2", "rationale": "why", "confidence": 0.90}}
  ],
  "tasks": ["task 1", "task 2", "task 3"],
  "effort": 16.0,
  "risks": ["risk 1", "risk 2"]
}}

Focus on:
1. Architectural decisions
2. Technology choices
3. Integration points
4. Testing strategy
5. Security considerations

Be concise and practical."""
        return prompt

    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse Claude's JSON response.

        Args:
            response_text: Raw response text

        Returns:
            Parsed analysis dict
        """
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                logger.warning("Could not find JSON in response, using defaults")
                return {
                    'decisions': [],
                    'tasks': ['Design API', 'Implement logic', 'Add tests', 'Document', 'Deploy'],
                    'effort': 16.0,
                    'risks': []
                }

            json_str = response_text[json_start:json_end]
            parsed = json.loads(json_str)

            return {
                'decisions': parsed.get('decisions', []),
                'tasks': parsed.get('tasks', []),
                'effort': float(parsed.get('effort', 16.0)),
                'risks': parsed.get('risks', [])
            }

        except json.JSONDecodeError as e:
            logger.error(f"Could not parse Claude response as JSON: {e}")
            return {
                'decisions': [],
                'tasks': ['Design', 'Implement', 'Test', 'Deploy'],
                'effort': 16.0,
                'risks': ['Parsing failed']
            }

    def get_usage_stats(self) -> Dict:
        """Get API usage statistics.

        Returns:
            Dict with usage metrics
        """
        return {
            'total_requests': self.total_requests,
            'total_tokens': self.total_tokens,
            'estimated_cost': f"${self.total_cost:.4f}",
            'model': self.model,
            'avg_tokens_per_request': self.total_tokens // self.total_requests if self.total_requests > 0 else 0
        }

    def health_check(self) -> bool:
        """Verify Claude API is accessible.

        Returns:
            True if API is accessible
        """
        try:
            # Make a minimal test call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[
                    {
                        "role": "user",
                        "content": "Say OK"
                    }
                ]
            )
            logger.info("Claude API health check passed")
            return True

        except Exception as e:
            logger.warning(f"Claude API health check failed: {e}")
            return False


class ClaudeIntegration:
    """Integration layer for Claude API with orchestrator."""

    def __init__(self, api_key: Optional[str] = None, use_real_api: bool = True):
        """Initialize Claude integration.

        Args:
            api_key: Anthropic API key
            use_real_api: Whether to use real API or mock
        """
        self.use_real_api = use_real_api
        self.client = None
        self.fallback_enabled = True

        if use_real_api:
            try:
                self.client = ClaudeAPIClient(api_key)
                logger.info("Initialized with real Claude API")
            except Exception as e:
                logger.warning(f"Could not initialize Claude API: {e}")
                logger.warning("Will use mock analysis as fallback")
                self.use_real_api = False

    def is_available(self) -> bool:
        """Check if Claude API is available.

        Returns:
            True if API is ready to use
        """
        if not self.use_real_api:
            return False

        if self.client is None:
            return False

        return self.client.health_check()

    def analyze_requirement(self, requirement_id: str, title: str, description: str,
                           acceptance_criteria: str = "",
                           requirement_type: str = "feature") -> Optional[Dict]:
        """Analyze requirement with fallback to mock.

        Args:
            requirement_id: Requirement ID
            title: Requirement title
            description: Description
            acceptance_criteria: Acceptance criteria
            requirement_type: Requirement type

        Returns:
            Dict with analysis or None
        """
        if self.use_real_api and self.client:
            try:
                response = self.client.analyze_requirement(
                    requirement_id, title, description,
                    acceptance_criteria, requirement_type
                )

                if response:
                    return {
                        'requirement_id': response.requirement_id,
                        'title': response.requirement_title,
                        'decisions': response.decisions,
                        'tasks': response.implementation_tasks,
                        'effort': response.estimated_effort_hours,
                        'risks': response.risks,
                        'model': response.model,
                        'tokens': {
                            'input': response.tokens_used.input_tokens,
                            'output': response.tokens_used.output_tokens,
                            'total': response.tokens_used.total_tokens
                        },
                        'confidence': response.confidence,
                        'source': 'real_api'
                    }

            except Exception as e:
                logger.error(f"Claude API call failed: {e}")

                if not self.fallback_enabled:
                    return None

                logger.info("Falling back to mock analysis")

        # Fallback to mock
        return self._mock_analysis(requirement_id, title, description, requirement_type)

    def _mock_analysis(self, requirement_id: str, title: str, description: str,
                      requirement_type: str) -> Dict:
        """Provide mock analysis (fallback).

        Args:
            requirement_id: Requirement ID
            title: Title
            description: Description
            requirement_type: Type

        Returns:
            Mock analysis dict
        """
        logger.info(f"Using mock analysis for {requirement_id}")

        effort_map = {
            'bugfix': 4.0,
            'feature': 16.0,
            'refactor': 12.0,
            'optimization': 8.0
        }

        return {
            'requirement_id': requirement_id,
            'title': title,
            'decisions': [
                {'title': 'Use existing abstraction layer', 'rationale': 'Minimize changes', 'confidence': 0.90},
                {'title': 'Add comprehensive tests', 'rationale': 'Ensure quality', 'confidence': 1.0},
                {'title': 'Document public API', 'rationale': 'Enable maintainability', 'confidence': 0.95}
            ],
            'tasks': [
                'Design interfaces',
                'Implement logic',
                'Add unit tests',
                'Add integration tests',
                'Write documentation',
                'Code review and merge'
            ],
            'effort': effort_map.get(requirement_type.lower(), 16.0),
            'risks': ['Standard engineering risks'],
            'model': 'mock',
            'tokens': {'input': 0, 'output': 0, 'total': 0},
            'confidence': 0.75,
            'source': 'mock_fallback'
        }

    def get_usage_stats(self) -> Dict:
        """Get API usage statistics.

        Returns:
            Usage stats dict
        """
        if self.client:
            return self.client.get_usage_stats()

        return {
            'total_requests': 0,
            'total_tokens': 0,
            'estimated_cost': '$0.0000',
            'model': 'mock',
            'source': 'mock'
        }


# Test usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    print("\n" + "="*80)
    print("CLAUDE API INTEGRATION TEST")
    print("="*80 + "\n")

    # Try to initialize with real API
    print("1️⃣ Initializing Claude API client...")
    try:
        integration = ClaudeIntegration(use_real_api=True)
        print(f"   ✓ Initialized")
    except Exception as e:
        print(f"   ⚠ Real API unavailable: {e}")
        print(f"   Using mock fallback")
        integration = ClaudeIntegration(use_real_api=False)

    # Check availability
    print("\n2️⃣ Checking Claude API availability...")
    available = integration.is_available()
    print(f"   {'✓' if available else '✗'} API available: {available}")

    # Test analysis
    print("\n3️⃣ Analyzing requirement with Claude...")
    result = integration.analyze_requirement(
        "REQ-CLAUDE-001",
        "Implement user authentication",
        "Add JWT-based authentication to protect API endpoints",
        "Secure tokens, refresh logic, logout functionality",
        "feature"
    )

    if result:
        print(f"   ✓ Analysis complete")
        print(f"   ✓ Source: {result['source']}")
        print(f"   ✓ Model: {result['model']}")
        print(f"   ✓ Decisions: {len(result['decisions'])}")
        print(f"   ✓ Tasks: {len(result['tasks'])}")
        print(f"   ✓ Effort: {result['effort']} hours")
        if result['tokens']['total'] > 0:
            print(f"   ✓ Tokens: {result['tokens']['total']} (${result['tokens']['total'] * 0.00002:.4f})")
    else:
        print(f"   ✗ Analysis failed")

    # Get usage stats
    print("\n4️⃣ API Usage Statistics...")
    stats = integration.get_usage_stats()
    for key, value in stats.items():
        print(f"   ✓ {key}: {value}")

    print("\n✓ Claude API integration test complete\n")
