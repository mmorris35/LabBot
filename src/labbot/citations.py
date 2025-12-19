"""Medical citation generator for lab results.

Provides authoritative sources for common lab tests with support for
Mayo Clinic, NIH, MedlinePlus, and fallback to generic medical references.
"""

import logging

logger = logging.getLogger(__name__)


class CitationSource:
    """Represents a medical citation source with URL pattern."""

    def __init__(self, name: str, url_pattern: str, description: str) -> None:
        """Initialize citation source.

        Args:
            name: Name of the source (e.g., "Mayo Clinic")
            url_pattern: URL pattern with {test_slug} placeholder
            description: Human-readable description of the source
        """
        self.name = name
        self.url_pattern = url_pattern
        self.description = description

    def get_url(self, test_slug: str) -> str:
        """Generate URL for a specific test.

        Args:
            test_slug: Slug-ified test name (e.g., "hemoglobin")

        Returns:
            Complete URL for the test resource.
        """
        return self.url_pattern.format(test_slug=test_slug)

    def get_citation(self, test_slug: str) -> str:
        """Generate citation text with URL.

        Args:
            test_slug: Slug-ified test name

        Returns:
            Citation text with source name and URL.
        """
        url = self.get_url(test_slug)
        return f"{self.name}: {url}"


# Define authoritative citation sources
MAYO_CLINIC = CitationSource(
    name="Mayo Clinic",
    url_pattern="https://www.mayoclinic.org/tests-procedures/{test_slug}/about/pac-20384692",
    description="Mayo Clinic medical information",
)

NIH_MEDLINEPLUS = CitationSource(
    name="MedlinePlus (NIH)",
    url_pattern="https://medlineplus.gov/lab-tests/{test_slug}/",
    description="NIH National Library of Medicine",
)

MEDLINEPLUS = CitationSource(
    name="MedlinePlus",
    url_pattern="https://medlineplus.gov/ency/article/{test_slug}.htm",
    description="National Library of Medicine comprehensive resource",
)

GENERIC_MEDICAL = CitationSource(
    name="Medical Reference",
    url_pattern="https://www.nlm.nih.gov/medlineplus/",
    description="National Library of Medicine general resource",
)


# Mapping of lab test names to citation sources
# Keys are normalized lowercase test names
# Values are preferred citation sources (in order of preference)
LAB_TEST_CITATIONS: dict[str, list[CitationSource]] = {
    # Complete Blood Count (CBC)
    "hemoglobin": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "hematocrit": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "red blood cell count": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "rbc": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "white blood cell count": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "wbc": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "platelet count": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "platelets": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "mean corpuscular volume": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "mcv": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    # Metabolic Panel
    "glucose": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "blood glucose": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "fasting glucose": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "sodium": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "potassium": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "chloride": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "co2": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "carbon dioxide": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "bicarbonate": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "bun": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "blood urea nitrogen": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "creatinine": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "calcium": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "albumin": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "total protein": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    # Lipid Panel
    "cholesterol": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "total cholesterol": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "ldl": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "low-density lipoprotein": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "hdl": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "high-density lipoprotein": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "triglycerides": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    # Liver Function Tests
    "ast": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "aspartate aminotransferase": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "alt": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "alanine aminotransferase": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "alkaline phosphatase": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "alp": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "bilirubin": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "total bilirubin": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    # Kidney Function Tests
    "bun/creatinine ratio": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "gfr": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "glomerular filtration rate": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "uric acid": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    # Thyroid Function
    "tsh": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "thyroid stimulating hormone": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "t3": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "t4": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "thyroxine": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    # Vitamin Levels
    "vitamin b12": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "b12": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "cobalamin": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "folate": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "folic acid": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "vitamin d": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "d25": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "25-hydroxyvitamin d": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    # Cardiac Markers
    "troponin": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "high-sensitivity troponin": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "creatine kinase": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "ck": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "ck-mb": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "myoglobin": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "bnp": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "b-type natriuretic peptide": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    # Hormone Tests
    "cortisol": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "testosterone": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "estrogen": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "progesterone": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "psa": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "prostate specific antigen": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    # Inflammatory Markers
    "crp": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "c-reactive protein": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "esr": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "erythrocyte sedimentation rate": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    # Coagulation Tests
    "pt": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "prothrombin time": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "inr": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "international normalized ratio": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "ptt": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "partial thromboplastin time": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "aptt": [MAYO_CLINIC, NIH_MEDLINEPLUS],
    "activated partial thromboplastin time": [MAYO_CLINIC, NIH_MEDLINEPLUS],
}


def normalize_test_name(test_name: str) -> str:
    """Normalize test name for lookup.

    Converts to lowercase, removes extra whitespace, and standardizes formatting.

    Args:
        test_name: Raw test name from lab results

    Returns:
        Normalized test name for dictionary lookup
    """
    return test_name.lower().strip()


def get_citation_for_test(test_name: str) -> str:
    """Get authoritative citation for a lab test.

    Searches for the test in the lab test citations mapping and returns
    the citation from the preferred source. Falls back to generic medical
    reference if test is not found.

    Args:
        test_name: Name of the lab test (e.g., "Hemoglobin", "Blood Glucose")

    Returns:
        Citation string with source name and URL.

    Example:
        >>> citation = get_citation_for_test("Hemoglobin")
        >>> "Mayo Clinic" in citation
        True
        >>> "https://" in citation
        True
    """
    normalized_name: str = normalize_test_name(test_name)

    # Look up test in citation database
    if normalized_name in LAB_TEST_CITATIONS:
        sources: list[CitationSource] = LAB_TEST_CITATIONS[normalized_name]
        # Return citation from the first (preferred) source
        preferred_source: CitationSource = sources[0]
        citation_text: str = preferred_source.get_citation(normalized_name)
        logger.debug(f"Found citation for test '{test_name}': {citation_text}")
        return citation_text
    else:
        # Return generic medical reference for unknown tests
        generic_citation: str = (
            f"{GENERIC_MEDICAL.name}: "
            f"{GENERIC_MEDICAL.url_pattern}"
        )
        logger.debug(
            f"No specific citation found for test '{test_name}'. "
            "Using generic medical reference."
        )
        return generic_citation


def get_all_citations_for_test(test_name: str) -> list[str]:
    """Get all available citations for a lab test.

    Returns citations from all available sources for the test, useful for
    providing users with multiple reference options.

    Args:
        test_name: Name of the lab test

    Returns:
        List of citation strings from all available sources,
        or list with single generic reference if test is unknown.

    Example:
        >>> citations = get_all_citations_for_test("Hemoglobin")
        >>> len(citations) >= 1
        True
    """
    normalized_name: str = normalize_test_name(test_name)

    if normalized_name in LAB_TEST_CITATIONS:
        sources: list[CitationSource] = LAB_TEST_CITATIONS[normalized_name]
        citations: list[str] = [
            source.get_citation(normalized_name) for source in sources
        ]
        return citations
    else:
        # Return single generic reference for unknown tests
        citation: str = (
            f"{GENERIC_MEDICAL.name}: "
            f"{GENERIC_MEDICAL.url_pattern}"
        )
        return [citation]


def is_test_known(test_name: str) -> bool:
    """Check if a lab test has a specific citation mapping.

    Args:
        test_name: Name of the lab test

    Returns:
        True if test has specific citation(s), False if only generic reference available
    """
    normalized_name: str = normalize_test_name(test_name)
    return normalized_name in LAB_TEST_CITATIONS
