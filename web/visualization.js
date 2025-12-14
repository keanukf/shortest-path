/**
 * Visualization engine for pathfinding algorithms.
 * Handles canvas rendering, step-by-step animation, and synchronization.
 */

class AlgorithmVisualizer {
    constructor(canvas, gridData, algorithmData) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.gridData = gridData;
        this.algorithmData = algorithmData;
        
        // Calculate cell size to fit canvas
        this.cellSize = Math.min(
            Math.floor(canvas.width / gridData.width),
            Math.floor(canvas.height / gridData.height)
        );
        
        // Adjust canvas size to fit grid exactly
        canvas.width = this.cellSize * gridData.width;
        canvas.height = this.cellSize * gridData.height;
        
        // Current step
        this.currentStep = 0;
        this.maxSteps = algorithmData.steps.length - 1;
        
        // Color mapping
        this.colors = {
            unvisited: '#1e2742',
            visited: '#3b82f6',
            visitedLight: '#60a5fa',
            frontier: '#fbbf24',
            path: '#10b981',
            pathGlow: '#34d399',
            obstacle: '#1f2937',
            start: '#06b6d4',
            end: '#ec4899'
        };
        
        // Initialize
        this.render();
    }
    
    /**
     * Render the current state of the algorithm.
     */
    render() {
        const ctx = this.ctx;
        const step = this.algorithmData.steps[this.currentStep];
        
        // Clear canvas
        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw grid cells
        for (let row = 0; row < this.gridData.height; row++) {
            for (let col = 0; col < this.gridData.width; col++) {
                this.drawCell(row, col, step);
            }
        }
    }
    
    /**
     * Draw a single cell.
     */
    drawCell(row, col, step) {
        const ctx = this.ctx;
        const x = col * this.cellSize;
        const y = row * this.cellSize;
        const coord = [row, col];
        
        // Check if this is start or end
        if (this.gridData.start && 
            this.gridData.start[0] === row && 
            this.gridData.start[1] === col) {
            this.drawStartEnd(x, y, this.colors.start);
            return;
        }
        
        if (this.gridData.end && 
            this.gridData.end[0] === row && 
            this.gridData.end[1] === col) {
            this.drawStartEnd(x, y, this.colors.end);
            return;
        }
        
        // Check if obstacle
        if (this.isObstacle(row, col)) {
            ctx.fillStyle = this.colors.obstacle;
            ctx.fillRect(x, y, this.cellSize, this.cellSize);
            return;
        }
        
        // Check state priority: path > frontier > visited > unvisited
        if (step.path && this.isInArray(coord, step.path)) {
            this.drawPath(x, y);
        } else if (this.isInArray(coord, step.frontier)) {
            ctx.fillStyle = this.colors.frontier;
            ctx.fillRect(x, y, this.cellSize, this.cellSize);
        } else if (this.isInArray(coord, step.visited)) {
            // Use gradient based on visit order for visual interest
            const visitIndex = step.visited.findIndex(v => 
                v[0] === row && v[1] === col
            );
            const alpha = Math.max(0.3, 1 - (visitIndex / step.visited.length) * 0.5);
            ctx.fillStyle = this.colors.visited;
            ctx.globalAlpha = alpha;
            ctx.fillRect(x, y, this.cellSize, this.cellSize);
            ctx.globalAlpha = 1.0;
        } else {
            ctx.fillStyle = this.colors.unvisited;
            ctx.fillRect(x, y, this.cellSize, this.cellSize);
        }
        
        // Draw grid lines (subtle)
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.lineWidth = 0.5;
        ctx.strokeRect(x, y, this.cellSize, this.cellSize);
    }
    
    /**
     * Draw start or end node with special styling.
     */
    drawStartEnd(x, y, color) {
        const ctx = this.ctx;
        const centerX = x + this.cellSize / 2;
        const centerY = y + this.cellSize / 2;
        const radius = this.cellSize * 0.35;
        
        // Background
        ctx.fillStyle = this.colors.unvisited;
        ctx.fillRect(x, y, this.cellSize, this.cellSize);
        
        // Circle
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        ctx.fill();
        
        // Glow effect
        ctx.shadowColor = color;
        ctx.shadowBlur = 8;
        ctx.fill();
        ctx.shadowBlur = 0;
    }
    
    /**
     * Draw path cell with glow effect.
     */
    drawPath(x, y) {
        const ctx = this.ctx;
        
        // Base color
        ctx.fillStyle = this.colors.path;
        ctx.fillRect(x, y, this.cellSize, this.cellSize);
        
        // Glow effect
        ctx.shadowColor = this.colors.pathGlow;
        ctx.shadowBlur = 4;
        ctx.fillRect(x, y, this.cellSize, this.cellSize);
        ctx.shadowBlur = 0;
    }
    
    /**
     * Check if a coordinate is in an array.
     */
    isInArray(coord, array) {
        if (!array) return false;
        return array.some(item => item[0] === coord[0] && item[1] === coord[1]);
    }
    
    /**
     * Check if a position is an obstacle.
     */
    isObstacle(row, col) {
        if (!this.gridData.obstacles) return false;
        return this.gridData.obstacles.some(
            obs => obs[0] === row && obs[1] === col
        );
    }
    
    /**
     * Go to a specific step.
     */
    goToStep(step) {
        this.currentStep = Math.max(0, Math.min(step, this.maxSteps));
        this.render();
    }
    
    /**
     * Get current step.
     */
    getCurrentStep() {
        return this.currentStep;
    }
    
    /**
     * Get max steps.
     */
    getMaxSteps() {
        return this.maxSteps;
    }
    
    /**
     * Reset to first step.
     */
    reset() {
        this.currentStep = 0;
        this.render();
    }
}

/**
 * Synchronized visualizer for multiple algorithms.
 */
class SynchronizedVisualizer {
    constructor(container, comparisonData) {
        this.container = container;
        this.comparisonData = comparisonData;
        this.visualizers = [];
        this.isPlaying = false;
        this.currentStep = 0;
        this.maxSteps = 0;
        this.animationSpeed = 5; // steps per frame
        this.animationFrameId = null;
        
        this.createPanels();
    }
    
    /**
     * Create visualization panels for each algorithm.
     */
    createPanels() {
        this.container.innerHTML = '';
        this.visualizers = [];
        
        // Find max steps across all algorithms
        this.maxSteps = Math.max(
            ...this.comparisonData.algorithms.map(algo => algo.steps.length - 1)
        );
        
        // Create panel for each algorithm
        this.comparisonData.algorithms.forEach((algorithmData, index) => {
            const panel = document.createElement('div');
            panel.className = 'algorithm-panel';
            
            const title = document.createElement('h3');
            title.className = 'algorithm-title';
            title.textContent = algorithmData.name;
            panel.appendChild(title);
            
            const canvasContainer = document.createElement('div');
            canvasContainer.className = 'canvas-container';
            
            const canvas = document.createElement('canvas');
            canvas.width = 600;
            canvas.height = 600;
            canvasContainer.appendChild(canvas);
            panel.appendChild(canvasContainer);
            
            this.container.appendChild(panel);
            
            // Create visualizer
            const visualizer = new AlgorithmVisualizer(
                canvas,
                this.comparisonData.grid,
                algorithmData
            );
            this.visualizers.push(visualizer);
        });
    }
    
    /**
     * Go to a specific step across all visualizers.
     */
    goToStep(step) {
        this.currentStep = Math.max(0, Math.min(step, this.maxSteps));
        this.visualizers.forEach(viz => {
            const maxSteps = viz.getMaxSteps();
            const relativeStep = Math.min(this.currentStep, maxSteps);
            viz.goToStep(relativeStep);
        });
    }
    
    /**
     * Reset all visualizers.
     */
    reset() {
        this.currentStep = 0;
        this.isPlaying = false;
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
        this.visualizers.forEach(viz => viz.reset());
    }
    
    /**
     * Play animation.
     */
    play() {
        if (this.isPlaying) return;
        this.isPlaying = true;
        this.animate();
    }
    
    /**
     * Pause animation.
     */
    pause() {
        this.isPlaying = false;
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
    }
    
    /**
     * Animation loop.
     */
    animate() {
        if (!this.isPlaying) return;
        
        if (this.currentStep < this.maxSteps) {
            this.currentStep += this.animationSpeed;
            this.goToStep(this.currentStep);
            this.animationFrameId = requestAnimationFrame(() => this.animate());
        } else {
            this.pause();
        }
    }
    
    /**
     * Set animation speed.
     */
    setSpeed(speed) {
        this.animationSpeed = speed;
    }
    
    /**
     * Get current step.
     */
    getCurrentStep() {
        return this.currentStep;
    }
    
    /**
     * Get max steps.
     */
    getMaxSteps() {
        return this.maxSteps;
    }
}

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AlgorithmVisualizer, SynchronizedVisualizer };
}

