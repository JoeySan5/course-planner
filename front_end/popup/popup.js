document.getElementById('agreeBtn').addEventListener('click', () => {
    // 크롤링 시작
    const initialView = document.getElementById('initial-view');
    const questionnaireView = document.getElementById('questionnaire-view');
    
    // 첫 화면 숨기고, 질문지 표시
    initialView.classList.add('hidden');
    questionnaireView.classList.remove('hidden');
});

document.addEventListener('DOMContentLoaded', () => {
    const tagInput = document.getElementById('electives');
    const tagContainer = tagInput.parentNode;

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

    const startSemesterSelect = document.getElementById('start-semester');
    const graduationGroup = document.getElementById('graduation-group');
    const endSemesterSelect = document.getElementById('end-semester');
    
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
        return parseInt(year) * 2 + (termNumber - 1); // 연도를 2배로 해서 Spring/Fall로 나눔 (예: 2024-Spring -> 4048, 2024-Fall -> 4049)
    }

    startSemesterSelect.addEventListener('change', function() {
        const startSemester = this.value;
        const startSemesterNumber = convertSemesterToNumber(startSemester);
        
        // 졸업 학기 선택 메뉴 초기화
        endSemesterSelect.innerHTML = '';

        // 유효한 선택이 있을 때만 졸업 학기 선택 표시
        if (startSemester) {
            graduationGroup.classList.remove('hidden');

            // 최대 5년(10개의 학기) 뒤까지만 추가
            const maxSemesterNumber = startSemesterNumber + 9; // 5년 후까지, 10개의 학기까지만 표시
            allSemesters.forEach(semester => {
                const semesterNumber = convertSemesterToNumber(semester);
                if (semesterNumber >= startSemesterNumber && semesterNumber <= maxSemesterNumber) {
                    const option = document.createElement('option');
                    option.value = semester;
                    option.textContent = semester.replace('-', ' ');
                    endSemesterSelect.appendChild(option);
                }
            });

            // 추가 가능한 학기가 없으면 안내 메시지 추가
            if (endSemesterSelect.options.length === 0) {
                const noOption = document.createElement('option');
                noOption.textContent = 'No available graduation semesters';
                noOption.disabled = true;
                endSemesterSelect.appendChild(noOption);
            }
        }
    });
});

document.querySelector('.close-btn').addEventListener('click', () => {
    window.close();
    // 팝업 창을 숨기기 위해 아래 코드 사용
    document.body.style.display = 'none';
});

document.getElementById('submitPreferences').addEventListener('click', () => {
    const electives = document.getElementById('electives').value;
    const startSemester = document.getElementById('start-semester').value;
    const endSemester = document.getElementById('end-semester').value;

    const userPreferences = {
        electives: electives.split(',').map(item => item.trim()),
        startSemester,
        endSemester
    };

    console.log(userPreferences);

    // AWS 백엔드로 데이터를 전송
    fetch('http://your-aws-ec2-ip:5000/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ data: userPreferences })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        // 시간표를 출력하거나 이미지를 표시하는 다음 단계 수행
    })
    .catch(error => console.error('Error:', error));
});
