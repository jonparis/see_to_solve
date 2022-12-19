var continuous_capture = false  // Set to true for continuous capture
var capture_every_x_seconds = 5;
chrome.action.onClicked.addListener(function (tab) {
    if(continuous_capture){
        if (typeof get_images === 'undefined'){
            var get_images = false;
        }
        if(get_images){
            clearInterval(get_images);
            get_images = false;
        }
        else {
            get_images = setInterval(function() { capture_board(tab); }, 1000 * capture_every_x_seconds);
        }
    } else {
        capture_board(tab);
    }
});


function capture_board(tab){
    chrome.tabs.captureVisibleTab(tab.windowId, { format: "png" }, function(dataUrl) {
        setTimeout(() => {
                chrome.tabs.sendMessage(tab.id, {name: "capture", dataUrl: dataUrl}, 
                    (response) => {
                        if (response.success) {
                            console.log("success")
                        } else {
                            console.log("failed download")
                        }
                    })
            }, 200);
    });
}