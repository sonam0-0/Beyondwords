document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const currentSymbol = document.getElementById('current-symbol');
    const sentenceDisplay = document.getElementById('sentence');
    const speakBtn = document.getElementById('speak-btn');
    const clearBtn = document.getElementById('clear-btn');
    const suggestionBtns = [
        document.getElementById('suggestion1'),
        document.getElementById('suggestion2'),
        document.getElementById('suggestion3'),
        document.getElementById('suggestion4')
    ];
    
    let isProcessing = false;
    let stream = null;
    
    // Initialize camera
    async function initCamera() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: 640, 
                    height: 480,
                    facingMode: 'user' 
                } 
            });
            video.srcObject = stream;
            video.play();
            processVideo();
        } catch (err) {
            console.error("Camera error:", err);
            alert(`Camera access error: ${err.message}`);
        }
    }
    
    // Process video frames
    async function processVideo() {
        if (isProcessing) return;
        
        isProcessing = true;
        
        try {
            // Draw video frame to canvas
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            // Get image data and send to server
            canvas.toBlob(async (blob) => {
                try {
                    const formData = new FormData();
                    formData.append('frame', blob, 'frame.jpg');
                    
                    const response = await fetch('/process_frame', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        updateUI(data);
                    }
                } catch (err) {
                    console.error("Processing error:", err);
                } finally {
                    isProcessing = false;
                    requestAnimationFrame(processVideo);
                }
            }, 'image/jpeg', 0.8);
        } catch (err) {
            console.error("Frame capture error:", err);
            isProcessing = false;
            setTimeout(processVideo, 100);
        }
    }
    
    // Update UI with new data
    function updateUI(data) {
        // Update current symbol
        currentSymbol.textContent = data.symbol || '-';
        currentSymbol.className = data.symbol ? 'symbol-display active' : 'symbol-display';
        
        // Update sentence
        sentenceDisplay.textContent = data.sentence || '';
        
        // Update suggestions
        data.suggestions.forEach((suggestion, index) => {
            const btn = suggestionBtns[index];
            if (btn) {
                btn.textContent = suggestion || '';
                btn.style.visibility = suggestion ? 'visible' : 'hidden';
                btn.onclick = () => {
                    if (suggestion) {
                        // Replace last word with suggestion
                        const words = data.sentence.split(' ');
                        words.pop();
                        words.push(suggestion);
                        fetch('/process_frame', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                update_sentence: words.join(' ')
                            })
                        }).then(() => {
                            sentenceDisplay.textContent = words.join(' ');
                        });
                    }
                };
            }
        });
    }
    
    // Button event handlers
    speakBtn.addEventListener('click', () => {
        const sentence = sentenceDisplay.textContent;
        if (sentence.trim()) {
            fetch('/speak', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: sentence })
            }).catch(err => console.error("Speech error:", err));
        }
    });
    
    clearBtn.addEventListener('click', () => {
        fetch('/clear_sentence', {
            method: 'POST'
        }).then(() => {
            sentenceDisplay.textContent = '';
        });
    });
    
    // Initialize camera when page loads
    initCamera();
    
    // Clean up when page unloads
    window.addEventListener('beforeunload', () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    });
});