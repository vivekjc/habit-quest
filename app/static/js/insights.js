function loadAnalytics() {
    fetch('/analyze_habits')
        .then(response => response.json())
        .then(data => {
            // Render correlations
            const correlationsHtml = data.correlations.map(correlation => `
                <div class="bg-gray-50 p-4 rounded">
                    <div class="flex justify-between items-center">
                        <div>
                            <span class="font-medium">${correlation.habit1}</span>
                            <span class="text-gray-400 mx-2">×</span>
                            <span class="font-medium">${correlation.habit2}</span>
                        </div>
                        <div class="text-green-600 font-bold">${correlation.strength}%</div>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
                        <div class="bg-green-500 h-2 rounded-full" 
                             style="width: ${correlation.strength}%">
                        </div>
                    </div>
                </div>
            `).join('');
            
            document.getElementById('correlations-container').innerHTML = 
                correlationsHtml || '<p class="text-gray-500">No significant correlations found yet</p>';

            // Render projections
            const projectionsHtml = data.projections.map(projection => `
                <div class="bg-gray-50 p-4 rounded">
                    <div class="flex justify-between items-center mb-2">
                        <span class="font-medium">${projection.habit_name}</span>
                        <span class="text-sm ${projection.trend === 'improving' ? 'text-green-600' : 'text-red-600'}">
                            <i class="fas fa-${projection.trend === 'improving' ? 'arrow-up' : 'arrow-down'} mr-1"></i>
                            ${projection.trend}
                        </span>
                    </div>
                    <div class="text-sm text-gray-600">
                        Current completion rate: ${projection.current_rate}%
                        ${projection.days_to_goal ? 
                            `<br>Projected days to goal: ${projection.days_to_goal}` : 
                            ''}
                    </div>
                </div>
            `).join('');
            
            document.getElementById('projections-container').innerHTML = projectionsHtml;

            // Store export data
            window.exportData = data.export_data;
        });
}

function exportData() {
    if (!window.exportData) return;

    const dataStr = JSON.stringify(window.exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `habit-tracker-export-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

function getChartOptions(isDark = document.documentElement.classList.contains('dark')) {
    return {
        responsive: true,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    color: isDark ? '#e5e7eb' : '#1f2937'
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                },
                ticks: {
                    color: isDark ? '#e5e7eb' : '#1f2937'
                }
            },
            x: {
                grid: {
                    color: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                },
                ticks: {
                    color: isDark ? '#e5e7eb' : '#1f2937'
                }
            }
        }
    };
}

// Update chart themes when dark mode changes
document.getElementById('darkModeToggle').addEventListener('click', () => {
    const isDark = document.documentElement.classList.contains('dark');
    
    // Update all charts with new theme
    Chart.instances.forEach(chart => {
        chart.options = { ...chart.options, ...getChartOptions(isDark) };
        chart.update();
    });
});

// Load analytics when page loads
loadAnalytics(); 