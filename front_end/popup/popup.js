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
        // 컨테이너 생성 후 스크롤을 맨 위로 이동
        setTimeout(() => {
            termContainer.scrollTop = 0;
        }, 0);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const agreeBtn = document.getElementById('agreeBtn');
    const tagInput = document.getElementById('electives');
    const tagContainer = tagInput.parentNode;
    const startSemesterSelect = document.getElementById('start-semester');
    const graduationGroup = document.getElementById('graduation-group');
    const endSemesterSelect = document.getElementById('end-semester');
    const nextButton = document.getElementById('submitPreferences');

    agreeBtn.addEventListener('click', () => {
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

    startSemesterSelect.addEventListener('change', function() {
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

    // end-semester 선택 시 이벤트
    endSemesterSelect.addEventListener('change', checkButtonState);

    // "Next" 버튼 클릭 이벤트
    nextButton.addEventListener('click', () => {
        const electives = Array.from(document.querySelectorAll('.tag')).map(tag => tag.textContent.trim());
        const startSemester = startSemesterSelect.value;
        const endSemester = endSemesterSelect.value;

        const userPreferences = {
            electives,
            startSemester,
            endSemester
        };

        console.log("User preferences:", userPreferences);

        showTermSetupView(startSemester, endSemester);
    });

    // Submit 버튼의 이벤트 리스너 추가
    const submitButton = document.getElementById('finalizeSchedule');
    submitButton.addEventListener('click', function() {
        const selectedCredits = {};
        document.querySelectorAll('#term-container select').forEach(select => {
            selectedCredits[select.name.replace('credits-', '')] = select.value;
        });
        console.log('Selected credits:', selectedCredits);
        // 여기에 선택된 크레딧을 처리하는 로직을 추가할 수 있습니다.
    });
});

// 창 닫기 버튼 이벤트
document.querySelector('.close-btn').addEventListener('click', () => {
    window.close();
    document.body.style.display = 'none';
});