"""Small, labeled scenarios for the context-selection experiment."""

SCENARIOS = [
    {
        "id": "distractor-removal",
        "title": "Remove distractors",
        "question": "Who first walked on the Moon, and when?",
        "research_question": (
            "Can query-aware selection remove unrelated passages without losing "
            "the passage that contains the answer?"
        ),
        "source": {
            "label": "LongLLMLingua (ACL 2024)",
            "url": "https://aclanthology.org/2024.acl-long.91/",
        },
        "chunks": [
            {
                "text": (
                    "The Moon is Earth's only natural satellite and orbits at an "
                    "average distance of about 384,400 kilometres."
                ),
                "is_evidence": False,
            },
            {
                "text": (
                    "Apollo 11 landed on July 20, 1969. Neil Armstrong became the "
                    "first person to step onto the lunar surface."
                ),
                "is_evidence": True,
            },
            {
                "text": (
                    "NASA's Artemis programme is intended to return people to the "
                    "Moon using the Space Launch System and Orion spacecraft."
                ),
                "is_evidence": False,
            },
            {
                "text": (
                    "The Soviet Luna programme achieved the first robotic soft "
                    "landing on the Moon with Luna 9 in 1966."
                ),
                "is_evidence": False,
            },
            {
                "text": (
                    "Moonlight is reflected sunlight, and the lunar surface has a "
                    "relatively low albedo."
                ),
                "is_evidence": False,
            },
        ],
    },
    {
        "id": "multi-hop",
        "title": "Keep both steps",
        "question": "Which band did Andrew Wood lead before Mother Love Bone?",
        "research_question": (
            "Can one embedding score preserve two separate facts that must be "
            "connected to answer a question?"
        ),
        "source": {
            "label": "HotpotQA (EMNLP 2018)",
            "url": "https://aclanthology.org/D18-1259/",
        },
        "chunks": [
            {
                "text": (
                    "Mother Love Bone was a Seattle rock band whose frontman was "
                    "Andrew Wood."
                ),
                "is_evidence": True,
            },
            {
                "text": (
                    "Before Mother Love Bone, Andrew Wood was the singer of the band "
                    "Malfunkshun."
                ),
                "is_evidence": True,
            },
            {
                "text": (
                    "The Seattle music scene also produced bands including Pearl "
                    "Jam, Soundgarden, and Alice in Chains."
                ),
                "is_evidence": False,
            },
            {
                "text": (
                    "Mother Love Bone's album Apple was released after Wood's death "
                    "in 1990."
                ),
                "is_evidence": False,
            },
            {
                "text": (
                    "Loosegroove Records was founded in Seattle by Stone Gossard and "
                    "Regan Hagar."
                ),
                "is_evidence": False,
            },
        ],
    },
    {
        "id": "exact-grounding",
        "title": "Protect exact details",
        "question": (
            "Can trial accounts export customer data, and how long is audit history "
            "kept?"
        ),
        "research_question": (
            "Does compression retain evidence-bearing negation and exact numbers, "
            "not only the general topic?"
        ),
        "source": {
            "label": "Efficiency vs. Verifiability (CustomNLP4U 2026)",
            "url": "https://aclanthology.org/2026.customnlp4u-1.19/",
        },
        "chunks": [
            {
                "text": (
                    "Trial accounts must not export customer data. Export access is "
                    "available only after a paid plan is activated."
                ),
                "is_evidence": True,
            },
            {
                "text": "Audit history is retained for exactly 90 days.",
                "is_evidence": True,
            },
            {
                "text": (
                    "Paid accounts can export usage reports in CSV and JSON formats."
                ),
                "is_evidence": False,
            },
            {
                "text": (
                    "Administrators can change the workspace name and upload a logo."
                ),
                "is_evidence": False,
            },
            {
                "text": (
                    "The analytics dashboard refreshes summary charts every hour."
                ),
                "is_evidence": False,
            },
        ],
    },
]
