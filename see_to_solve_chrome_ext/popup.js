document.addEventListener('DOMContentLoaded', async () => {
  const responseDiv = document.getElementById('responseMessage');

  try {
    // Query the active tab in the current window.
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) {
      responseDiv.textContent = 'No active tab found.';
      return;
    }
    const tabId = tab.id;

    // Execute a script in the active tab to compute the target element’s dimensions.
    const [{ result: dimensions }] = await chrome.scripting.executeScript({
      target: { tabId },
      func: () => {
        let target = document.getElementById('board-single');
        if (!target) {
          // Try fallback if the element with ID 'board-single' isn't found.
          const els = document.getElementsByClassName('round__app__board main-board');
          if (els.length > 0 && els[0].firstElementChild && els[0].firstElementChild.firstElementChild) {
            target = els[0].firstElementChild.firstElementChild;
          }
        }
        if (!target) return null;

        const rect = target.getBoundingClientRect();
        return {
          top: (rect.top + window.scrollY) * window.devicePixelRatio,
          left: (rect.left + window.scrollX) * window.devicePixelRatio,
          width: rect.width * window.devicePixelRatio,
          height: rect.height * window.devicePixelRatio
        };
      }
    });

    if (!dimensions) {
      responseDiv.textContent = 'Target element not found on the page.';
      return;
    }

    // Capture the entire visible tab as a screenshot.
    chrome.tabs.captureVisibleTab(null, { format: "png" }, (dataUrl) => {
      if (chrome.runtime.lastError) {
        responseDiv.textContent = 'Error capturing tab: ' + chrome.runtime.lastError.message;
        return;
      }

      // Load the screenshot image.
      const image = new Image();
      image.onload = () => {
        // Create a canvas to crop the image.
        const canvas = document.createElement("canvas");
        canvas.width = dimensions.width;
        canvas.height = dimensions.height;
        const context = canvas.getContext("2d");

        // Crop the screenshot using the dimensions of the target element.
        context.drawImage(
          image,
          dimensions.left, dimensions.top, dimensions.width, dimensions.height, // Source crop
          0, 0, dimensions.width, dimensions.height // Destination
        );

        // Convert the canvas to a data URL and then to a Blob.
        const croppedDataUrl = canvas.toDataURL("image/png");

        // Helper function: Convert data URL to Blob.
        function dataURLtoBlob(dataurl) {
          const arr = dataurl.split(',');
          const mimeMatch = arr[0].match(/:(.*?);/);
          const mime = mimeMatch ? mimeMatch[1] : 'image/png';
          const bstr = atob(arr[1]);
          let n = bstr.length;
          const u8arr = new Uint8Array(n);
          while (n--) {
            u8arr[n] = bstr.charCodeAt(n);
          }
          return new Blob([u8arr], { type: mime });
        }

        const blob = dataURLtoBlob(croppedDataUrl);

        // Create form data and append the cropped image.
        const formData = new FormData();
        formData.append('image', blob, 'screenshot.png');

        // Send the cropped image to the Python service.
        fetch('http://localhost:5000/process-image', {
          method: 'POST',
          body: formData
        })
          .then(response => response.json())
          .then(data => {
            responseDiv.textContent = data.text;
          })
          .catch(error => {
            responseDiv.textContent = 'Error: ' + error;
          });
      };

      image.src = dataUrl;
    });

  } catch (err) {
    responseDiv.textContent = 'Error: ' + err;
  }
});
