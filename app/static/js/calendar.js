function generateCalendar() {
    // ... existing calendar generation code ...

    // Update cell creation to include new styling
    for (let day = 1; day <= lastDay.getDate(); day++) {
        const cell = document.createElement('div');
        cell.className = 'calendar-day h-24 border rounded hover:bg-gray-50 p-2 transition-all duration-200';
        
        const dateStr = `${currentDate.getFullYear()}-${(currentDate.getMonth() + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
        
        cell.innerHTML = `
            <div class="font-bold text-gray-700">${day}</div>
            <div class="habit-completions flex flex-wrap gap-1" data-date="${dateStr}"></div>
        `;
        grid.appendChild(cell);
    }
}

function fetchHabitCompletions() {
    const completionsByDate = {};
    
    Promise.all(habits.map(habit =>
        fetch(`/get_completions/${habit.id}`)
            .then(response => response.json())
            .then(dates => {
                dates.forEach(date => {
                    if (!completionsByDate[date]) {
                        completionsByDate[date] = new Set();
                    }
                    completionsByDate[date].add(habit.id);
                    
                    const cell = document.querySelector(`[data-date="${date}"] .habit-completions`);
                    if (cell) {
                        const dot = document.createElement('div');
                        dot.className = 'habit-dot w-3 h-3 rounded-full inline-block cursor-pointer';
                        dot.style.backgroundColor = `hsl(${habit.id * 137.508}deg, 70%, 50%)`;
                        dot.title = `${habit.name} completed`;
                        cell.appendChild(dot);
                    }
                });
            })
    )).then(() => {
        // After all completions are fetched, update cell styling
        Object.entries(completionsByDate).forEach(([date, habitIds]) => {
            const cell = document.querySelector(`[data-date="${date}"]`).parentElement;
            cell.classList.add('has-completion');
            if (habitIds.size === habits.length) {
                cell.classList.add('perfect-day');
            }
        });
    });
} 