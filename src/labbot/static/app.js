/**
 * LabBot Frontend Application
 * Handles user interactions for lab result interpretation
 */

/**
 * Get the base path for API calls (handles API Gateway stage prefixes like /Prod)
 */
function getBasePath() {
    const path = window.location.pathname;
    // Remove trailing slash and get directory path
    const dir = path.endsWith('/') ? path.slice(0, -1) : path.substring(0, path.lastIndexOf('/'));
    console.log('[LabBot] window.location.href:', window.location.href);
    console.log('[LabBot] window.location.pathname:', path);
    console.log('[LabBot] getBasePath() returning:', dir || '(empty)');
    return dir || '';
}

// Sample CBC (Complete Blood Count) data
const SAMPLE_CBC_DATA = {
    lab_values: [
        {
            name: "Hemoglobin",
            value: 14.5,
            unit: "g/dL",
            reference_min: 13.5,
            reference_max: 17.5
        },
        {
            name: "Hematocrit",
            value: 42.1,
            unit: "%",
            reference_min: 40.0,
            reference_max: 50.0
        },
        {
            name: "Red Blood Cells",
            value: 4.8,
            unit: "million/mcL",
            reference_min: 4.5,
            reference_max: 5.5
        },
        {
            name: "White Blood Cells",
            value: 7.2,
            unit: "thousand/mcL",
            reference_min: 4.5,
            reference_max: 11.0
        },
        {
            name: "Platelets",
            value: 250,
            unit: "thousand/mcL",
            reference_min: 150,
            reference_max: 400
        }
    ]
};

/**
 * Initialize the application
 */
function initialize() {
    const loadSampleButton = document.getElementById('loadSampleButton');
    const interpretButton = document.getElementById('interpretButton');
    const jsonInput = document.getElementById('jsonInput');

    loadSampleButton.addEventListener('click', () => {
        loadSampleData();
    });

    interpretButton.addEventListener('click', () => {
        interpretResults();
    });

    // Allow Enter key in textarea for form submission
    jsonInput.addEventListener('keydown', (event) => {
        if (event.ctrlKey && event.key === 'Enter') {
            interpretResults();
        }
    });
}

/**
 * Load sample CBC data into the textarea
 */
function loadSampleData() {
    const jsonInput = document.getElementById('jsonInput');
    jsonInput.value = JSON.stringify(SAMPLE_CBC_DATA, null, 2);
    jsonInput.focus();
}

/**
 * Detect personally identifiable information patterns in text
 *
 * @param {string} text - The text to scan for PII
 * @returns {Array<string>} List of detected PII types
 */
function detectPiiPatterns(text) {
    const detectedTypes = [];

    // SSN pattern: XXX-XX-XXXX or 9 consecutive digits
    if (/\b\d{3}-\d{2}-\d{4}\b/.test(text) || /\b\d{9}\b/.test(text)) {
        detectedTypes.push('ssn');
    }

    // Phone patterns: XXX-XXX-XXXX, XXX.XXX.XXXX, XXX XXX XXXX, (XXX) XXX-XXXX
    if (/\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b/.test(text) || /\(\d{3}\)\s*\d{3}-\d{4}/.test(text)) {
        detectedTypes.push('phone');
    }

    // Email pattern: standard RFC pattern with plus addressing and underscores
    if (/\b[A-Za-z0-9._+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b/.test(text)) {
        detectedTypes.push('email');
    }

    // Date of birth patterns: MM/DD/YYYY, M/D/YYYY, MM-DD-YYYY, DD/MM/YYYY
    if (/\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b/.test(text)) {
        detectedTypes.push('dob');
    }

    // Personal name field names: patient_name, full_name, first_name, last_name, surname
    if (/\b(?:patient_name|full_name|first_name|last_name|surname)\b/i.test(text)) {
        detectedTypes.push('name');
    }

    return [...new Set(detectedTypes)];
}

/**
 * Check lab data for PII and return detected types
 *
 * @param {Object} labData - The lab data object to scan
 * @returns {Array<string>} List of detected PII types
 */
function checkForPiiInData(labData) {
    const detectedPii = [];
    const jsonString = JSON.stringify(labData).toLowerCase();

    // Get all detected PII patterns
    const patterns = detectPiiPatterns(jsonString);
    detectedPii.push(...patterns);

    // Check dictionary keys for name field patterns
    function checkKeys(obj) {
        if (typeof obj !== 'object' || obj === null) return;
        for (const key in obj) {
            if (/\b(?:patient_name|full_name|first_name|last_name|surname)\b/i.test(key)) {
                if (!detectedPii.includes('name')) {
                    detectedPii.push('name');
                }
            }
            if (typeof obj[key] === 'object') {
                checkKeys(obj[key]);
            }
        }
    }

    checkKeys(labData);

    return [...new Set(detectedPii)];
}

/**
 * Interpret lab results by sending to API
 */
async function interpretResults() {
    const jsonInput = document.getElementById('jsonInput');
    const resultsSection = document.getElementById('resultsSection');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorMessage = document.getElementById('errorMessage');
    const resultsContainer = document.getElementById('resultsContainer');
    const resultDisclaimer = document.getElementById('resultDisclaimer');
    const summarySection = document.getElementById('summarySection');

    // Hide previous results
    resultsSection.style.display = 'none';
    errorMessage.style.display = 'none';

    // Validate input
    let labData;
    try {
        const inputText = jsonInput.value.trim();
        if (!inputText) {
            showError('Please enter lab results JSON');
            return;
        }
        labData = JSON.parse(inputText);
    } catch (error) {
        showError('Invalid JSON: ' + error.message);
        return;
    }

    // Client-side PII detection warning
    const detectedPii = checkForPiiInData(labData);
    if (detectedPii.length > 0) {
        const piiWarning =
            'WARNING: Personal information detected in your data:\n\n' +
            '- ' + detectedPii.join('\n- ') + '\n\n' +
            'Your data will NOT be sent to the AI service due to privacy protections.\n\n' +
            'Please remove any personal identifiers (names, phone numbers, emails, dates of birth, SSNs) ' +
            'and try again.\n\n' +
            'Example of safe data: {"lab_values": [{"name": "Hemoglobin", "value": 14.5, "unit": "g/dL"}]}';

        if (!confirm(piiWarning + '\n\nClick OK to acknowledge and remove the information, or Cancel to edit your data.')) {
            return;
        }

        showError(
            'Personal information detected in your data. ' +
            'Please remove any names, phone numbers, emails, or other personal identifiers. ' +
            'Detected: ' + detectedPii.join(', ')
        );
        return;
    }

    // Show results section and loading spinner
    resultsSection.style.display = 'block';
    loadingSpinner.style.display = 'block';
    resultsContainer.innerHTML = '';

    try {
        const apiUrl = getBasePath() + '/api/interpret';
        console.log('[LabBot] Calling API:', apiUrl);
        console.log('[LabBot] Request body:', JSON.stringify(labData));

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(labData)
        });

        console.log('[LabBot] Response status:', response.status);
        console.log('[LabBot] Response ok:', response.ok);

        if (!response.ok) {
            const errorText = await response.text();
            console.log('[LabBot] Error response body:', errorText);
            let errorData;
            try {
                errorData = JSON.parse(errorText);
            } catch (e) {
                errorData = { detail: errorText };
            }
            if (response.status === 400 && errorData.error === 'PII detected') {
                showError(
                    'Personal information detected in your data. ' +
                    'Please remove any names, phone numbers, emails, or other personal identifiers. ' +
                    'Detected: ' + errorData.types.join(', ')
                );
            } else if (response.status === 422) {
                showError('Invalid lab results format: ' + JSON.stringify(errorData.detail));
            } else if (response.status === 503) {
                showError('Service temporarily unavailable. Please try again later.');
            } else {
                showError('Error: ' + (errorData.detail || 'Unknown error'));
            }
            return;
        }

        const interpretationResponse = await response.json();
        console.log('[LabBot] Success! Response:', interpretationResponse);
        displayResults(interpretationResponse);

    } catch (error) {
        console.error('[LabBot] Network/JS error:', error);
        showError('Network error: ' + error.message);
    } finally {
        loadingSpinner.style.display = 'none';
    }
}

/**
 * Display interpretation results
 */
function displayResults(data) {
    const resultsContainer = document.getElementById('resultsContainer');
    const resultDisclaimer = document.getElementById('resultDisclaimer');
    const summarySection = document.getElementById('summarySection');
    const summaryText = document.getElementById('summaryText');

    // Clear previous results
    resultsContainer.innerHTML = '';

    // Display individual results
    if (data.results && Array.isArray(data.results)) {
        data.results.forEach((result) => {
            const card = createResultCard(result);
            resultsContainer.appendChild(card);
        });
    }

    // Display disclaimer if present
    if (data.disclaimer) {
        resultDisclaimer.innerHTML = '<strong>Disclaimer:</strong> ' + sanitizeHtml(data.disclaimer);
        resultDisclaimer.style.display = 'block';
    }

    // Display summary if present
    if (data.summary) {
        summaryText.textContent = data.summary;
        summarySection.style.display = 'block';
    } else {
        summarySection.style.display = 'none';
    }
}

/**
 * Create a result card element for a single lab value
 */
function createResultCard(result) {
    const card = document.createElement('div');
    card.className = 'result-card ' + (result.severity || 'normal');

    const header = document.createElement('div');
    header.className = 'result-header';

    const nameElement = document.createElement('div');
    nameElement.className = 'result-name';
    nameElement.textContent = result.name;

    const badgeElement = document.createElement('span');
    badgeElement.className = 'severity-badge ' + (result.severity || 'normal');
    badgeElement.textContent = (result.severity || 'normal').toUpperCase();

    header.appendChild(nameElement);
    header.appendChild(badgeElement);
    card.appendChild(header);

    // Value and unit
    const valueElement = document.createElement('div');
    valueElement.className = 'result-value';
    valueElement.innerHTML =
        '<strong>' + result.value + ' <span class="result-unit">' +
        sanitizeHtml(result.unit) + '</span></strong>';
    card.appendChild(valueElement);

    // Explanation
    const explanationElement = document.createElement('div');
    explanationElement.className = 'result-explanation';
    explanationElement.textContent = result.explanation;
    card.appendChild(explanationElement);

    // Citation if available
    if (result.citation) {
        const citationElement = document.createElement('div');
        citationElement.className = 'result-citation';

        // Check if citation is a URL
        if (result.citation.startsWith('http')) {
            citationElement.innerHTML =
                'Source: <a href="' + sanitizeHtml(result.citation) +
                '" target="_blank" rel="noopener noreferrer">Learn more</a>';
        } else {
            citationElement.textContent = 'Source: ' + sanitizeHtml(result.citation);
        }
        card.appendChild(citationElement);
    }

    return card;
}

/**
 * Show error message to user
 */
function showError(message) {
    const resultsSection = document.getElementById('resultsSection');
    const errorMessage = document.getElementById('errorMessage');
    const loadingSpinner = document.getElementById('loadingSpinner');

    resultsSection.style.display = 'block';
    loadingSpinner.style.display = 'none';
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

/**
 * Simple HTML sanitization to prevent XSS
 * Removes dangerous tags and attributes
 */
function sanitizeHtml(text) {
    if (!text) return '';

    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}
