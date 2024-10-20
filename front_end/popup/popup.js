// Global variables and function definitions
const allSemesters = [
    "2024-Spring", "2024-Fall",
    "2025-Spring", "2025-Fall",
    "2026-Spring", "2026-Fall",
    "2027-Spring", "2027-Fall",
    "2028-Spring", "2028-Fall",
    "2029-Spring"
];

// Load SheetJS library
const script = document.createElement('script');
script.src = "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.17.0/xlsx.full.min.js";
document.head.appendChild(script);

function convertSemesterToNumber(semester) {
    const [year, term] = semester.split('-');
    const termNumber = (term === "Spring") ? 1 : 2;
    return parseInt(year) * 2 + (termNumber - 1);
}

function fetchHTML() {
    console.log("fetchHTML function called");

    // Retrieve the entire HTML content
    const htmlContent = document.documentElement.outerHTML;
    console.log(htmlContent);

    // Parse the HTML structure to extract desired course names
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlContent, "text/html");

    // Select rows with 'takenCourse' and 'takenCourse ip' classes
    const takenCourses = doc.querySelectorAll('tr.takenCourse, tr.takenCourse.ip');

    // Store course names in a Set to remove duplicates
    let courseNamesSet = new Set();

    // Iterate through each row and extract course names
    takenCourses.forEach((row) => {
        const courseTd = row.querySelector('td.course');
        if (courseTd) {
            // Remove spaces and add the course name
            const courseName = courseTd.textContent.trim().replace(/\s+/g, '');
            courseNamesSet.add(courseName);
        }
    });

    // Convert the Set to an array and log it to the console
    const courseNames = Array.from(courseNamesSet);
    console.log(courseNames);

    // Send the course name data along with HTML content via chrome runtime
    chrome.runtime.sendMessage({ html: htmlContent, courses: courseNames });
}

function showTermSetupView(startSemester, endSemester) {
    console.log("showTermSetupView called with:", startSemester, endSemester);

    const questionnaireView = document.getElementById('questionnaire-view');
    const termSetupView = document.getElementById('term-setup-view');
    const termContainer = document.getElementById('term-container');

    questionnaireView.classList.add('hidden');
    termSetupView.classList.remove('hidden');

    const startNum = convertSemesterToNumber(startSemester);
    const endNum = convertSemesterToNumber(endSemester);

    console.log("Start number:", startNum, "End number:", endNum);

    termContainer.innerHTML = '';

    let semestersAdded = 0;

    allSemesters.forEach(semester => {
        const semesterNum = convertSemesterToNumber(semester);
        console.log("Processing semester:", semester, "Number:", semesterNum);

        if (semesterNum >= startNum && semesterNum <= endNum) {
            const termDiv = document.createElement('div');
            termDiv.className = 'input-group';

            const label = document.createElement('label');
            label.textContent = `Credits for ${semester.replace('-', ' ')}:`;

            const select = document.createElement('select');
            select.name = `credits-${semester}`;
            select.id = `credits-${semester}`;

            for (let i = 12; i <= 21; i++) {
                const option = document.createElement('option');
                option.value = i;
                option.textContent = i;
                if (i === 18) {
                    option.selected = true;
                }
                select.appendChild(option);
            }

            termDiv.appendChild(label);
            termDiv.appendChild(select);
            termContainer.appendChild(termDiv);

            semestersAdded++;
        }
    });

    console.log("Semesters added:", semestersAdded);

    if (semestersAdded === 0) {
        const noOptionMessage = document.createElement('p');
        noOptionMessage.textContent = 'No available terms to select credits.';
        noOptionMessage.style.color = '#fff';
        termContainer.appendChild(noOptionMessage);
    } else {
        setTimeout(() => {
            termContainer.scrollTop = 0;
        }, 0);
    }
}
    document.querySelector('.close-btn').addEventListener('click', () => {
        document.body.style.visibility = 'hidden';
        document.body.style.opacity = 0;
        document.body.style.transition = 'visibility 0s 0.3s, opacity 0.3s linear';

        setTimeout(() => {
            document.body.style.display = 'none';
        }, 300); 
    });


document.addEventListener('DOMContentLoaded', () => {
    const agreeBtn = document.getElementById('agreeBtn');
    const goalMajorSelect = document.getElementById('goal-major');
    const tagInput = document.getElementById('electives');
    const tagContainer = tagInput.parentNode;
    const startSemesterSelect = document.getElementById('start-semester');
    const graduationGroup = document.getElementById('graduation-group');
    const endSemesterSelect = document.getElementById('end-semester');
    const nextButton = document.getElementById('submitPreferences');
    let extractedCourses = [];
    let selectedMajor = ""; 

    chrome.runtime.onMessage.addListener((request) => {
        if (request.courses) {
            extractedCourses = request.courses;
            console.log("Extracted courses:", extractedCourses);
        }
    });

    goalMajorSelect.addEventListener('change', () => {
        selectedMajor = goalMajorSelect.value;

        if (selectedMajor) {
            agreeBtn.disabled = false; 
            agreeBtn.classList.add('active'); 
        } else {
            agreeBtn.disabled = true; 
            agreeBtn.classList.remove('active'); 
        }
    });

    agreeBtn.addEventListener('click', () => {
        // Goal Major 선택 여부 확인
        if (!selectedMajor) {
            alert("Please select your Goal Major.");
            return; // If you don't select the major, the function will stop here.
        }

        console.log("Selected Goal Major:", selectedMajor);


        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            chrome.scripting.executeScript({
                target: { tabId: tabs[0].id },
                func: fetchHTML
            }, () => {
                if (chrome.runtime.lastError) {
                    console.error("Error executing script:", chrome.runtime.lastError);
                }
            });
        });

        const initialView = document.getElementById('initial-view');
        const questionnaireView = document.getElementById('questionnaire-view');

        initialView.classList.add('hidden');
        questionnaireView.classList.remove('hidden');
    });

    // tag input keypress event
    tagInput.addEventListener('keypress', function (event) {
        if (event.key === ' ' || event.key === 'Enter') {
            event.preventDefault();
            const value = tagInput.value.trim();
            if (value) {
                addTag(value);
                tagInput.value = '';
            }
        }
    });

    function addTag(text) {
        const tag = document.createElement('span');
        tag.className = 'tag';
        tag.textContent = text;

        const closeBtn = document.createElement('span');
        closeBtn.className = 'close';
        closeBtn.innerHTML = '&times;';
        closeBtn.onclick = function () {
            tag.remove();
        };

        tag.appendChild(closeBtn);
        tagContainer.insertBefore(tag, tagInput);
    }

    // check button state function
    function checkButtonState() {
        nextButton.disabled = !(startSemesterSelect.value && endSemesterSelect.value);
    }

    // initial button state check
    checkButtonState();

    startSemesterSelect.addEventListener('change', function () {
        const startSemester = this.value;
        const startSemesterNumber = convertSemesterToNumber(startSemester);

        endSemesterSelect.innerHTML = '';

        if (startSemester) {
            graduationGroup.classList.remove('hidden');

            const maxSemesterNumber = startSemesterNumber + 9;
            allSemesters.forEach(semester => {
                const semesterNumber = convertSemesterToNumber(semester);
                if (semesterNumber >= startSemesterNumber && semesterNumber <= maxSemesterNumber) {
                    const option = document.createElement('option');
                    option.value = semester;
                    option.textContent = semester.replace('-', ' ');
                    endSemesterSelect.appendChild(option);
                }
            });

            if (endSemesterSelect.options.length === 0) {
                const noOption = document.createElement('option');
                noOption.textContent = 'No available graduation semesters';
                noOption.disabled = true;
                endSemesterSelect.appendChild(noOption);
            }
        } else {
            graduationGroup.classList.add('hidden');
        }

        checkButtonState();
    });

    endSemesterSelect.addEventListener('change', checkButtonState);

    // "Next" click event
    nextButton.addEventListener('click', () => {
        const electives = Array.from(document.querySelectorAll('.tag')).map(tag => tag.textContent.trim());
        const startSemester = startSemesterSelect.value;
        const endSemester = endSemesterSelect.value;

        if (startSemester && endSemester) {
            showTermSetupView(startSemester, endSemester);
        }
    });

    // Submit button click event
    const submitButton = document.getElementById('finalizeSchedule');
    submitButton.addEventListener('click', function() {
        const selectedCredits = {};
        document.querySelectorAll('#term-container select').forEach(select => {
            selectedCredits[select.name.replace('credits-', '')] = select.value;
        });
    
        const finalData = {
            goalMajor: selectedMajor,
            takenCourses: extractedCourses,
            startSemester: startSemesterSelect.value,
            endSemester: endSemesterSelect.value,
            selectedCredits: selectedCredits,
            userPreferences: Array.from(document.querySelectorAll('.tag')).map(tag => tag.textContent.trim())
        };
    
        console.log('Final Data:', JSON.stringify(finalData, null, 2));
    
        const analyzingPrompt = document.createElement('div');
        analyzingPrompt.id = 'analyzing-prompt';
        analyzingPrompt.style.position = 'fixed';
        analyzingPrompt.style.top = '50%';
        analyzingPrompt.style.left = '50%';
        analyzingPrompt.style.transform = 'translate(-50%, -50%)';
        analyzingPrompt.style.padding = '20px';
        analyzingPrompt.style.backgroundColor = '#000';
        analyzingPrompt.style.color = '#fff';
        analyzingPrompt.style.borderRadius = '8px';
        analyzingPrompt.style.boxShadow = '0 0 15px rgba(0,0,0,0.5)';
        analyzingPrompt.style.fontSize = '18px';
        analyzingPrompt.style.textAlign = 'center';
        analyzingPrompt.textContent = 'Analyzing...';
    
        document.body.appendChild(analyzingPrompt);
    
        // Send data to the EC2 server
        const ec2Url = 'http://127.0.0.1:5000'; // actual URL
        fetch(ec2Url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(finalData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            // get the json from the response
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            alert('Data successfully received from EC2');
    
            try {
                // json to excel
                const ws = XLSX.utils.json_to_sheet(data);
                const wb = XLSX.utils.book_new();
                XLSX.utils.book_append_sheet(wb, ws, "Results");
    
                const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
                const blob = new Blob([wbout], { type: 'application/octet-stream' });
    
                // excel download
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'result.xlsx'; // filename
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            } catch (excelError) {
                console.error('Error converting to Excel:', excelError);
                alert('Failed to convert data to Excel format. Please check the response data.');
            }
    
        })
        .catch(error => {
            console.error('Error sending data to EC2:', error);
            alert('Failed to send data to EC2');
        })
        .finally(() => {
            if (analyzingPrompt) {
                analyzingPrompt.remove();
            }
        });
    });
});
