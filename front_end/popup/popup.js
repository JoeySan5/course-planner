// 전역 변수 및 함수 정의
const allSemesters = [
    "2024-Spring", "2024-Fall",
    "2025-Spring", "2025-Fall",
    "2026-Spring", "2026-Fall",
    "2027-Spring", "2027-Fall",
    "2028-Spring", "2028-Fall",
    "2029-Spring"
];

function convertSemesterToNumber(semester) {
    const [year, term] = semester.split('-');
    const termNumber = (term === "Spring") ? 1 : 2;
    return parseInt(year) * 2 + (termNumber - 1);
}

function fetchHTML() {
    console.log("fetchHTML function called");

    // 전체 HTML 콘텐츠 가져오기
    const htmlContent = document.documentElement.outerHTML;
    console.log(htmlContent);

    // HTML 구조에서 원하는 과목명 추출
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlContent, "text/html");

    // 'takenCourse'와 'takenCourse ip' 클래스 행들을 선택
    const takenCourses = doc.querySelectorAll('tr.takenCourse, tr.takenCourse.ip');

    // 과목명을 저장할 Set (중복 제거)
    let courseNamesSet = new Set();

    // 각 행을 순회하며 과목명을 추출
    takenCourses.forEach((row) => {
        const courseTd = row.querySelector('td.course');
        if (courseTd) {
            // 공백 제거 후 과목명 추가
            const courseName = courseTd.textContent.trim().replace(/\s+/g, '');
            courseNamesSet.add(courseName);
        }
    });

    // Set을 배열로 변환하여 콘솔에 출력
    const courseNames = Array.from(courseNamesSet);
    console.log(courseNames);

    // chrome runtime으로 과목명 데이터도 함께 전송
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
    let selectedMajor = ""; // 전역 변수로 선택된 전공 저장

    // 기존 크롤링 데이터 받기
    chrome.runtime.onMessage.addListener((request) => {
        if (request.courses) {
            extractedCourses = request.courses;
            console.log("Extracted courses:", extractedCourses);
        }
    });

    // Goal Major 선택 시 Agree 버튼 활성화
    goalMajorSelect.addEventListener('change', () => {
        selectedMajor = goalMajorSelect.value;

        if (selectedMajor) {
            agreeBtn.disabled = false; // 전공 선택 시 버튼 활성화
            agreeBtn.classList.add('active'); // 버튼에 활성화 스타일 추가
        } else {
            agreeBtn.disabled = true; // 전공 미선택 시 버튼 비활성화
            agreeBtn.classList.remove('active'); // 버튼에서 활성화 스타일 제거
        }
    });

    // Agree 버튼 클릭 이벤트 - Goal Major 로직 포함
    agreeBtn.addEventListener('click', () => {
        // Goal Major 선택 여부 확인
        if (!selectedMajor) {
            alert("Please select your Goal Major.");
            return; // Goal Major 선택하지 않으면 진행되지 않음
        }

        // 선택된 Goal Major 정보 출력 (추후 로직에 사용 가능)
        console.log("Selected Goal Major:", selectedMajor);

        // 기존 로직: Agree 버튼 클릭 시 다음 화면으로 이동
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

    // 태그 입력 관련 코드
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

    // 버튼 활성화 상태를 체크하는 함수
    function checkButtonState() {
        nextButton.disabled = !(startSemesterSelect.value && endSemesterSelect.value);
    }

    // 초기 버튼 상태 설정
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

    // "Next" 버튼 클릭 이벤트
    nextButton.addEventListener('click', () => {
        const electives = Array.from(document.querySelectorAll('.tag')).map(tag => tag.textContent.trim());
        const startSemester = startSemesterSelect.value;
        const endSemester = endSemesterSelect.value;

        if (startSemester && endSemester) {
            showTermSetupView(startSemester, endSemester);
        }
    });

    // Submit 버튼의 이벤트 리스너 추가
    const submitButton = document.getElementById('finalizeSchedule');
    submitButton.addEventListener('click', function() {
    const selectedCredits = {};
    document.querySelectorAll('#term-container select').forEach(select => {
        selectedCredits[select.name.replace('credits-', '')] = select.value;
    });

    // 모든 데이터를 JSON으로 정리
    const finalData = {
        goalMajor: selectedMajor,
        takenCourses: extractedCourses,
        startSemester: startSemesterSelect.value,
        endSemester: endSemesterSelect.value,
        selectedCredits: selectedCredits,
        userPreferences: Array.from(document.querySelectorAll('.tag')).map(tag => tag.textContent.trim())
    };

    console.log('Final Data:', JSON.stringify(finalData, null, 2));

    // "Analyzing..." 프롬프트 표시
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

    // ec2 sending
    const ec2Url = 'http://172.31.32.189:5000/api'; // acutal url
    fetch(ec2Url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        alert('Data successfully sent to EC2');
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
