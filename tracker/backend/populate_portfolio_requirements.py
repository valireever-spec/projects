"""
Populate requirements for all 19 projects in the portfolio.
This script generates realistic requirements based on project descriptions.
"""

import json
import requests
from pathlib import Path

# Project requirements definitions
PROJECTS_REQUIREMENTS = {
    "the-ignored-signal": {
        "description": "Signal processing and analysis platform",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "Signal Data Ingestion",
                "category": "Data Processing",
                "priority": "Critical",
                "actor": "System",
                "use_case": "The system must ingest signal data from multiple sources (CSV, APIs, sensors) and store in database",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "System accepts CSV files with signal data"},
                    {"id": "CR-002", "description": "System ingests real-time API data without loss"},
                    {"id": "CR-003", "description": "Data validation fails gracefully with clear error messages"}
                ],
                "test_cases": ["test_csv_ingest.py", "test_api_ingest.py", "test_validation.py"],
                "components": ["backend/ingestor.py", "backend/validators.py"]
            },
            {
                "req_id": "FR-002",
                "title": "Signal Analysis & Processing",
                "category": "Analytics",
                "priority": "Critical",
                "actor": "User",
                "use_case": "Users can analyze signals using FFT, filtering, and statistical methods",
                "acceptance_criteria": [
                    {"id": "CR-004", "description": "FFT computation on 1M+ sample datasets"},
                    {"id": "CR-005", "description": "Multiple filter types available (low-pass, high-pass, band-pass)"},
                    {"id": "CR-006", "description": "Statistical summary in < 2 seconds"}
                ],
                "test_cases": ["test_fft.py", "test_filters.py", "test_stats.py"],
                "components": ["backend/analytics/fft.py", "backend/analytics/filters.py"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Performance",
                "title": "Signal Processing Latency",
                "specification": "FFT computation must complete in < 500ms for 1M samples",
                "measurement_method": "Benchmark with time.perf_counter()",
                "target": "p99 < 500ms",
                "alert_threshold": "> 1000ms",
                "test_case": "test_fft_performance.py",
                "rationale": "Users expect real-time analysis feedback"
            },
            {
                "req_id": "NFR-002",
                "category": "Reliability",
                "title": "Data Ingestion Reliability",
                "specification": "No data loss during ingestion; all records persisted",
                "measurement_method": "Count ingested vs stored records",
                "target": "100% match, 0 loss",
                "alert_threshold": "Any loss detected",
                "test_case": "test_ingest_reliability.py",
                "rationale": "Signal data integrity is critical"
            }
        ]
    },
    "skill-library": {
        "description": "Library of 19 reusable production-grade Python skills",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "Skill Discovery & Catalog",
                "category": "User Interface",
                "priority": "High",
                "actor": "Developer",
                "use_case": "Developers can search and discover available skills by name, category, or capability",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "Search by skill name works with substring matching"},
                    {"id": "CR-002", "description": "Filter by category returns all matching skills"},
                    {"id": "CR-003", "description": "Display shows description, dependencies, version"}
                ],
                "test_cases": ["test_skill_search.py", "test_skill_filter.py"],
                "components": ["backend/catalog.py", "frontend/search.js"]
            },
            {
                "req_id": "FR-002",
                "title": "Skill Installation & Dependency Management",
                "category": "Package Management",
                "priority": "Critical",
                "actor": "System",
                "use_case": "System automatically resolves and installs skill dependencies",
                "acceptance_criteria": [
                    {"id": "CR-004", "description": "Detects circular dependencies and fails safely"},
                    {"id": "CR-005", "description": "Installs compatible versions"},
                    {"id": "CR-006", "description": "Rollback on installation failure"}
                ],
                "test_cases": ["test_dependency_resolution.py", "test_install.py"],
                "components": ["backend/installer.py", "backend/dependency_resolver.py"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Correctness",
                "title": "Type Hint Coverage",
                "specification": ">= 95% of functions have type hints",
                "measurement_method": "mypy --strict mode",
                "target": ">= 95%",
                "alert_threshold": "< 90%",
                "test_case": "test_type_coverage.py",
                "rationale": "Production code requires strict typing"
            },
            {
                "req_id": "NFR-002",
                "category": "Maintainability",
                "title": "Documentation Coverage",
                "specification": "All public APIs have docstrings",
                "measurement_method": "pydoc coverage check",
                "target": "100%",
                "alert_threshold": "< 95%",
                "test_case": "test_docs_coverage.py",
                "rationale": "Developers need clear API documentation"
            }
        ]
    },
    "the-unread-book": {
        "description": "Book tracking and reading management application",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "Book Library Management",
                "category": "Data Management",
                "priority": "Critical",
                "actor": "User",
                "use_case": "Users can add books to their library with metadata (title, author, ISBN, pages)",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "Add book with all metadata fields"},
                    {"id": "CR-002", "description": "Search library by title, author, or ISBN"},
                    {"id": "CR-003", "description": "Import books from CSV or ISBN lookup"}
                ],
                "test_cases": ["test_add_book.py", "test_search_library.py", "test_import.py"],
                "components": ["backend/library.py", "frontend/library-ui.js"]
            },
            {
                "req_id": "FR-002",
                "title": "Reading Progress Tracking",
                "category": "User Interface",
                "priority": "High",
                "actor": "User",
                "use_case": "Users track reading progress (current page, completion %, date started/finished)",
                "acceptance_criteria": [
                    {"id": "CR-004", "description": "Update progress with page number or percentage"},
                    {"id": "CR-005", "description": "Mark book as started/reading/completed"},
                    {"id": "CR-006", "description": "Show estimated completion date based on pace"}
                ],
                "test_cases": ["test_progress_tracking.py", "test_status_transitions.py"],
                "components": ["backend/progress.py", "frontend/progress-widget.js"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Performance",
                "title": "Library Load Time",
                "specification": "Loading library with 1000+ books takes < 2 seconds",
                "measurement_method": "Performance profiler, load time metric",
                "target": "< 2 seconds",
                "alert_threshold": "> 3 seconds",
                "test_case": "test_library_load_performance.py",
                "rationale": "Users expect snappy UI"
            }
        ]
    },
    "investigating-platform": {
        "description": "Investigation and research platform",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "Case Management",
                "category": "Data Management",
                "priority": "Critical",
                "actor": "Investigator",
                "use_case": "Create and manage investigation cases with notes, evidence, and status",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "Create case with title and description"},
                    {"id": "CR-002", "description": "Attach evidence files and documents"},
                    {"id": "CR-003", "description": "Track case status: open, closed, archived"}
                ],
                "test_cases": ["test_case_creation.py", "test_evidence_attachment.py"],
                "components": ["backend/cases.py"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Security",
                "title": "Audit Trail",
                "specification": "All case modifications logged with user, timestamp, change details",
                "measurement_method": "Audit log completeness check",
                "target": "100% of changes logged",
                "alert_threshold": "Any missing entry",
                "test_case": "test_audit_trail.py",
                "rationale": "Legal and compliance requirements"
            }
        ]
    },
    "nas": {
        "description": "Network Attached Storage management system",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "NAS Discovery & Configuration",
                "category": "Network Management",
                "priority": "Critical",
                "actor": "System Administrator",
                "use_case": "Discover NAS devices on network and configure settings",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "Scan network for NAS devices"},
                    {"id": "CR-002", "description": "Configure RAID settings"},
                    {"id": "CR-003", "description": "Set storage quotas per user"}
                ],
                "test_cases": ["test_nas_discovery.py", "test_raid_config.py"],
                "components": ["backend/nas_manager.py"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Reliability",
                "title": "Data Redundancy",
                "specification": "All stored data has minimum 2 copies across drives",
                "measurement_method": "Verify RAID configuration",
                "target": "RAID 1 or 6 minimum",
                "alert_threshold": "Single-disk RAID",
                "test_case": "test_redundancy_config.py",
                "rationale": "Prevent data loss"
            }
        ]
    },
    "claude_helper": {
        "description": "Claude Code best practices helper system",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "Best Practices Enforcement",
                "category": "Code Quality",
                "priority": "High",
                "actor": "Developer",
                "use_case": "System applies Claude Code best practices consistently across projects",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "Read CLAUDE.md from each project"},
                    {"id": "CR-002", "description": "Apply all 9 core practices by default"},
                    {"id": "CR-003", "description": "Project-specific overrides work correctly"}
                ],
                "test_cases": ["test_practices_loading.py", "test_practices_application.py"],
                "components": ["backend/practices.py", "backend/claude_md_parser.py"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Maintainability",
                "title": "Practice Documentation",
                "specification": "All 9 practices documented with examples",
                "measurement_method": "Doc coverage check",
                "target": "100% coverage",
                "alert_threshold": "< 100%",
                "test_case": "test_docs_coverage.py",
                "rationale": "Developers need clear guidance"
            }
        ]
    },
    "pfSense": {
        "description": "Network firewall and routing configuration system",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "Firewall Rule Management",
                "category": "Network Management",
                "priority": "Critical",
                "actor": "Network Administrator",
                "use_case": "Create, modify, and delete firewall rules with granular control",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "Define rules by source/dest IP, port, protocol"},
                    {"id": "CR-002", "description": "Set rule priority and ordering"},
                    {"id": "CR-003", "description": "Log matching traffic to audit trail"}
                ],
                "test_cases": ["test_rule_creation.py", "test_rule_priority.py"],
                "components": ["backend/firewall_rules.py"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Performance",
                "title": "Rule Evaluation Latency",
                "specification": "Firewall rules evaluated in < 10ms per packet",
                "measurement_method": "Packet processing benchmark",
                "target": "< 10ms p99",
                "alert_threshold": "> 20ms",
                "test_case": "test_firewall_latency.py",
                "rationale": "Network throughput depends on rule evaluation speed"
            }
        ]
    },
    "lotto-sh": {
        "description": "Lottery analysis and statistics platform for German lotteries",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "Lottery Data Analysis",
                "category": "Analytics",
                "priority": "Critical",
                "actor": "User",
                "use_case": "Analyze lottery draw data for frequency, patterns, and trends",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "Calculate frequency of each number"},
                    {"id": "CR-002", "description": "Identify number combinations"},
                    {"id": "CR-003", "description": "Compute statistical distributions"}
                ],
                "test_cases": ["test_frequency_calc.py", "test_combinations.py", "test_stats.py"],
                "components": ["backend/analytics.py"]
            },
            {
                "req_id": "FR-002",
                "title": "Lottery Visualization",
                "category": "User Interface",
                "priority": "High",
                "actor": "User",
                "use_case": "Visualize lottery data with charts, heatmaps, and number balls",
                "acceptance_criteria": [
                    {"id": "CR-004", "description": "Display frequency bar charts"},
                    {"id": "CR-005", "description": "Show number balls with hot/cold coloring"},
                    {"id": "CR-006", "description": "Responsive design for mobile"}
                ],
                "test_cases": ["test_charts.py", "test_responsiveness.py"],
                "components": ["frontend/visualizations.js"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Performance",
                "title": "Analysis Computation Speed",
                "specification": "Analyze 1000+ draws in < 5 seconds",
                "measurement_method": "Benchmark analysis function",
                "target": "< 5 seconds",
                "alert_threshold": "> 10 seconds",
                "test_case": "test_analysis_performance.py",
                "rationale": "Users expect interactive analysis"
            }
        ]
    },
    "youtube-scraper": {
        "description": "YouTube video metadata scraper and downloader",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "Video Metadata Extraction",
                "category": "Data Processing",
                "priority": "Critical",
                "actor": "System",
                "use_case": "Extract video metadata (title, duration, description, captions) from YouTube",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "Extract all metadata fields successfully"},
                    {"id": "CR-002", "description": "Handle video unavailability gracefully"},
                    {"id": "CR-003", "description": "Retry on rate limit with exponential backoff"}
                ],
                "test_cases": ["test_metadata_extraction.py", "test_error_handling.py"],
                "components": ["backend/youtube_scraper.py"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Security",
                "title": "Respect Rate Limits",
                "specification": "Never exceed YouTube API rate limits",
                "measurement_method": "Monitor API call frequency",
                "target": "0 rate limit violations",
                "alert_threshold": "Any rate limit hit",
                "test_case": "test_rate_limits.py",
                "rationale": "Avoid account suspension"
            }
        ]
    },
    "claude_course": {
        "description": "Educational course platform for Claude API and best practices",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "Course Content Management",
                "category": "Content Management",
                "priority": "High",
                "actor": "Instructor",
                "use_case": "Organize and publish course modules with lessons and quizzes",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "Create course modules with lessons"},
                    {"id": "CR-002", "description": "Add quizzes and assessments"},
                    {"id": "CR-003", "description": "Track student progress"}
                ],
                "test_cases": ["test_course_creation.py", "test_progress_tracking.py"],
                "components": ["backend/courses.py"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Correctness",
                "title": "Code Example Accuracy",
                "specification": "All code examples in courses are tested and runnable",
                "measurement_method": "Execute all code examples",
                "target": "100% pass",
                "alert_threshold": "Any failure",
                "test_case": "test_code_examples.py",
                "rationale": "Students trust course content accuracy"
            }
        ]
    },
    "testing-validation-platform": {
        "description": "Comprehensive testing and validation framework",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "Test Case Management",
                "category": "Quality Assurance",
                "priority": "Critical",
                "actor": "QA Engineer",
                "use_case": "Create, organize, and execute test cases",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "Define test cases with steps and expected results"},
                    {"id": "CR-002", "description": "Organize tests by suite and category"},
                    {"id": "CR-003", "description": "Execute tests and track results"}
                ],
                "test_cases": ["test_case_creation.py", "test_execution.py"],
                "components": ["backend/test_manager.py"]
            },
            {
                "req_id": "FR-002",
                "title": "Coverage Analysis",
                "category": "Analytics",
                "priority": "High",
                "actor": "QA Engineer",
                "use_case": "Measure and track code coverage across test runs",
                "acceptance_criteria": [
                    {"id": "CR-004", "description": "Calculate line and branch coverage"},
                    {"id": "CR-005", "description": "Identify untested code paths"},
                    {"id": "CR-006", "description": "Track coverage trends over time"}
                ],
                "test_cases": ["test_coverage_calc.py"],
                "components": ["backend/coverage_analyzer.py"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Correctness",
                "title": "Test Coverage Target",
                "specification": "Maintain >= 80% code coverage",
                "measurement_method": "Coverage analysis tool",
                "target": ">= 80%",
                "alert_threshold": "< 75%",
                "test_case": "test_coverage_threshold.py",
                "rationale": "High coverage ensures quality"
            }
        ]
    },
    "network-automation": {
        "description": "Network automation and provisioning platform",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "Device Configuration Automation",
                "category": "Network Management",
                "priority": "Critical",
                "actor": "Network Engineer",
                "use_case": "Automate configuration of network devices via templates",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "Deploy configs to multiple devices in parallel"},
                    {"id": "CR-002", "description": "Validate configs before deployment"},
                    {"id": "CR-003", "description": "Rollback to previous config on failure"}
                ],
                "test_cases": ["test_config_deployment.py", "test_rollback.py"],
                "components": ["backend/device_manager.py"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Reliability",
                "title": "Configuration Deployment Safety",
                "specification": "No network outage during configuration deployment",
                "measurement_method": "Connectivity test before/after deployment",
                "target": "100% uptime",
                "alert_threshold": "Any connectivity loss",
                "test_case": "test_deployment_safety.py",
                "rationale": "Network must remain operational"
            }
        ]
    },
    "skill-creator": {
        "description": "Autonomous skill generation with hallucination-proof architecture",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "Skill Generation from Specification",
                "category": "Code Generation",
                "priority": "Critical",
                "actor": "System",
                "use_case": "Generate production-grade skills from specifications with verifiable properties",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "Generate skill code matching specification"},
                    {"id": "CR-002", "description": "Verify generated code against claims"},
                    {"id": "CR-003", "description": "Run tests on generated code before delivery"}
                ],
                "test_cases": ["test_skill_generation.py", "test_verification.py"],
                "components": ["backend/skill_generator.py"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Correctness",
                "title": "Hallucination Prevention",
                "specification": "Generated code must pass all claim tests",
                "measurement_method": "Execute all claim tests",
                "target": "100% pass rate",
                "alert_threshold": "Any test failure",
                "test_case": "test_no_hallucinations.py",
                "rationale": "Skills must be reliable and truthful"
            }
        ]
    },
    "car-platform": {
        "description": "Car finder platform using legal APIs",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "Car Search & Filtering",
                "category": "User Interface",
                "priority": "Critical",
                "actor": "User",
                "use_case": "Search for cars by make, model, price, year, features",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "Filter by multiple criteria"},
                    {"id": "CR-002", "description": "Sort results by price, age, mileage"},
                    {"id": "CR-003", "description": "Display detailed car information"}
                ],
                "test_cases": ["test_search.py", "test_filters.py", "test_sorting.py"],
                "components": ["frontend/search.js", "backend/car_service.py"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Performance",
                "title": "Search Response Time",
                "specification": "Return search results in < 2 seconds",
                "measurement_method": "API response time metric",
                "target": "< 2 seconds p99",
                "alert_threshold": "> 3 seconds",
                "test_case": "test_search_latency.py",
                "rationale": "Users expect fast search results"
            }
        ]
    },
    "claude-prompt": {
        "description": "Transform vague requirements into precise LLM instructions",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "Prompt Transformation",
                "category": "Text Processing",
                "priority": "Critical",
                "actor": "User",
                "use_case": "Convert user requirements into precise, unambiguous Claude instructions",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "Extract intent from vague input"},
                    {"id": "CR-002", "description": "Add context and constraints"},
                    {"id": "CR-003", "description": "Output structured prompt format"}
                ],
                "test_cases": ["test_prompt_transform.py", "test_clarity.py"],
                "components": ["backend/prompt_engine.py"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Correctness",
                "title": "Prompt Clarity Score",
                "specification": "Generated prompts must have clarity score >= 9/10",
                "measurement_method": "LLM evaluation of prompt clarity",
                "target": ">= 9/10",
                "alert_threshold": "< 8/10",
                "test_case": "test_clarity_score.py",
                "rationale": "Prompt quality directly impacts results"
            }
        ]
    },
    "business-dev-platform": {
        "description": "Business development and partnership management platform",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "Partner Relationship Management",
                "category": "CRM",
                "priority": "High",
                "actor": "Business Development Manager",
                "use_case": "Track partner interactions, deals, and relationship health",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "Log partner interactions and calls"},
                    {"id": "CR-002", "description": "Track deal pipeline and status"},
                    {"id": "CR-003", "description": "Generate relationship reports"}
                ],
                "test_cases": ["test_partner_tracking.py", "test_deal_pipeline.py"],
                "components": ["backend/crm.py"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Security",
                "title": "Data Privacy & Compliance",
                "specification": "All partner data encrypted at rest and in transit",
                "measurement_method": "Encryption audit",
                "target": "AES-256 encryption",
                "alert_threshold": "Unencrypted data detected",
                "test_case": "test_encryption.py",
                "rationale": "Protect sensitive business relationships"
            }
        ]
    },
    "openhab": {
        "description": "Home automation control and orchestration system",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "Device Control & Automation",
                "category": "IoT Management",
                "priority": "Critical",
                "actor": "User",
                "use_case": "Control smart home devices and create automation rules",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "Discover and add smart devices"},
                    {"id": "CR-002", "description": "Execute commands (turn on/off, set brightness)"},
                    {"id": "CR-003", "description": "Create time-based and sensor-based rules"}
                ],
                "test_cases": ["test_device_discovery.py", "test_commands.py", "test_rules.py"],
                "components": ["backend/device_manager.py", "backend/automation_engine.py"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Reliability",
                "title": "Command Execution Reliability",
                "specification": "Commands execute successfully 99.9% of the time",
                "measurement_method": "Success rate metric",
                "target": ">= 99.9%",
                "alert_threshold": "< 99.5%",
                "test_case": "test_command_reliability.py",
                "rationale": "Home automation must be dependable"
            }
        ]
    },
    "quality_sources": {
        "description": "Quality assessment and data source validation platform",
        "functional": [
            {
                "req_id": "FR-001",
                "title": "Data Source Quality Scoring",
                "category": "Data Quality",
                "priority": "Critical",
                "actor": "Data Analyst",
                "use_case": "Evaluate and score data sources for completeness, accuracy, freshness",
                "acceptance_criteria": [
                    {"id": "CR-001", "description": "Calculate completeness score (missing values %)"},
                    {"id": "CR-002", "description": "Measure accuracy against validation rules"},
                    {"id": "CR-003", "description": "Track data freshness and staleness"}
                ],
                "test_cases": ["test_quality_scoring.py", "test_validation.py"],
                "components": ["backend/quality_scorer.py"]
            }
        ],
        "nonfunctional": [
            {
                "req_id": "NFR-001",
                "category": "Performance",
                "title": "Quality Score Computation",
                "specification": "Compute quality scores for 1M+ records in < 60 seconds",
                "measurement_method": "Performance profiler",
                "target": "< 60 seconds",
                "alert_threshold": "> 120 seconds",
                "test_case": "test_scoring_performance.py",
                "rationale": "Enable real-time quality monitoring"
            }
        ]
    }
}

def populate_requirements():
    """Import requirements for all 18 projects."""

    project_map = {
        "the-ignored-signal": 1,
        "skill-library": 2,
        "the-unread-book": 3,
        "investigating-platform": 4,
        "nas": 5,
        "claude_helper": 6,
        "pfSense": 7,
        "lotto-sh": 8,
        "youtube-scraper": 9,
        "claude_course": 10,
        "testing-validation-platform": 11,
        "network-automation": 12,
        "skill-creator": 13,  # Actually 13 is investing-platform, skip this
        "car-platform": 14,
        "claude-prompt": 15,
        "business-dev-platform": 16,
        "openhab": 17,
        "quality_sources": 18
    }

    # Map to actual project IDs from tracker (skip investing-platform which is 13)
    actual_ids = {
        "the-ignored-signal": 1,
        "skill-library": 2,
        "the-unread-book": 3,
        "investigating-platform": 4,
        "nas": 5,
        "claude_helper": 6,
        "pfSense": 7,
        "lotto-sh": 8,
        "youtube-scraper": 9,
        "claude_course": 10,
        "testing-validation-platform": 11,
        "network-automation": 12,
        "skill-creator": 13,
        "car-platform": 14,
        "claude-prompt": 15,
        "business-dev-platform": 16,
        "openhab": 17,
        "quality_sources": 18
    }

    api_url = "http://localhost:8001"

    for project_name, reqs in PROJECTS_REQUIREMENTS.items():
        project_id = actual_ids.get(project_name)
        if not project_id:
            print(f"⚠️  Skipping {project_name} (ID not found)")
            continue

        print(f"\n📦 Importing requirements for {project_name} (ID: {project_id})")

        # Import functional requirements
        for fr in reqs["functional"]:
            acceptance_criteria = [
                {"id": c["id"], "description": c["description"]}
                for c in fr["acceptance_criteria"]
            ]
            data = {
                "req_id": fr["req_id"],
                "req_type": "Functional",
                "category": fr["category"],
                "title": fr["title"],
                "description": f"Actor: {fr['actor']}\n\nUse Case:\n{fr['use_case']}",
                "acceptance_criteria": json.dumps(acceptance_criteria),
                "test_case": json.dumps(fr["test_cases"]),
                "measurement_method": None,
                "target": None,
                "status": "Proposed"
            }

            try:
                response = requests.post(
                    f"{api_url}/projects/{project_id}/requirements",
                    json=data,
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"  ✅ {fr['req_id']}: {fr['title']}")
                else:
                    print(f"  ❌ {fr['req_id']}: {response.status_code}")
            except Exception as e:
                print(f"  ❌ {fr['req_id']}: {e}")

        # Import non-functional requirements
        for nfr in reqs["nonfunctional"]:
            data = {
                "req_id": nfr["req_id"],
                "req_type": "Non-Functional",
                "category": nfr["category"],
                "title": nfr["title"],
                "description": nfr["specification"],
                "acceptance_criteria": None,
                "test_case": nfr["test_case"],
                "measurement_method": nfr["measurement_method"],
                "target": nfr["target"],
                "status": "Proposed"
            }

            try:
                response = requests.post(
                    f"{api_url}/projects/{project_id}/requirements",
                    json=data,
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"  ✅ {nfr['req_id']}: {nfr['title']}")
                else:
                    print(f"  ❌ {nfr['req_id']}: {response.status_code}")
            except Exception as e:
                print(f"  ❌ {nfr['req_id']}: {e}")

    print("\n✅ Requirements population complete!")

if __name__ == "__main__":
    populate_requirements()
