function showAddHabitModal() {
    document.getElementById('addHabitModal').classList.remove('hidden');
}

function hideAddHabitModal() {
    document.getElementById('addHabitModal').classList.add('hidden');
}

function updateTimesPerDayVisibility() {
    const frequency = document.getElementById('habitFrequency').value;
    const timesPerDaySection = document.getElementById('timesPerDaySection');
    const timesPerDayInput = document.getElementById('timesPerDay');

    if (frequency === 'weekly') {
        timesPerDaySection.classList.add('hidden');
        timesPerDayInput.value = '1';
    } else {
        timesPerDaySection.classList.remove('hidden');
    }
}

function validateTimesPerDay(input) {
    const value = parseInt(input.value);
    if (value < 1) {
        input.value = '1';
    } else if (value > 10) {
        input.value = '10';
    }
}

function addHabit() {
    const name = document.getElementById('habitName').value.trim();
    const frequency = document.getElementById('habitFrequency').value;
    const timesPerDay = parseInt(document.getElementById('timesPerDay').value);

    if (!name) {
        alert('Please enter a habit name');
        return;
    }

    if (isNaN(timesPerDay) || timesPerDay < 1 || timesPerDay > 10) {
        alert('Please enter a valid number of times per day (1-10)');
        return;
    }

    fetch('/add_habit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, frequency, times_per_day: timesPerDay }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
}

function updateHabitButton(habitId, isFullyCompleted, completionsToday, totalNeeded) {
    const button = document.getElementById(`habit-button-${habitId}`);
    
    if (isFullyCompleted) {
        // Show undo button when fully completed
        button.className = 'bg-yellow-500 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded flex items-center';
        button.innerHTML = '<span class="mr-1">✓</span> Undo';
        button.onclick = () => uncompleteHabit(habitId);
    } else {
        // Show complete/+1 button when not fully completed
        const isPartiallyComplete = completionsToday > 0;
        const remainingCount = totalNeeded - completionsToday;
        
        button.className = `${isPartiallyComplete ? 'bg-blue-500 hover:bg-blue-700' : 'bg-green-500 hover:bg-green-700'} text-white font-bold py-2 px-4 rounded`;
        button.innerHTML = isPartiallyComplete ? 
            `+1 More (${remainingCount} left)` : 
            'Complete';
        button.onclick = () => completeHabit(habitId);
    }
}

function playSound(soundId) {
    const sound = document.getElementById(soundId);
    if (sound) {
        sound.currentTime = 0;
        sound.play().catch(e => console.log('Sound play failed:', e));
    }
}

function showConfirmationModal(title, message, onConfirm) {
    const modal = document.getElementById('confirmationModal');
    document.getElementById('confirmationTitle').textContent = title;
    document.getElementById('confirmationMessage').textContent = message;
    document.getElementById('confirmButton').onclick = () => {
        onConfirm();
        hideConfirmationModal();
    };
    modal.classList.remove('hidden');
}

function hideConfirmationModal() {
    document.getElementById('confirmationModal').classList.add('hidden');
}

function showHistoryModal(habitId, habitName) {
    fetch(`/habit_history/${habitId}`)
        .then(response => response.json())
        .then(data => {
            const modal = document.getElementById('historyModal');
            const content = document.getElementById('historyContent');
            
            content.innerHTML = `
                <h4 class="font-bold mb-4">${habitName}</h4>
                <div class="space-y-4">
                    ${data.history.map(entry => `
                        <div class="bg-gray-50 p-4 rounded">
                            <div class="flex justify-between items-center">
                                <div>
                                    <span class="font-medium">${entry.date}</span>
                                    <span class="text-gray-500 ml-2">${entry.completions} completion(s)</span>
                                </div>
                                <span class="text-sm text-gray-500">${entry.time}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
            
            modal.classList.remove('hidden');
        });
}

function hideHistoryModal() {
    document.getElementById('historyModal').classList.add('hidden');
}

function completeHabit(habitId) {
    const confirmMessage = "Are you sure you want to mark this habit as complete?";
    showConfirmationModal("Complete Habit", confirmMessage, () => {
        fetch(`/complete_habit/${habitId}`, {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                playSound('completionSound');
                
                updateHabitButton(
                    habitId, 
                    data.is_fully_completed,
                    data.completions,
                    data.total_needed
                );
                
                // Update streak with animation
                const streakElement = document.querySelector(`#habit-${habitId} .text-green-500`);
                if (streakElement) {
                    streakElement.textContent = data.streak;
                    streakElement.classList.add('celebrate');
                    setTimeout(() => streakElement.classList.remove('celebrate'), 500);
                }

                // Update progress bar with animation
                const progressBar = document.querySelector(`#habit-${habitId} .bg-green-500`);
                if (progressBar) {
                    progressBar.classList.remove('progress-animate');
                    void progressBar.offsetWidth; // Trigger reflow
                    const percentage = Math.min(100, (data.completions * 100) / data.total_needed);
                    progressBar.style.width = `${percentage}%`;
                    progressBar.classList.add('progress-animate');
                }

                // Update completion count
                const completionCount = document.querySelector(`#habit-${habitId} .text-sm.text-gray-500`);
                if (completionCount) {
                    completionCount.textContent = `${data.completions}/${data.total_needed} completed today`;
                }
            } else {
                alert(data.message);
            }
        });
    });
}

function uncompleteHabit(habitId) {
    const confirmMessage = "Are you sure you want to undo this completion?";
    showConfirmationModal("Undo Completion", confirmMessage, () => {
        fetch(`/uncomplete_habit/${habitId}`, {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                playSound('undoSound');
                updateHabitButton(habitId, false);
                
                // Update streak
                const streakElement = document.querySelector(`#habit-${habitId} .text-green-500`);
                if (streakElement) {
                    streakElement.textContent = data.streak;
                }
            }
        });
    });
}

function showEditHabitModal(habitId, name, frequency, timesPerDay) {
    document.getElementById('editHabitId').value = habitId;
    document.getElementById('editHabitName').value = name;
    document.getElementById('editHabitFrequency').value = frequency;
    document.getElementById('editTimesPerDay').value = timesPerDay;
    
    updateEditTimesPerDayVisibility();
    document.getElementById('editHabitModal').classList.remove('hidden');
}

function hideEditHabitModal() {
    document.getElementById('editHabitModal').classList.add('hidden');
}

function updateEditTimesPerDayVisibility() {
    const frequency = document.getElementById('editHabitFrequency').value;
    const timesPerDaySection = document.getElementById('editTimesPerDaySection');
    const timesPerDayInput = document.getElementById('editTimesPerDay');

    if (frequency === 'weekly') {
        timesPerDaySection.classList.add('hidden');
        timesPerDayInput.value = '1';
    } else {
        timesPerDaySection.classList.remove('hidden');
    }
}

function saveHabitEdit() {
    const habitId = document.getElementById('editHabitId').value;
    const name = document.getElementById('editHabitName').value.trim();
    const frequency = document.getElementById('editHabitFrequency').value;
    const timesPerDay = parseInt(document.getElementById('editTimesPerDay').value);

    if (!name) {
        alert('Please enter a habit name');
        return;
    }

    if (isNaN(timesPerDay) || timesPerDay < 1 || timesPerDay > 10) {
        alert('Please enter a valid number of times per day (1-10)');
        return;
    }

    fetch(`/edit_habit/${habitId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, frequency, times_per_day: timesPerDay }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        alert('Error: ' + error);
    });
} 