// background.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.showPopup) {
        chrome.action.openPopup();
    }
});
