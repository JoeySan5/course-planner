// background.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.courses) {
        console.log('Received Courses:', request.courses);
    }
    if (request.showPopup) {
        chrome.action.openPopup();
    }
});
