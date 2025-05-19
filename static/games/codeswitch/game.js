// Global variables
let canvas, ctx, startScreen, startButton;
let scoreElement, languageElement, classNameElement, speedElement;
let lastTime, animationId, isPaused;

// Sound effects
const sounds = {
    collect: new Audio('assets/sounds/collect.wav'),
    levelUp: new Audio('assets/sounds/level-up.wav'),
    select: new Audio('assets/sounds/select.wav'),
    background: new Audio('assets/sounds/background.mp3')
};

// Game configuration
const config = {
    width: window.innerWidth,
    height: window.innerHeight,
    player: {
        baseSize: 20,
        baseSpeed: 5,
        // Class configurations
        classes: {
            hacker: {
                name: 'Hacker',
                sizeMultiplier: 0.7,
                speedMultiplier: 1.8,
                growthRate: 0.3,
                color: '#00ff00',
                description: 'Fast and nimble, but starts small and grows slowly',
                symbol: '{}',
                symbolColor: '#00ff00'
            },
            engineer: {
                name: 'Engineer',
                sizeMultiplier: 1.0,
                speedMultiplier: 1.0,
                growthRate: 0.5,
                color: '#00aaff',
                description: 'Balanced stats for steady growth',
                symbol: '[]',
                symbolColor: '#00aaff'
            },
            architect: {
                name: 'Architect',
                sizeMultiplier: 1.5,
                speedMultiplier: 0.6,
                growthRate: 0.8,
                color: '#ff55ff',
                description: 'Starts big but moves slowly, grows quickly',
                symbol: '<>',
                symbolColor: '#ff55ff'
            }
        }
    },
    tokens: {
        count: 50,
        minSize: 5,
        maxSize: 15,
        colors: ['#ff5555', '#55ff55', '#5555ff', '#ffff55', '#ff55ff', '#55ffff']
    },
    languages: ['Python', 'JavaScript', 'Java', 'C++', 'Ruby', 'Go', 'Rust', 'TypeScript']
};

// Game states
const GAME_STATES = {
    MENU: 'menu',
    PLAYING: 'playing',
    PAUSED: 'paused',
    GAME_OVER: 'game_over'
};

// DOM elements
let canvas, ctx, startScreen, startButton;
let scoreElement, languageElement, classNameElement, speedElement;
let lastTime, animationId, isPaused;

// Game state
const state = {
    player: null,
    tokens: [],
    particles: [],
    lastTime: 0,
    deltaTime: 0,
    keys: {},
    isPaused: false,
    gameOver: false,
    score: 0,
    level: 1,
    gameStarted: false,
    selectedClass: null,
    accumulator: 0,
    timestep: 1000/60, // 60 FPS
    currentState: 'MENU', // MENU, PLAYING, GAME_OVER
    animationId: null
};

// Initialize game
function init() {
    console.log('Initializing game...');
    
    try {
        // Set initial game state
        state.currentState = 'MENU';
        state.gameStarted = false;
        state.gameOver = false;
        state.selectedClass = null;
        
        // Get DOM elements
        canvas = document.getElementById('gameCanvas');
        ctx = canvas.getContext('2d');
        startScreen = document.getElementById('startScreen');
        startButton = document.getElementById('startButton');
        scoreElement = document.getElementById('score');
        languageElement = document.getElementById('language');
        classNameElement = document.getElementById('class-name');
        speedElement = document.getElementById('speed');
        
        // Set up class selection
        document.querySelectorAll('.class-option').forEach(option => {
            option.addEventListener('click', () => {
                // Remove selected class from all options
                document.querySelectorAll('.class-option').forEach(opt => {
                    opt.classList.remove('selected');
                });
                
                // Add selected class to clicked option
                option.classList.add('selected');
                
                // Update start button
                startButton.disabled = false;
                startButton.textContent = `Play as ${option.querySelector('h3').textContent}`;
                
                // Store selected class
                state.selectedClass = option.getAttribute('data-class');
                console.log('Selected class:', state.selectedClass);
                
                // Play select sound
                if (sounds.select) {
                    sounds.select.currentTime = 0;
                    sounds.select.volume = 0.3;
                    sounds.select.play().catch(e => console.log('Select sound failed:', e));
                }
            });
        });
        
        // Set up start button
        startButton.addEventListener('click', startGame);
        
        // Set canvas size
        resizeCanvas();
        
        // Initialize empty player
        state.player = null;
        
        // Initialize tokens
        state.tokens = [];
        
        // Initialize particles
        state.particles = [];
        
        // Initialize keys
        state.keys = {};
        
        console.log('Game initialized');
    } catch (error) {
        console.error('Error initializing game:', error);
        alert('Failed to initialize the game. Please check the console for details.');
    }
}

// Start the game
function startGame() {
    try {
        if (!state.selectedClass) {
            console.error('No class selected');
            alert('Please select a class first!');
            return;
        }
        
        console.log('Starting game with class:', state.selectedClass);
        
        // Hide start screen
        if (startScreen) {
            startScreen.classList.add('hidden');
        }
        
        // Initialize player with selected class
        const classConfig = config.player.classes[state.selectedClass];
        if (!classConfig) {
            console.error('Invalid class configuration for:', state.selectedClass);
            return;
        }
        
        // Set up player state
        state.player = {
            x: canvas.width / 2,
            y: canvas.height / 2,
            size: 20 * (classConfig.sizeMultiplier || 1),
            speed: config.player.baseSpeed * (classConfig.speedMultiplier || 1),
            score: 0,
            level: 1,
            class: state.selectedClass,
            className: classConfig.name || state.selectedClass,
            growthRate: classConfig.growthRate || 0.5,
            color: classConfig.color || '#3498db',
            language: 'None',
            lastTokenCollected: null
        };
        
        // Generate initial tokens
        generateTokens();
        
        // Update UI
        updateUI();
        
        // Play background music if available
        if (sounds.background) {
            try {
                sounds.background.loop = true;
                sounds.background.volume = 0.3;
                sounds.background.play().catch(e => console.log('Background music failed:', e));
            } catch (e) {
                console.error('Error playing background music:', e);
            }
        }
        
        // Update game state
        state.gameStarted = true;
        state.currentState = 'PLAYING';
        
        // Start game loop if not already running
        if (!state.animationId) {
            state.lastTime = performance.now();
            state.animationId = requestAnimationFrame(gameLoop);
        }
        
        console.log('Game started with player:', state.player);
    } catch (error) {
        console.error('Error in startGame:', error);
        alert('Failed to start the game. Please check the console for details.');
    }
    // Generate tokens
    generateTokens();
    
    // Set game state to playing
    state.currentState = GAME_STATES.PLAYING;
    state.gameStarted = true;
    
    // Update UI
    updateUI();
    
    // Play background music
    if (sounds.background) {
        sounds.background.loop = true;
        sounds.background.volume = 0.5;
        sounds.background.play().catch(e => console.log('Audio play failed:', e));
    }
    
    // Play select sound
    if (sounds.select) {
        sounds.select.play().catch(e => console.log('Audio play failed:', e));
    }
    
    console.log('Game started with class:', state.selectedClass, 'Player:', state.player);
}

// Game loop with delta time
function gameLoop(timestamp) {
    // Calculate delta time
    if (!state.lastTime) state.lastTime = timestamp;
    const deltaTime = Math.min(timestamp - state.lastTime, 1000); // Cap at 1 second
    state.lastTime = timestamp;
    
    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Update game state if playing
    if (state.currentState === GAME_STATES.PLAYING) {
        update(deltaTime);
    }
    
    // Render
    render();
    
    // Draw particles on top of everything
    if (state.currentState === GAME_STATES.PLAYING) {
        drawParticles();
    }
    
    // Next frame
    state.animationId = requestAnimationFrame(gameLoop);
}

// Update game state
function update(deltaTime) {
    if (state.currentState !== GAME_STATES.PLAYING) return;
    
    try {
        // Convert deltaTime from ms to seconds
        const dt = deltaTime / 1000;
        
        // Update player position based on input
        const moveSpeed = (state.player.speed || 100) * dt; // Default speed if not set
        
        // Calculate movement vector
        let moveX = 0;
        let moveY = 0;
        
        if (state.keys['ArrowUp'] || state.keys['w']) moveY -= 1;
        if (state.keys['ArrowDown'] || state.keys['s']) moveY += 1;
        if (state.keys['ArrowLeft'] || state.keys['a']) moveX -= 1;
        if (state.keys['ArrowRight'] || state.keys['d']) moveX += 1;
        
        // Normalize diagonal movement
        if (moveX !== 0 || moveY !== 0) {
            const length = Math.sqrt(moveX * moveX + moveY * moveY);
            moveX = (moveX / length) * moveSpeed;
            moveY = (moveY / length) * moveSpeed;
            
            // Update player position with bounds checking
            const newX = state.player.x + moveX;
            const newY = state.player.y + moveY;
            const playerSize = state.player.size || 20;
            
            state.player.x = Math.max(playerSize, Math.min(canvas.width - playerSize, newX));
            state.player.y = Math.max(playerSize, Math.min(canvas.height - playerSize, newY));
        }
        
        // Check for collisions
        checkCollisions();
        
        // Update particles if they exist
        if (state.particles && state.particles.length > 0) {
            updateParticles(dt);
        }
        
    } catch (error) {
        console.error('Error in update loop:', error);
    }
}

// Render the game
function render() {
    // Clear the canvas with a background color
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw tokens first (so player appears on top)
    state.tokens.forEach(token => {
        if (!token) return;
        
        // Draw token glow
        const gradient = ctx.createRadialGradient(
            token.x, token.y, 0,
            token.x, token.y, token.size * 1.5
        );
        gradient.addColorStop(0, token.color);
        gradient.addColorStop(1, 'transparent');
        
        ctx.beginPath();
        ctx.arc(token.x, token.y, token.size * 1.5, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
        
        // Draw token
        ctx.beginPath();
        ctx.arc(token.x, token.y, token.size, 0, Math.PI * 2);
        ctx.fillStyle = token.color;
        ctx.fill();
        
        // Draw token symbol
        if (token.symbol) {
            ctx.fillStyle = '#fff';
            ctx.font = `${Math.max(12, token.size)}px 'Courier New', monospace`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(token.symbol, token.x, token.y);
        }
    });
    
    // Draw player with glow effect
    if (state.player && state.currentState === GAME_STATES.PLAYING) {
        // Player glow
        const gradient = ctx.createRadialGradient(
            state.player.x, state.player.y, 0,
            state.player.x, state.player.y, state.player.size * 1.5
        );
        gradient.addColorStop(0, state.player.color);
        gradient.addColorStop(1, 'transparent');
        
        ctx.beginPath();
        ctx.arc(state.player.x, state.player.y, state.player.size * 1.5, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
        
        // Player circle
        ctx.beginPath();
        ctx.arc(state.player.x, state.player.y, state.player.size, 0, Math.PI * 2);
        ctx.fillStyle = state.player.color;
        ctx.fill();
        
        // Player symbol
        if (state.player.symbol) {
            ctx.fillStyle = state.player.symbolColor || '#ffffff';
            const fontSize = Math.max(16, state.player.size);
            ctx.font = `bold ${fontSize}px 'Courier New', monospace`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(state.player.symbol, state.player.x, state.player.y);
        }
    }
    
    // Draw particles
    if (state.particles && state.particles.length > 0) {
        drawParticles();
    }
    
    // Draw UI elements
    if (state.currentState === GAME_STATES.MENU) {
        // Draw menu elements if needed
    } else if (state.currentState === GAME_STATES.PLAYING) {
        updateUI();
    } else if (state.currentState === GAME_STATES.GAME_OVER) {
        // Draw game over screen if needed
    }
}

// Generate random tokens
function generateTokens() {
    try {
        const count = config.tokens?.count || 20; // Default to 20 tokens if not specified
        state.tokens = [];
        
        // Clear any existing tokens
        state.tokens.length = 0;
        
        // Generate new tokens
        for (let i = 0; i < count; i++) {
            generateToken();
        }
        
        console.log(`Generated ${state.tokens.length} tokens`);
        return state.tokens;
    } catch (error) {
        console.error('Error generating tokens:', error);
        state.tokens = [];
        return [];
    }
}

// Check for collisions
function checkCollisions() {
    if (!state.player || !state.tokens) return;
    
    try {
        // Check token collisions
        for (let i = state.tokens.length - 1; i >= 0; i--) {
            const token = state.tokens[i];
            if (!token) {
                state.tokens.splice(i, 1);
                continue;
            }
            
            const dx = state.player.x - token.x;
            const dy = state.player.y - token.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const collisionDistance = (state.player.size || 20) + (token.size || 10);
            
            if (distance < collisionDistance) {
                // Player collected token
                const growthAmount = (token.growthValue || 1) * (state.player.growthRate || 0.5);
                state.player.size = Math.min(100, (state.player.size || 20) + growthAmount);
                state.player.score += token.points || 10;
                
                // Play collect sound if available
                if (sounds.collect) {
                    try {
                        sounds.collect.currentTime = 0;
                        sounds.collect.play().catch(e => console.log('Audio play failed:', e));
                    } catch (e) {
                        console.log('Error playing collect sound:', e);
                    }
                }
                
                // Create particle effect
                createParticles(token.x, token.y, token.color || '#ffffff', 15);
                
                // Remove the collected token
                state.tokens.splice(i, 1);
                
                // Change language occasionally
                if (Math.random() < 0.1) {
                    state.player.language = config.languages[
                        Math.floor(Math.random() * config.languages.length)
                    ];
                }
                
                // Generate a new token to replace the collected one
                generateToken();
                
                // Check for level up
                checkLevelUp();
                
                // Update UI
                updateUI();
            }
        }
        
        // Add new tokens if needed
        while (state.tokens.length < (config.tokens?.count || 10)) {
            generateToken();
        }
    } catch (error) {
        console.error('Error in checkCollisions:', error);
    }
}

// Check if player should level up
function checkLevelUp() {
    if (!state.player) return;
    
    const sizeThresholds = [30, 50, 75];
    const currentLevel = state.player.level || 1;
    
    if (currentLevel <= sizeThresholds.length && state.player.size >= sizeThresholds[currentLevel - 1]) {
        state.player.level = currentLevel + 1;
        
        // Play level up sound if available
        if (sounds.levelUp) {
            try {
                sounds.levelUp.currentTime = 0;
                sounds.levelUp.play().catch(e => console.log('Audio play failed:', e));
            } catch (e) {
                console.log('Error playing level up sound:', e);
            }
        }
        
        // Visual effect for level up
        createParticles(state.player.x, state.player.y, state.player.color || '#ffffff', 30);
    }
}

// Update UI elements with player statistics
function updateUI() {
    try {
        if (!state.player) {
            console.warn('Cannot update UI: Player state not available');
            return;
        }
        
        // Update score display
        if (scoreElement) {
            scoreElement.textContent = Math.floor(state.player.size || 0);
        }
        
        // Update language display
        if (languageElement) {
            languageElement.textContent = state.player.language || 'None';
        }
        
        // Update class name display
        if (classNameElement) {
            classNameElement.textContent = state.player.className || state.player.class || '-';
            
            // Add class-based styling
            if (state.player.class) {
                classNameElement.className = state.player.class.toLowerCase();
            }
        }
        
        // Update speed display
        if (speedElement) {
            speedElement.textContent = state.player.speed ? state.player.speed.toFixed(1) : '0.0';
        }
        
        // Update level display if it exists
        const levelElement = document.getElementById('level');
        if (levelElement) {
            levelElement.textContent = state.player.level || 1;
        }
        
        // Update score display if it exists
        const scoreDisplayElement = document.getElementById('score-display');
        if (scoreDisplayElement) {
            scoreDisplayElement.textContent = Math.floor(state.player.score || 0);
        }
        
    } catch (error) {
        console.error('Error updating UI:', error);
    }
}

// Generate a single token
function generateToken() {
    try {
        const minSize = config.tokens?.minSize || 5;
        const maxSize = config.tokens?.maxSize || 15;
        const colors = config.tokens?.colors || ['#ff5555', '#55ff55', '#5555ff', '#ffff55', '#ff55ff', '#55ffff'];
        const languages = config.languages || ['Python', 'JavaScript', 'Java', 'C++', 'Ruby', 'Go', 'Rust', 'TypeScript'];
        
        const size = minSize + Math.random() * (maxSize - minSize);
        const x = size + Math.random() * (canvas.width - size * 2);
        const y = size + Math.random() * (canvas.height - size * 2);
        const color = colors[Math.floor(Math.random() * colors.length)];
        const language = languages[Math.floor(Math.random() * languages.length)];
        
        // Determine token value based on size
        const points = Math.ceil(size);
        const growthValue = size / 10; // Larger tokens give more growth
        
        const token = {
            x,
            y,
            size,
            color,
            language,
            points,
            growthValue,
            symbol: '</>', // Default symbol, can be customized per language
            symbolColor: '#ffffff'
        };
        
        state.tokens.push(token);
        return token;
    } catch (error) {
        console.error('Error generating token:', error);
        return null;
    }
}

// Handle window resize
function resizeCanvas() {
    try {
        // Get the container or use window dimensions
        const container = document.getElementById('gameContainer') || document.body;
        const containerWidth = container.clientWidth;
        const containerHeight = container.clientHeight;
        
        // Set canvas dimensions to match container
        canvas.width = containerWidth;
        canvas.height = containerHeight;
        
        // Update config with new dimensions
        config.width = canvas.width;
        config.height = canvas.height;
        
        // If game is in progress, ensure player stays within bounds
        if (state.player) {
            state.player.x = Math.min(Math.max(state.player.size, state.player.x), canvas.width - state.player.size);
            state.player.y = Math.min(Math.max(state.player.size, state.player.y), canvas.height - state.player.size);
        }
        
        console.log(`Canvas resized to ${canvas.width}x${canvas.height}`);
        return { width: canvas.width, height: canvas.height };
    } catch (error) {
        console.error('Error resizing canvas:', error);
        // Fallback to window dimensions
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        config.width = canvas.width;
        config.height = canvas.height;
        return { width: canvas.width, height: canvas.height };
    }
}

// Handle keyboard input
function handleKeyDown(e) {
    state.keys[e.key] = true;
    
    // Pause game with Escape key
    if (e.key === 'Escape') {
        togglePause();
    }
    
    // Prevent arrow keys from scrolling the page
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(e.key)) {
        e.preventDefault();
    }
}

function handleKeyUp(e) {
    state.keys[e.key] = false;
}

// Toggle pause state
function togglePause() {
    if (state.currentState === GAME_STATES.PLAYING) {
        state.currentState = GAME_STATES.PAUSED;
        // Show pause menu or overlay
    } else if (state.currentState === GAME_STATES.PAUSED) {
        state.currentState = GAME_STATES.PLAYING;
        // Hide pause menu or overlay
    }
}

// Create particle effect
function createParticles(x, y, color, count) {
    for (let i = 0; i < count; i++) {
        const angle = Math.random() * Math.PI * 2;
        const speed = 1 + Math.random() * 3;
        const size = 1 + Math.random() * 3;
        const lifetime = 30 + Math.random() * 30;
        
        state.particles.push({
            x: x,
            y: y,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            size: size,
            color: color,
            lifetime: lifetime,
            maxLifetime: lifetime
        });
    }
}

// Update particles
function updateParticles(deltaTime) {
    for (let i = state.particles.length - 1; i >= 0; i--) {
        const p = state.particles[i];
        p.x += p.vx * (deltaTime / 16.67);
        p.y += p.vy * (deltaTime / 16.67);
        p.lifetime--;
        
        if (p.lifetime <= 0) {
            state.particles.splice(i, 1);
        }
    }
}

// Draw particles
function drawParticles() {
    state.particles.forEach(p => {
        const alpha = p.lifetime / p.maxLifetime;
        ctx.globalAlpha = alpha * 0.7;
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size * alpha, 0, Math.PI * 2);
        ctx.fill();
    });
    ctx.globalAlpha = 1;
}

// Reset game state
function resetGame() {
    // Stop all sounds
    Object.values(sounds).forEach(sound => {
        if (!sound.paused) {
            sound.pause();
            sound.currentTime = 0;
        }
    });
    
    // Clear particles
    state.particles = [];
    // Reset player
    state.player = {
        ...state.player,
        x: config.width / 2,
        y: config.height / 2,
        score: 0,
        level: 1
    };
    
    // Reset tokens
    generateTokens();
    
    // Reset game state
    state.currentState = GAME_STATES.PLAYING;
    
    // Start game loop if not already running
    if (!state.animationId) {
        state.lastTime = performance.now();
        state.accumulator = 0;
        gameLoop(state.lastTime);
    }
}

// Start the game
function startGame() {
    try {
        console.log('Starting game with selected class:', selectedClass);
        
        if (!selectedClass) {
            console.error('No class selected');
            alert('Please select a class first!');
            return;
        }
        
        // Hide start screen
        if (startScreen) {
            startScreen.classList.add('hidden');
        }
        
        // Initialize player with selected class
        const classConfig = config.player.classes[selectedClass];
        if (!classConfig) {
            console.error('Invalid class configuration for:', selectedClass);
            return;
        }
        
        // Set up player state
        state.player = {
            x: canvas.width / 2,
            y: canvas.height / 2,
            size: 20 * (classConfig.sizeMultiplier || 1),
            speed: config.player.baseSpeed * (classConfig.speedMultiplier || 1),
            score: 0,
            level: 1,
            class: selectedClass,
            className: classConfig.name || selectedClass,
            growthRate: classConfig.growthRate || 0.5,
            color: classConfig.color || '#3498db',
            language: 'None',
            lastTokenCollected: null
        };
        
        // Generate initial tokens
        generateTokens();
        
        // Update UI
        updateUI();
        
        // Play start sound if available
        if (sounds.start) {
            try {
                sounds.start.currentTime = 0;
                sounds.start.play().catch(e => console.log('Start sound failed:', e));
            } catch (e) {
                console.error('Error playing start sound:', e);
            }
        }
        
        // Start game loop
        lastTime = performance.now();
        isPaused = false;
        state.gameStarted = true;
        
        console.log('Game started with player:', state.player);
        requestAnimationFrame(gameLoop);
        
    } catch (error) {
        console.error('Error starting game:', error);
        alert('Failed to start the game. Please check the console for details.');
    }
}

// Initialize the game when the window loads
window.addEventListener('load', () => {
    console.log('Window loaded, initializing game...');
    
    try {
        // Initialize the game
        init();
        
        // Add keyboard event listeners
        window.addEventListener('keydown', handleKeyDown);
        window.addEventListener('keyup', handleKeyUp);
        
        // Set up window resize handler
        window.addEventListener('resize', resizeCanvas);
        
        // Initial canvas resize
        resizeCanvas();
        
        console.log('Game initialization complete');
    } catch (error) {
        console.error('Error during game initialization:', error);
        alert('Failed to initialize the game. Please check the console for details.');
    }
});
