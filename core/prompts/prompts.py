class Prompts:
    SYSTEM_ROLE_PROMPT = (
        "You are an expert AI in geopolitical strategy and civilizational intelligence. "
        "Analyze, chunk, and tag the following doctrine text."
    )

    CHUNK_AND_ENRICH_PROMPT = (
        "Split text into ≤500-word doctrine chunks. Return:"
        '[{"section":...,"text":...,"meta":{"theme","region","use_case",'
        '"strategic_category":["military_doctrine","geopolitical_strategy",'
        '"national_security","diplomatic_posture","geostrategic_positioning"],'
        '"economic_category":["development_models","resource_strategies",'
        '"trade_tariff_systems","economic_warfare"],'
        '"civilizational_category":["cultural_ethos","temporal_orientation",'
        '"value_systems","historical_memory","civilizational_missions"],'
        '"usage_tags","influence_map":["influenced_works","modern_applications"]}}]'
    )

    EMBEDDED_CHUNK_TAGGING_PROMPT = (
        "Classify the following text into semantically coherent doctrine chunks (≤500 words each).\n"
        "For each chunk, return:\n"
        "- section: title\n"
        "- text: chunk\n"
        "- meta: {theme, region, use_case,\n"
        "    strategic_category: {military_doctrine, geopolitical_strategy, national_security, diplomatic_posture, geostrategic_positioning},\n"
        "    economic_category: {development_models, resource_strategies, trade_tariff_systems, economic_warfare},\n"
        "    civilizational_category: {cultural_ethos, temporal_orientation, value_systems, historical_memory, civilizational_missions},\n"
        "    usage_tags,\n"
        "    influence_map: {influenced_works, modern_applications}\n"
        "}\n"
        "Output only the JSON array."
    )
