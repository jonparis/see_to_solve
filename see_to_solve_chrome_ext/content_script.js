chrome.runtime.onMessage.addListener((message, sender, senderResponse) => {
    if (message.name === 'capture') {
        var target = document.getElementById('board-single');
        if (!target) {
            target = document.getElementsByClassName('round__app__board main-board')[0]
        }
        var element, dimensions = {};

       if (element !== target) {
            element = target;
            dimensions.top = -window.scrollY;
            
            dimensions.left = -window.scrollX;
            
            var elem = target;
            while (elem !== document.body) {
                dimensions.top += elem.offsetTop;
                dimensions.left += elem.offsetLeft;
                elem = elem.offsetParent;
            }
            dimensions.width = element.offsetWidth;
            dimensions.height = element.offsetHeight;
        }

        var resolution_multiple = 2;  
        dimensions.top = resolution_multiple * dimensions.top;
        dimensions.left = resolution_multiple * dimensions.left;
        dimensions.width = resolution_multiple * dimensions.width;
        dimensions.height = resolution_multiple * dimensions.height;

        canvas = null;
        if (!canvas) {
            canvas = document.createElement("canvas");
            document.body.appendChild(canvas);
        };
        
        var image = new Image();
        image.onload = function() {
            canvas.width = dimensions.width;
            canvas.height = dimensions.height;
            var context = canvas.getContext("2d");
            context.drawImage(image,
                dimensions.left, dimensions.top,
                dimensions.width, dimensions.height,
                0, 0,
                dimensions.width, dimensions.height
            );
            var croppedDataUrl = canvas.toDataURL("image/png").replace("image/png", "image/octet-stream"); 

            var link = document.createElement('a');
            link.setAttribute('href', croppedDataUrl);
            link.setAttribute('download', 'chess_board_' + Date.now() + '.png');
            link.click();
        };
        image.src = message.dataUrl;  
        senderResponse({success: true, message: "successful download"});
    }
})