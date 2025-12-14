/**
 * Main application logic for pathfinding algorithm comparison.
 */

let synchronizedVisualizer = null;
let presets = {};

// DOM elements
const presetSelect = document.getElementById('preset-select');
const runButton = document.getElementById('run-button');
const loading = document.getElementById('loading');
const visualizationContainer = document.getElementById('visualization-container');
const algorithmPanels = document.getElementById('algorithm-panels');
const playPauseBtn = document.getElementById('play-pause');
const resetBtn = document.getElementById('reset');
const speedSlider = document.getElementById('speed-slider');
const speedValue = document.getElementById('speed-value');
const stepInfo = document.getElementById('step-info');
const metricsContent = document.getElementById('metrics-content');

/**
 * Initialize the application.
 */
async function init() {
    // Load presets
    await loadPresets();
    
    // Set up event listeners
    runButton.addEventListener('click', handleRun);
    playPauseBtn.addEventListener('click', handlePlayPause);
    resetBtn.addEventListener('click', handleReset);
    speedSlider.addEventListener('input', handleSpeedChange);
    
    // Update speed display
    speedValue.textContent = `${speedSlider.value}x`;
}

/**
 * Load preset configurations from API.
 */
async function loadPresets() {
    try {
        const response = await fetch('/api/presets');
        presets = await response.json();
    } catch (error) {
        console.error('Failed to load presets:', error);
    }
}

/**
 * Handle run button click.
 */
async function handleRun() {
    // Get selected algorithms
    const selectedAlgorithms = [];
    if (document.getElementById('algo-dijkstra').checked) {
        selectedAlgorithms.push('Dijkstra');
    }
    if (document.getElementById('algo-astar-manhattan').checked) {
        selectedAlgorithms.push('AStar:manhattan');
    }
    if (document.getElementById('algo-astar-euclidean').checked) {
        selectedAlgorithms.push('AStar:euclidean');
    }
    if (document.getElementById('algo-astar-chebyshev').checked) {
        selectedAlgorithms.push('AStar:chebyshev');
    }
    
    if (selectedAlgorithms.length === 0) {
        alert('Please select at least one algorithm.');
        return;
    }
    
    // Get preset
    const presetName = presetSelect.value;
    const preset = presets[presetName];
    
    if (!preset) {
        alert('Invalid preset selected.');
        return;
    }
    
    // Prepare request data
    const requestData = {
        width: preset.width,
        height: preset.height,
        start: preset.start,
        end: preset.end,
        allow_diagonal: preset.allow_diagonal || false,
        algorithms: selectedAlgorithms
    };
    
    // Handle random obstacles
    if (preset.obstacles === 'random') {
        // Generate random obstacles on backend
        requestData.obstacles = [];
        requestData.density = preset.density || 0.25;
    } else {
        requestData.obstacles = preset.obstacles || [];
    }
    
    // Show loading
    loading.classList.remove('hidden');
    visualizationContainer.classList.add('hidden');
    runButton.disabled = true;
    
    try {
        // Call API
        const response = await fetch('/api/compare', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to run comparison');
        }
        
        const comparisonData = await response.json();
        
        // Create visualizer
        synchronizedVisualizer = new SynchronizedVisualizer(
            algorithmPanels,
            comparisonData
        );
        
        // Display metrics
        displayMetrics(comparisonData.algorithms);
        
        // Show visualization
        loading.classList.add('hidden');
        visualizationContainer.classList.remove('hidden');
        
        // Update step info
        updateStepInfo();
        
    } catch (error) {
        console.error('Error running comparison:', error);
        alert('Error: ' + error.message);
        loading.classList.add('hidden');
    } finally {
        runButton.disabled = false;
    }
}

/**
 * Display performance metrics.
 */
function displayMetrics(algorithms) {
    metricsContent.innerHTML = '';
    
    // Create comparison metrics
    const comparisonCard = document.createElement('div');
    comparisonCard.className = 'metric-card';
    comparisonCard.innerHTML = `
        <h3>Algorithm Comparison</h3>
        <div class="metric-comparison">
            ${algorithms.map(algo => `
                <div class="metric-item">
                    <div class="metric-value">${algo.metrics.nodes_visited}</div>
                    <div class="metric-label">${algo.name}</div>
                </div>
            `).join('')}
        </div>
    `;
    metricsContent.appendChild(comparisonCard);
    
    // Create individual metric cards
    algorithms.forEach(algorithm => {
        const card = document.createElement('div');
        card.className = 'metric-card';
        card.innerHTML = `
            <h3>${algorithm.name}</h3>
            <div class="metric-value">${algorithm.metrics.nodes_visited}</div>
            <div class="metric-label">Nodes Visited</div>
            <div class="metric-value" style="margin-top: 1rem;">${algorithm.metrics.path_length}</div>
            <div class="metric-label">Path Length</div>
            <div class="metric-value" style="margin-top: 1rem; color: ${algorithm.metrics.path_found ? '#10b981' : '#ef4444'};">
                ${algorithm.metrics.path_found ? '✓ Found' : '✗ Not Found'}
            </div>
        `;
        metricsContent.appendChild(card);
    });
}

/**
 * Handle play/pause button.
 */
function handlePlayPause() {
    if (!synchronizedVisualizer) return;
    
    if (synchronizedVisualizer.isPlaying) {
        synchronizedVisualizer.pause();
        playPauseBtn.textContent = '▶ Play';
    } else {
        synchronizedVisualizer.play();
        playPauseBtn.textContent = '⏸ Pause';
        
        // Update step info during animation
        const updateStepInfoInterval = setInterval(() => {
            if (!synchronizedVisualizer.isPlaying) {
                clearInterval(updateStepInfoInterval);
                return;
            }
            updateStepInfo();
        }, 100);
    }
}

/**
 * Handle reset button.
 */
function handleReset() {
    if (!synchronizedVisualizer) return;
    
    synchronizedVisualizer.reset();
    playPauseBtn.textContent = '▶ Play';
    updateStepInfo();
}

/**
 * Handle speed slider change.
 */
function handleSpeedChange() {
    const speed = parseInt(speedSlider.value);
    speedValue.textContent = `${speed}x`;
    
    if (synchronizedVisualizer) {
        synchronizedVisualizer.setSpeed(speed);
    }
}

/**
 * Update step info display.
 */
function updateStepInfo() {
    if (!synchronizedVisualizer) {
        stepInfo.textContent = 'Step: 0 / 0';
        return;
    }
    
    const current = synchronizedVisualizer.getCurrentStep();
    const max = synchronizedVisualizer.getMaxSteps();
    stepInfo.textContent = `Step: ${current} / ${max}`;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

