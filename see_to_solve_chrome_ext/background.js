if (typeof get_images === 'undefined'){
    var get_images = false;
}

chrome.action.onClicked.addListener(function (tab) {
    if(get_images){
        clearInterval(get_images);
        get_images = false;
    }
    else {
        get_images = setInterval(function() { 
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
        }, 5000);
    }
});