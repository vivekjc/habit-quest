const sounds = {
    complete: new Audio('/static/sounds/complete.mp3'),
    levelUp: new Audio('/static/sounds/level-up.mp3'),
    achievement: new Audio('/static/sounds/achievement.mp3'),
    switch: new Audio('/static/sounds/switch.mp3')
};

function playSound(soundName) {
    sounds[soundName].play().catch(e => console.log('Sound play failed:', e));
}

function updateDarkMode(isDark) {
    document.querySelectorAll('.progress-bar').forEach(bar => {
        bar.style.opacity = '0';
        setTimeout(() => {
            bar.style.opacity = '1';
        }, 300);
    });

    document.querySelectorAll('.character').forEach(char => {
        char.style.transition = 'filter 0.3s ease';
    });

    document.querySelectorAll('.achievement-badge').forEach(badge => {
        badge.style.transition = 'filter 0.3s ease';
    });

    playSound('switch');
}

darkModeToggle.addEventListener('click', () => {
    html.classList.toggle('dark');
    localStorage.setItem('darkMode', html.classList.contains('dark'));
    updateDarkMode(html.classList.contains('dark'));
}); 