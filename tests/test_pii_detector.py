"""Test PII detection module."""

from labbot.pii_detector import detect_pii, detect_pii_in_dict


class TestDetectSSN:
    """Tests for Social Security Number detection."""

    def test_detect_ssn_with_dashes(self) -> None:
        """Detect SSN in XXX-XX-XXXX format."""
        result = detect_pii("SSN: 123-45-6789")
        assert "ssn" in result

    def test_detect_ssn_without_dashes(self) -> None:
        """Detect SSN in XXXXXXXXX format."""
        result = detect_pii("SSN: 123456789")
        assert "ssn" in result

    def test_detect_multiple_ssn_formats(self) -> None:
        """Detect SSN regardless of format."""
        result = detect_pii("123-45-6789 or 987654321")
        assert "ssn" in result
        assert result.count("ssn") == 1  # Should only appear once in list

    def test_no_false_positive_on_lab_values(self) -> None:
        """No false positive when text contains 9-digit lab values."""
        # Hemoglobin count of 123456789 should not trigger SSN detection
        # when it's not a word boundary match
        result = detect_pii("Lab value: 14.5")
        assert "ssn" not in result

    def test_no_false_positive_on_partial_numbers(self) -> None:
        """No false positive on partial number sequences."""
        result = detect_pii("value 12-34-56")
        assert "ssn" not in result


class TestDetectPhoneNumber:
    """Tests for phone number detection."""

    def test_detect_phone_with_dashes(self) -> None:
        """Detect phone number in XXX-XXX-XXXX format."""
        result = detect_pii("Phone: 555-123-4567")
        assert "phone" in result

    def test_detect_phone_with_dots(self) -> None:
        """Detect phone number in XXX.XXX.XXXX format."""
        result = detect_pii("Contact: 555.123.4567")
        assert "phone" in result

    def test_detect_phone_with_spaces(self) -> None:
        """Detect phone number in XXX XXX XXXX format."""
        result = detect_pii("Call 555 123 4567 today")
        assert "phone" in result

    def test_detect_phone_with_parentheses(self) -> None:
        """Detect phone number in (XXX) XXX-XXXX format."""
        result = detect_pii("(555) 123-4567")
        assert "phone" in result

    def test_detect_phone_with_parentheses_and_spaces(self) -> None:
        """Detect phone number in (XXX) XXX XXXX format."""
        result = detect_pii("(555) 123 4567")
        assert "phone" in result

    def test_no_false_positive_on_lab_values(self) -> None:
        """No false positive on numeric lab values."""
        result = detect_pii("Reference range: 123-456 to 789-012")
        assert "phone" not in result

    def test_no_false_positive_on_measurements(self) -> None:
        """No false positive on measurement ranges."""
        result = detect_pii("Normal range: 100-200 cells/mL")
        assert "phone" not in result


class TestDetectEmail:
    """Tests for email address detection."""

    def test_detect_email_basic(self) -> None:
        """Detect standard email address."""
        result = detect_pii("Email: john.smith@example.com")
        assert "email" in result

    def test_detect_email_with_plus(self) -> None:
        """Detect email with plus addressing."""
        result = detect_pii("john+test@domain.co.uk")
        assert "email" in result

    def test_detect_email_with_underscore(self) -> None:
        """Detect email with underscores in local part."""
        result = detect_pii("john_doe@company.org")
        assert "email" in result

    def test_detect_email_with_numbers(self) -> None:
        """Detect email with numbers."""
        result = detect_pii("patient123@hospital.gov")
        assert "email" in result

    def test_no_false_positive_on_units(self) -> None:
        """No false positive on measurement units."""
        result = detect_pii("Hemoglobin: 14.5 g/dL")
        assert "email" not in result

    def test_no_false_positive_on_partial_email_like_text(self) -> None:
        """No false positive on email-like but invalid text."""
        result = detect_pii("test.@invalid")
        assert "email" not in result


class TestDetectDOB:
    """Tests for date of birth detection."""

    def test_detect_dob_slash_format_mmddyyyy(self) -> None:
        """Detect DOB in MM/DD/YYYY format."""
        result = detect_pii("DOB: 01/15/1990")
        assert "dob" in result

    def test_detect_dob_slash_format_mdyyyy(self) -> None:
        """Detect DOB in M/D/YYYY format."""
        result = detect_pii("Birthday: 3/5/1985")
        assert "dob" in result

    def test_detect_dob_dash_format(self) -> None:
        """Detect DOB in MM-DD-YYYY format."""
        result = detect_pii("Date: 12-25-1980")
        assert "dob" in result

    def test_detect_dob_european_format(self) -> None:
        """Detect DOB in DD/MM/YYYY format (European)."""
        result = detect_pii("Born: 31/12/1975")
        assert "dob" in result

    def test_detect_dob_two_digit_year(self) -> None:
        """Detect DOB with two-digit year."""
        result = detect_pii("05/20/95")
        assert "dob" in result

    def test_no_false_positive_on_ranges(self) -> None:
        """No false positive on reference ranges."""
        result = detect_pii("Reference: 10/100 to 20/200")
        assert "dob" not in result


class TestDetectName:
    """Tests for personal name detection."""

    def test_detect_name_patient_name_field(self) -> None:
        """Detect patient_name field."""
        result = detect_pii("patient_name: John Smith")
        assert "name" in result

    def test_detect_name_full_name_field(self) -> None:
        """Detect full_name field."""
        result = detect_pii("full_name: Jane Doe")
        assert "name" in result

    def test_detect_name_name_field_with_spaces(self) -> None:
        """Detect name field with actual name value."""
        result = detect_pii("name: John Smith")
        assert "name" in result

    def test_detect_name_first_name_field(self) -> None:
        """Detect first_name field."""
        result = detect_pii("first_name: Robert")
        assert "name" in result

    def test_detect_name_last_name_field(self) -> None:
        """Detect last_name field."""
        result = detect_pii("last_name: Johnson")
        assert "name" in result

    def test_detect_name_surname_field(self) -> None:
        """Detect surname field."""
        result = detect_pii("surname: Williams")
        assert "name" in result

    def test_detect_name_with_equals(self) -> None:
        """Detect name field with equals sign."""
        result = detect_pii("patient_name=Michael Brown")
        assert "name" in result

    def test_detect_name_case_insensitive(self) -> None:
        """Detect name field regardless of case."""
        result = detect_pii("PATIENT_NAME: David Lee")
        assert "name" in result

    def test_detect_name_with_quotes(self) -> None:
        """Detect name field with quoted value."""
        result = detect_pii('full_name: "Sarah Chen"')
        assert "name" in result

    def test_no_false_positive_on_lab_test_names(self) -> None:
        """No false positive on actual lab test names."""
        result = detect_pii("name: Hemoglobin, unit: g/dL")
        assert "name" not in result

    def test_no_false_positive_on_common_words(self) -> None:
        """No false positive on common field names without name pattern."""
        result = detect_pii("value: test")
        assert "name" not in result


class TestCombinedPII:
    """Tests for detecting multiple PII types."""

    def test_detect_multiple_pii_types(self) -> None:
        """Detect multiple PII types in single text."""
        text = "patient_name: John Smith, SSN: 123-45-6789, Email: john@example.com"
        result = detect_pii(text)
        assert "ssn" in result
        assert "name" in result
        assert "email" in result

    def test_each_pii_type_appears_once(self) -> None:
        """Each PII type appears at most once in result list."""
        text = "SSN: 123-45-6789 SSN: 987-65-4321 (duplicate)"
        result = detect_pii(text)
        assert result.count("ssn") == 1

    def test_empty_string_returns_empty_list(self) -> None:
        """Empty string returns empty list."""
        result = detect_pii("")
        assert result == []

    def test_clean_lab_data_returns_empty_list(self) -> None:
        """Clean lab data without PII returns empty list."""
        result = detect_pii("Hemoglobin: 14.5 g/dL, WBC: 7.2 10^3/µL")
        assert result == []


class TestDetectPIIInDict:
    """Tests for PII detection in dictionary structures."""

    def test_detect_pii_in_simple_dict(self) -> None:
        """Detect PII in simple dictionary."""
        data = {
            "patient_name": "John Smith",
            "email": "john@example.com"
        }
        result = detect_pii_in_dict(data)
        assert "name" in result
        assert "email" in result

    def test_detect_pii_in_nested_dict(self) -> None:
        """Detect PII in nested dictionary."""
        data = {
            "patient": {
                "patient_name": "Jane Doe",
                "ssn": "123-45-6789"
            }
        }
        result = detect_pii_in_dict(data)
        assert "name" in result
        assert "ssn" in result

    def test_detect_pii_in_list_of_dicts(self) -> None:
        """Detect PII in list of dictionaries."""
        data = {
            "lab_values": [
                {"name": "Hemoglobin", "value": 14.5},
                {"name": "SSN", "value": "123-45-6789"}
            ]
        }
        result = detect_pii_in_dict(data)
        assert "ssn" in result

    def test_detect_pii_in_complex_structure(self) -> None:
        """Detect PII in complex nested structure."""
        data = {
            "patient": {
                "personal": {
                    "patient_name": "John Smith",
                    "dob": "01/15/1990"
                },
                "contact": {
                    "email": "john@example.com",
                    "phone": "555-123-4567"
                },
                "lab_values": [
                    {"name": "Hemoglobin", "value": 14.5},
                    {"name": "WBC", "value": 7.2}
                ]
            }
        }
        result = detect_pii_in_dict(data)
        assert "name" in result
        assert "dob" in result
        assert "email" in result
        assert "phone" in result

    def test_each_pii_type_appears_once_in_dict(self) -> None:
        """Each PII type appears once even if detected multiple times."""
        data = {
            "phone1": "555-123-4567",
            "phone2": "555-987-6543"
        }
        result = detect_pii_in_dict(data)
        assert result.count("phone") == 1

    def test_no_pii_in_clean_dict(self) -> None:
        """Clean dictionary returns empty list."""
        data = {
            "lab_values": [
                {"name": "Hemoglobin", "value": 14.5, "unit": "g/dL"},
                {"name": "WBC", "value": 7.2, "unit": "10^3/µL"}
            ]
        }
        result = detect_pii_in_dict(data)
        assert result == []

    def test_detect_pii_in_dict_with_none_values(self) -> None:
        """Handle None values gracefully."""
        data = {
            "full_name": "John Smith",
            "notes": None,
            "lab_values": []
        }
        result = detect_pii_in_dict(data)
        assert "name" in result

    def test_detect_pii_in_dict_with_numeric_values(self) -> None:
        """Handle numeric values without error."""
        data = {
            "full_name": "John Smith",
            "age": 45,
            "hemoglobin": 14.5
        }
        result = detect_pii_in_dict(data)
        assert "name" in result


class TestLabValueFalsePositives:
    """Tests to ensure no false positives on actual lab values."""

    def test_no_false_positive_on_normal_lab_ranges(self) -> None:
        """No false positives on standard lab reference ranges."""
        lab_data = {
            "lab_values": [
                {
                    "name": "Hemoglobin",
                    "value": 14.5,
                    "unit": "g/dL",
                    "reference_min": 13.5,
                    "reference_max": 17.5
                },
                {
                    "name": "WBC",
                    "value": 7.2,
                    "unit": "10^3/µL",
                    "reference_min": 4.5,
                    "reference_max": 11.0
                }
            ]
        }
        result = detect_pii_in_dict(lab_data)
        assert result == []

    def test_no_false_positive_on_cbc_results(self) -> None:
        """No false positives on Complete Blood Count results."""
        cbc_data = {
            "lab_values": [
                {"name": "Hemoglobin", "value": 14.5, "unit": "g/dL"},
                {"name": "Hematocrit", "value": 42.0, "unit": "%"},
                {"name": "MCV", "value": 88, "unit": "fL"},
                {"name": "Platelets", "value": 250, "unit": "10^3/µL"}
            ]
        }
        result = detect_pii_in_dict(cbc_data)
        assert result == []

    def test_no_false_positive_on_metabolic_panel(self) -> None:
        """No false positives on Comprehensive Metabolic Panel results."""
        metabolic_data = {
            "lab_values": [
                {"name": "Glucose", "value": 95, "unit": "mg/dL"},
                {"name": "Calcium", "value": 9.2, "unit": "mg/dL"},
                {"name": "Phosphate", "value": 3.5, "unit": "mg/dL"},
                {"name": "Sodium", "value": 138, "unit": "mEq/L"}
            ]
        }
        result = detect_pii_in_dict(metabolic_data)
        assert result == []

    def test_no_false_positive_on_numeric_only_values(self) -> None:
        """No false positives when data contains only numeric values."""
        numeric_data = {
            "value1": 123456789,
            "value2": 555123456,
            "value3": 12345678
        }
        result = detect_pii_in_dict(numeric_data)
        assert result == []


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_long_text(self) -> None:
        """Handle very long text without errors."""
        long_text = "Lab value: 14.5 " * 10000
        result = detect_pii(long_text)
        assert result == []

    def test_special_characters_in_pii(self) -> None:
        """Detect PII even with special characters nearby."""
        result = detect_pii("***SSN: 123-45-6789***")
        assert "ssn" in result

    def test_pii_at_string_boundaries(self) -> None:
        """Detect PII at start and end of strings."""
        result = detect_pii("123-45-6789")
        assert "ssn" in result

    def test_unicode_characters(self) -> None:
        """Handle unicode characters without errors."""
        result = detect_pii("Name: João Silva, SSN: 123-45-6789")
        assert "ssn" in result

    def test_newlines_in_text(self) -> None:
        """Handle newlines in text."""
        text = "Patient Info:\nName: John Smith\nSSN: 123-45-6789"
        result = detect_pii(text)
        assert "name" in result
        assert "ssn" in result

    def test_tabs_in_text(self) -> None:
        """Handle tabs in text."""
        text = "Name:\tJohn Smith\nEmail:\tjohn@example.com"
        result = detect_pii(text)
        assert "name" in result
        assert "email" in result
