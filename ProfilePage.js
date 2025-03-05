function createBubbles() {
    let container = document.querySelector('.bubble-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'bubble-container';
        document.body.insertBefore(container, document.body.firstChild);
    }

    const bubbleCount = 20;
    const colors = [
        'rgba(233, 30, 99, 0.1)',
        'rgba(233, 30, 99, 0.15)',
        'rgba(233, 30, 99, 0.2)'
    ];

    for (let i = 0; i < bubbleCount; i++) {
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        
        // Random size between 60px and 240px
        const size = Math.random() * 180 + 60;
        bubble.style.width = `${size}px`;
        bubble.style.height = `${size}px`;
        
        // Random starting positions
        bubble.style.left = `${Math.random() * 100}vw`;
        bubble.style.top = `${Math.random() * 100}vh`;
        
        // Random movement parameters
        const randomX = Math.random() * 200 - 100; // -100 to 100
        const randomY = Math.random() * 200 - 100; // -100 to 100
        
        bubble.style.setProperty('--moveX', `${randomX}vw`);
        bubble.style.setProperty('--moveY', `${randomY}vh`);
        
        // Random animation duration
        bubble.style.animationDuration = `${20 + Math.random() * 10}s`;
        
        // Random color from array
        bubble.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        
        container.appendChild(bubble);
    }
}

// Create initial bubbles
createBubbles();

// Optional: Recreate bubbles every 30 seconds for new patterns
setInterval(createBubbles, 30000);

function showPCODReport() {
    document.getElementById('displayArea').innerHTML = `
        <h2>PCOD Report</h2>
        <p>Your latest PCOD analysis and recommendations:</p>
        <ul>
            <li>Risk Factor: Low</li>
            <li>Last Check: 01/03/2024</li>
            <li>Recommendations: 
                <ul>
                    <li>Maintain regular exercise</li>
                    <li>Follow balanced diet</li>
                    <li>Regular health check-ups</li>
                </ul>
            </li>
        </ul>
    `;
}

function showPeriodTrack() {
    document.getElementById('displayArea').innerHTML = `
        <h2>Period Tracking</h2>
        <p>Your menstrual cycle information:</p>
        <ul>
            <li>Last Period: 15/02/2024</li>
            <li>Cycle Length: 28 days</li>
            <li>Next Expected: 14/03/2024</li>
            <li>Cycle Regularity: Regular</li>
        </ul>
    `;
}

function showSettings() {
    document.getElementById('displayArea').innerHTML = `
        <h2>Settings</h2>
        <ul>
            <li>Profile Settings</li>
            <li>Notification Preferences</li>
            <li>Privacy Settings</li>
            <li>Account Management</li>
            <li>Help & Support</li>
        </ul>
    `;
}