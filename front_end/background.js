// background.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.html) {
        console.log('Received HTML:', request.html);
    }
    if (request.showPopup) {
        chrome.action.openPopup();
    }
});
