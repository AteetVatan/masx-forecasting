
class Prompts:    
    
    SYSTEM_ROLE_PROMPT = ""
    SYSTEM_ROLE_PROMPT_V1 = """
        You are an expert AI in geopolitical strategy and civilizational intelligence.
        Analyze, chunk, and tag the following doctrine text.
        """
    
    EMBEDDED_CHUNK_TAGGING_PROMPT = """Split text into ≤500-word doctrine chunks. Return:[{"section":...,"text":...,"meta":{"theme","region","use_case","strategic_category":["military_doctrine","geopolitical_strategy","national_security","diplomatic_posture","geostrategic_positioning"],"economic_category":["development_models","resource_strategies","trade_tariff_systems","economic_warfare"],"civilizational_category":["cultural_ethos","temporal_orientation","value_systems","historical_memory","civilizational_missions"],"usage_tags","influence_map":["influenced_works","modern_applications"]}}]"""
    
    EMBEDDED_CHUNK_TAGGING_PROMPT_MINI_v1 = """
    Classify the following text into semantically coherent doctrine chunks (≤500 words each).
    For each chunk, return:
    - section: title
    - text: chunk
    - meta: {
        theme, region, use_case,
        strategic_category: {military_doctrine, geopolitical_strategy, national_security, diplomatic_posture, geostrategic_positioning},
        economic_category: {development_models, resource_strategies, trade_tariff_systems, economic_warfare},
        civilizational_category: {cultural_ethos, temporal_orientation, value_systems, historical_memory, civilizational_missions},
        usage_tags,
        influence_map: {influenced_works, modern_applications}
    }
    Output only the JSON array.
    """
    
    
    
    
    EMBEDDED_CHUNK_TAGGING_PROMPT_MINI_v0 = """
        You are an AI trained in geopolitical doctrine analysis.

        Your job is to:
        - Split each text segment into 1 or more coherent strategic chunks (max 500 words each)
        - For each chunk, assign:
            - section: concise title (e.g., "Supply Chain Disruption", "Psychological Warfare")
            - theme: core topic (e.g., "cyberwarfare", "espionage", "soft power")
            - region: relevant geo-focus (e.g., "China", "Global", "South Asia")
            - use_case: geopolitical scenario simulation (e.g., "doctrine_selector", "psyops_engine", "risk_analyzer")

        Return a valid JSON array:
        [
        {
            "section": "...",
            "text": "...",
            "meta": {
            "theme": "...",
            "region": "...",
            "use_case": "..."
            }
        },
        ...
        ]

        Only output the JSON array, nothing else.
        """
        
    SYSTEM_ROLE_PROMPT_OLD = """
        You are an expert AI in geopolitical strategy and civilizational intelligence.
        Analyze, chunk, and tag the following doctrine text.
        """
    

    EMBEDDED_CHUNK_TAGGING_PROMPT_OLD = """
        You are an elite geopolitical analyst.
        Given a strategic text segment:
        1. Split it into coherent semantic chunks (around 500 words each).
        2. For each chunk, return:
        - section: A short title
        - text: The chunk content
        - meta: {
            theme,
            region,
            use_case: geopolitical scenario ,
            strategic_category: {
            military_doctrine: ,
            geopolitical_strategy: ,
            national_security: ,
            diplomatic_posture: ,
            geostrategic_positioning: 
            },
            economic_category: {
            development_models: ,
            resource_strategies: ,
            trade_tariff_systems: ,
            economic_warfare: 
            },
            civilizational_category: {
            cultural_ethos: ,
            temporal_orientation: ,
            value_systems: ,
            historical_memory: ,
            civilizational_missions: 
            },
            usage_tags: ,
            influence_map: {
            influenced_works: ,
            modern_applications: 
            }
        }
        Return a valid JSON array of these objects. Only return the JSON. Do not explain anything.
        """