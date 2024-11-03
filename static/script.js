document.addEventListener('DOMContentLoaded', () => {
    const collectionContainer = document.getElementById('collection-container');
    const collectionItemInput = document.getElementById('collection-item');
    const addItemButton = document.getElementById('add-item-btn');
    const collectionList = document.getElementById('collection-list');

    // Functionality for adding items to the collection
    addItemButton.addEventListener('click', () => {
        const item = collectionItemInput.value;
        if (item) {
            // Add the item to the collection
            const li = document.createElement('li');
            li.textContent = item;
            collectionList.appendChild(li);
            collectionItemInput.value = ''; // Clear input field
        } else {
            alert('Please enter an item to add to your collection.');
        }
    });

    // Functionality for the camera button
    document.getElementById('cameraButton').addEventListener('click', () => {
        window.location.href = 'camera.html'; // Ensure this file exists
    });

    // Functionality for the collection button
    document.getElementById('collectionButton').addEventListener('click', () => {
        collectionContainer.style.display = 'block'; // Show the collection container
    });

    // Camera Functionality
    const takePhotoButton = document.getElementById('takePhotoButton');
    const video = document.getElementById('cameraStream');
    const canvas = document.getElementById('photoCanvas');

    async function startCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
        } catch (error) {
            alert('Error accessing the camera: ' + error.message);
        }
    }

    function takePhoto() {
        const video = document.getElementById('cameraStream');
        const canvas = document.getElementById('photoCanvas');
        const photo = document.getElementById('capturedPhoto');
    
        // Set canvas size to match video stream
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
    
        // Draw the current frame from the video onto the canvas
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
        // Convert the canvas to a data URL and display the photo
        const dataUrl = canvas.toDataURL('image/png');
        photo.src = dataUrl;
        photo.style.display = 'block'; // Show the captured photo
        video.style.display = 'none'; // Hide the live video stream
        document.getElementById('takePhotoButton').style.display = 'none'; // Hide the "Take Photo" button
        document.getElementById('flipCameraButton').style.display = 'none'; // Hide the "Flip Camera" button
        document.getElementById('newPhotoButton').style.display = 'inline'; // Show the "New Picture" button
    
        // Send the dataUrl to the server
        sendDataUrlToServer(dataUrl);
    }
    
    // Function to send the data URL to the server
    function sendDataUrlToServer(dataUrl) {
        const url = 'http://127.0.0.1:5000/classify_image'; // Replace with your server URL
    
        // Construct the request payload
        const payload = {
            image: dataUrl // Include the image data
        };
    
        // Send a POST request using fetch
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json' // Content type is JSON
            },
            body: JSON.stringify(payload) // Convert the payload to a JSON string
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // Parse the JSON from the response
        })
        .then(data => {
            console.log('Success:', data); // Handle the success response
            alert('Photo successfully sent to the server!');
        })
        .catch(error => {
            console.error('Error:', error); // Handle any errors
            alert('Failed to send photo. Please try again.');
        });
    }
    
});
