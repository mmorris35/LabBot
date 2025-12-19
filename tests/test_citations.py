"""Test citation generator module."""

from labbot.citations import (
    GENERIC_MEDICAL,
    LAB_TEST_CITATIONS,
    MAYO_CLINIC,
    NIH_MEDLINEPLUS,
    CitationSource,
    get_all_citations_for_test,
    get_citation_for_test,
    is_test_known,
    normalize_test_name,
)


class TestNormalizeTestName:
    """Test test name normalization."""

    def test_lowercase_conversion(self) -> None:
        """Test conversion to lowercase."""
        assert normalize_test_name("HEMOGLOBIN") == "hemoglobin"
        assert normalize_test_name("HeMoGlObIn") == "hemoglobin"

    def test_whitespace_trimming(self) -> None:
        """Test removal of leading/trailing whitespace."""
        assert normalize_test_name("  Hemoglobin  ") == "hemoglobin"
        assert normalize_test_name("\tGlucose\n") == "glucose"

    def test_preserves_internal_spaces(self) -> None:
        """Test that internal spaces are preserved."""
        assert normalize_test_name("Red Blood Cell Count") == "red blood cell count"
        assert (
            normalize_test_name("Blood Urea Nitrogen")
            == "blood urea nitrogen"
        )

    def test_case_insensitive_normalization(self) -> None:
        """Test full case-insensitive normalization."""
        assert normalize_test_name("TOTAL CHOLESTEROL") == "total cholesterol"
        assert normalize_test_name("LDL Cholesterol") == "ldl cholesterol"


class TestCitationSource:
    """Test CitationSource class."""

    def test_citation_source_initialization(self) -> None:
        """Test CitationSource creation."""
        source = CitationSource(
            name="Test Source",
            url_pattern="https://example.com/{test_slug}",
            description="Test description",
        )
        assert source.name == "Test Source"
        assert source.url_pattern == "https://example.com/{test_slug}"
        assert source.description == "Test description"

    def test_get_url_with_slug(self) -> None:
        """Test URL generation with test slug."""
        source = CitationSource(
            name="Mayo Clinic",
            url_pattern="https://www.example.com/{test_slug}/info",
            description="Test",
        )
        url = source.get_url("hemoglobin")
        assert url == "https://www.example.com/hemoglobin/info"

    def test_get_url_with_multiple_placeholders(self) -> None:
        """Test URL generation preserves other content."""
        source = CitationSource(
            name="Test",
            url_pattern="https://example.com/tests/{test_slug}/page",
            description="Test",
        )
        url = source.get_url("glucose")
        assert url == "https://example.com/tests/glucose/page"

    def test_get_citation_format(self) -> None:
        """Test citation text format."""
        source = CitationSource(
            name="Test Source",
            url_pattern="https://example.com/{test_slug}",
            description="Test",
        )
        citation = source.get_citation("test_value")
        assert citation == "Test Source: https://example.com/test_value"

    def test_citation_includes_name_and_url(self) -> None:
        """Test citation includes both source name and URL."""
        citation = MAYO_CLINIC.get_citation("hemoglobin")
        assert "Mayo Clinic" in citation
        assert "https://" in citation
        assert "hemoglobin" in citation.lower()


class TestPredefinedSources:
    """Test predefined citation sources."""

    def test_mayo_clinic_source(self) -> None:
        """Test Mayo Clinic source configuration."""
        assert MAYO_CLINIC.name == "Mayo Clinic"
        assert "mayoclinic.org" in MAYO_CLINIC.url_pattern
        assert "{test_slug}" in MAYO_CLINIC.url_pattern

    def test_nih_medlineplus_source(self) -> None:
        """Test NIH MedlinePlus source configuration."""
        assert NIH_MEDLINEPLUS.name == "MedlinePlus (NIH)"
        assert "medlineplus.gov" in NIH_MEDLINEPLUS.url_pattern
        assert "{test_slug}" in NIH_MEDLINEPLUS.url_pattern

    def test_generic_medical_source(self) -> None:
        """Test generic medical source configuration."""
        assert GENERIC_MEDICAL.name == "Medical Reference"
        assert "nlm.nih.gov" in GENERIC_MEDICAL.url_pattern

    def test_all_sources_have_https(self) -> None:
        """Test all sources use HTTPS."""
        assert MAYO_CLINIC.url_pattern.startswith("https://")
        assert NIH_MEDLINEPLUS.url_pattern.startswith("https://")
        assert GENERIC_MEDICAL.url_pattern.startswith("https://")


class TestLabTestCitationsMapping:
    """Test lab test to citation mapping."""

    def test_common_blood_work_tests_mapped(self) -> None:
        """Test common blood test names are in mapping."""
        common_tests = [
            "hemoglobin",
            "glucose",
            "cholesterol",
            "sodium",
            "potassium",
        ]
        for test in common_tests:
            assert test in LAB_TEST_CITATIONS, f"{test} should be in mapping"

    def test_abbreviation_tests_mapped(self) -> None:
        """Test abbreviation test names are in mapping."""
        abbrev_tests = ["rbc", "wbc", "ast", "alt", "gfr", "tsh"]
        for test in abbrev_tests:
            assert test in LAB_TEST_CITATIONS, f"{test} should be in mapping"

    def test_each_mapping_has_sources(self) -> None:
        """Test each test has at least one citation source."""
        for test_name, sources in LAB_TEST_CITATIONS.items():
            assert isinstance(
                sources, list
            ), f"{test_name} should have list of sources"
            assert (
                len(sources) > 0
            ), f"{test_name} should have at least one source"
            for source in sources:
                assert isinstance(
                    source, CitationSource
                ), "Source should be CitationSource instance"

    def test_mapping_contains_major_panels(self) -> None:
        """Test that major lab panels are well represented."""
        # CBC tests
        cbc_tests = ["hemoglobin", "hematocrit", "rbc", "wbc", "platelets"]
        for test in cbc_tests:
            assert test in LAB_TEST_CITATIONS

        # Metabolic panel tests
        metabolic_tests = ["glucose", "sodium", "potassium", "creatinine"]
        for test in metabolic_tests:
            assert test in LAB_TEST_CITATIONS

        # Lipid panel tests
        lipid_tests = ["cholesterol", "ldl", "hdl", "triglycerides"]
        for test in lipid_tests:
            assert test in LAB_TEST_CITATIONS


class TestGetCitationForTest:
    """Test citation retrieval for specific tests."""

    def test_known_test_returns_citation(self) -> None:
        """Test known test returns proper citation."""
        citation = get_citation_for_test("Hemoglobin")
        assert ":" in citation
        assert "https://" in citation

    def test_hemoglobin_citation(self) -> None:
        """Test hemoglobin citation format."""
        citation = get_citation_for_test("Hemoglobin")
        assert "Mayo Clinic" in citation or "MedlinePlus" in citation
        assert "https://" in citation

    def test_case_insensitive_lookup(self) -> None:
        """Test citation lookup is case-insensitive."""
        citation_upper = get_citation_for_test("HEMOGLOBIN")
        citation_lower = get_citation_for_test("hemoglobin")
        citation_mixed = get_citation_for_test("HeMoGlObIn")
        assert citation_upper == citation_lower
        assert citation_lower == citation_mixed

    def test_whitespace_handling(self) -> None:
        """Test citation lookup with extra whitespace."""
        citation_normal = get_citation_for_test("Hemoglobin")
        citation_spaces = get_citation_for_test("  Hemoglobin  ")
        assert citation_normal == citation_spaces

    def test_multi_word_test_names(self) -> None:
        """Test citation lookup for multi-word test names."""
        test_names = [
            "Red Blood Cell Count",
            "Blood Glucose",
            "Total Cholesterol",
            "Low-density Lipoprotein",
        ]
        for test_name in test_names:
            citation = get_citation_for_test(test_name)
            assert ":" in citation
            assert "https://" in citation

    def test_unknown_test_returns_generic_citation(self) -> None:
        """Test unknown test returns generic medical reference."""
        citation = get_citation_for_test("UnknownTestXYZ123")
        assert "Medical Reference" in citation
        assert "nlm.nih.gov" in citation

    def test_unknown_test_still_valid_url(self) -> None:
        """Test generic citation for unknown test has valid URL."""
        citation = get_citation_for_test("FakeLab TestValue")
        assert "https://" in citation
        assert citation.startswith("Medical Reference:")

    def test_abbreviation_lookup(self) -> None:
        """Test citation lookup with abbreviations."""
        abbreviations = {
            "rbc": "Red blood cell",
            "wbc": "White blood cell",
            "ast": "AST",
            "alt": "ALT",
            "gfr": "GFR",
            "tsh": "TSH",
        }
        for abbrev, expected_word in abbreviations.items():
            citation = get_citation_for_test(abbrev)
            assert ":" in citation
            assert "https://" in citation

    def test_glucose_variations(self) -> None:
        """Test different glucose test name variations."""
        variations = [
            "Glucose",
            "Blood Glucose",
            "Fasting Glucose",
        ]
        for test_name in variations:
            citation = get_citation_for_test(test_name)
            assert "https://" in citation

    def test_cholesterol_variations(self) -> None:
        """Test different cholesterol test name variations."""
        test_names = [
            "Cholesterol",
            "Total Cholesterol",
            "LDL",
            "HDL",
            "Triglycerides",
        ]
        for test_name in test_names:
            citation = get_citation_for_test(test_name)
            assert ":" in citation
            assert "https://" in citation


class TestGetAllCitationsForTest:
    """Test retrieval of all available citations."""

    def test_known_test_returns_list(self) -> None:
        """Test known test returns list of citations."""
        citations = get_all_citations_for_test("Hemoglobin")
        assert isinstance(citations, list)
        assert len(citations) > 0

    def test_citations_are_strings(self) -> None:
        """Test all returned citations are strings."""
        citations = get_all_citations_for_test("Glucose")
        for citation in citations:
            assert isinstance(citation, str)
            assert ":" in citation
            assert "https://" in citation

    def test_multiple_sources_for_known_test(self) -> None:
        """Test that known tests have multiple source options."""
        citations = get_all_citations_for_test("Hemoglobin")
        # Should have at least Mayo Clinic and MedlinePlus
        assert len(citations) >= 2

    def test_unknown_test_returns_generic(self) -> None:
        """Test unknown test returns list with generic citation."""
        citations = get_all_citations_for_test("UnknownTest123")
        assert isinstance(citations, list)
        assert len(citations) == 1
        assert "Medical Reference" in citations[0]

    def test_all_citations_contain_urls(self) -> None:
        """Test all returned citations contain URLs."""
        citations = get_all_citations_for_test("Cholesterol")
        for citation in citations:
            assert "https://" in citation

    def test_case_insensitive_all_citations(self) -> None:
        """Test all citations lookup is case-insensitive."""
        citations_upper = get_all_citations_for_test("HEMOGLOBIN")
        citations_lower = get_all_citations_for_test("hemoglobin")
        assert citations_upper == citations_lower

    def test_different_sources_have_different_urls(self) -> None:
        """Test that multiple sources for same test have different URLs."""
        citations = get_all_citations_for_test("Hemoglobin")
        if len(citations) > 1:
            # Extract URLs from citations (format: "Source: URL")
            urls = [c.split(": ", 1)[1] for c in citations]
            # URLs should be different
            assert len(set(urls)) == len(urls)


class TestIsTestKnown:
    """Test test knowledge checking."""

    def test_known_test(self) -> None:
        """Test known tests return True."""
        known_tests = ["Hemoglobin", "Glucose", "Cholesterol"]
        for test_name in known_tests:
            assert is_test_known(test_name) is True

    def test_unknown_test(self) -> None:
        """Test unknown tests return False."""
        assert is_test_known("UnknownTestXYZ") is False
        assert is_test_known("FakeLab Value 123") is False

    def test_case_insensitive_check(self) -> None:
        """Test test knowledge is case-insensitive."""
        assert is_test_known("HEMOGLOBIN") is True
        assert is_test_known("hemoglobin") is True
        assert is_test_known("HeMoGlObIn") is True

    def test_whitespace_handling_in_check(self) -> None:
        """Test test knowledge with extra whitespace."""
        assert is_test_known("  Hemoglobin  ") is True
        assert is_test_known("\tGlucose\n") is True

    def test_multi_word_known_test(self) -> None:
        """Test multi-word known tests."""
        multi_word_tests = [
            "Red Blood Cell Count",
            "Blood Glucose",
            "Total Cholesterol",
        ]
        for test_name in multi_word_tests:
            assert is_test_known(test_name) is True

    def test_abbreviations_known(self) -> None:
        """Test abbreviations are recognized as known."""
        abbrevs = ["rbc", "wbc", "ast", "alt", "gfr", "tsh"]
        for abbrev in abbrevs:
            assert is_test_known(abbrev) is True


class TestIntegration:
    """Integration tests for citation generation."""

    def test_get_citation_and_verify_structure(self) -> None:
        """Test that retrieved citation has proper structure."""
        citation = get_citation_for_test("Hemoglobin")
        parts = citation.split(": ", 1)
        assert len(parts) == 2
        source_name, url = parts
        assert source_name in ["Mayo Clinic", "MedlinePlus (NIH)", "Medical Reference"]
        assert url.startswith("https://")

    def test_known_test_has_priority_source(self) -> None:
        """Test that first source in list is returned for known tests."""
        all_citations = get_all_citations_for_test("Hemoglobin")
        primary_citation = get_citation_for_test("Hemoglobin")
        # Primary should be the first one
        assert all_citations[0] == primary_citation

    def test_citation_for_each_major_lab_type(self) -> None:
        """Test citation generation for each major lab test type."""
        test_types = {
            "CBC": "Hemoglobin",
            "Metabolic Panel": "Glucose",
            "Lipid Panel": "Cholesterol",
            "Liver Function": "AST",
            "Kidney Function": "Creatinine",
            "Thyroid": "TSH",
        }
        for lab_type, test_name in test_types.items():
            citation = get_citation_for_test(test_name)
            assert ":" in citation, f"{lab_type} should have citation"
            assert "https://" in citation, f"{lab_type} citation should have URL"

    def test_batch_citation_retrieval(self) -> None:
        """Test citation retrieval for multiple tests at once."""
        test_names = [
            "Hemoglobin",
            "Glucose",
            "Cholesterol",
            "Sodium",
            "Potassium",
        ]
        citations = {
            test_name: get_citation_for_test(test_name)
            for test_name in test_names
        }
        assert len(citations) == len(test_names)
        for citation in citations.values():
            assert ":" in citation
            assert "https://" in citation

    def test_common_test_variations_all_work(self) -> None:
        """Test common name variations all retrieve citations."""
        # Different ways to write the same test
        test_variations = [
            ["Hemoglobin", "hemoglobin", "HEMOGLOBIN"],
            ["Glucose", "Blood Glucose", "Fasting Glucose"],
            ["Cholesterol", "Total Cholesterol", "TOTAL CHOLESTEROL"],
        ]
        for variations in test_variations:
            citations = [get_citation_for_test(v) for v in variations]
            # All variations should return citations with same source
            sources = [c.split(": ")[0] for c in citations]
            # At least first and second should be the same source
            assert sources[0] == sources[1]
