"""Comprehensive XBRL concept and keyword mappings — re-export hub.

Split into per-statement files for maintainability:
  concept_maps_is.py — Income statement concepts
  concept_maps_bs.py — Balance sheet concepts
  concept_maps_cf.py — Cash flow concepts (operating)
  concept_maps_cf_inv.py — Cash flow concepts (investing/financing) + subtotals
  concept_maps_kw_is.py — IS keyword fallbacks
  concept_maps_kw_bs.py — BS keyword fallbacks
  concept_maps_kw_cf.py — CF keyword fallbacks
"""

from lib.data.concept_maps_is import IS_CONCEPTS
from lib.data.concept_maps_bs import BS_CONCEPTS
from lib.data.concept_maps_cf import CF_CONCEPTS_OPERATING
from lib.data.concept_maps_cf_inv import (
    CF_CONCEPTS_INVESTING_FINANCING,
    CF_SUBTOTAL_CONCEPTS,
)
from lib.data.concept_maps_kw_is import IS_KEYWORDS
from lib.data.concept_maps_kw_bs import BS_KEYWORDS
from lib.data.concept_maps_kw_cf import CF_KEYWORDS

# Merge CF concept dicts into single CF_CONCEPTS for backward compatibility
CF_CONCEPTS = {**CF_CONCEPTS_OPERATING, **CF_CONCEPTS_INVESTING_FINANCING}

__all__ = [
    "IS_CONCEPTS", "BS_CONCEPTS", "CF_CONCEPTS",
    "CF_SUBTOTAL_CONCEPTS",
    "IS_KEYWORDS", "BS_KEYWORDS", "CF_KEYWORDS",
]
