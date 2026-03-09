document.addEventListener('DOMContentLoaded', () => {
    // --- Configuration ---
    const SCREENS = {
        HOME: 'home-screen',
        ROOM_SELECTION: 'room-selection-screen',
        ROOM_DETAIL: 'room-detail-screen',
        RESERVATION: 'reservation-screen',
        ROOM_CODE: 'room-code-screen',
        STAFF_AUTH: 'staff-auth-screen',
        STAFF_WELCOME: 'staff-welcome-screen',
        SCANNER: 'scanner-screen',
        PAYMENT_SELECTION: 'payment-selection-screen',
        PAYMENT_AUTO: 'payment-auto-screen',
        PAYMENT_MANUAL: 'payment-manual-screen',
        TERMS: 'terms-screen',
        FINAL: 'final-screen',
        STAFF_WAITING: 'staff-waiting-screen'
    };

    // --- Kiosk Configuration ---
    const API_URL = 'http://' + window.location.hostname + ':8000'; // API Port
    const urlParams = new URLSearchParams(window.location.search);
    const KIOSK_MODE = urlParams.get('mode') || 'entrada'; // entrada o salida
    document.body.classList.add('mode-' + KIOSK_MODE);

    // --- Sound Controller ---
    // The user will create 'assets/sounds/' and place files there.
    const AUDIO_PATH = 'assets/sounds/';
    const SOUNDS = {
        tap: new Audio(AUDIO_PATH + 'tap.mp3'),
        transition: new Audio(AUDIO_PATH + 'transition.mp3'),
        wrong: new Audio(AUDIO_PATH + 'wrong.mp3'),
        correct: new Audio(AUDIO_PATH + 'correct.mp3'),
        celebration: new Audio(AUDIO_PATH + 'celebration.mp3'),
        continue: new Audio(AUDIO_PATH + 'continue.mp3')
    };

    // Preload sounds
    Object.values(SOUNDS).forEach(audio => {
        audio.load();
        audio.volume = 0.5; // Default volume
    });

    function playSound(name) {
        if (SOUNDS[name]) {
            const sound = SOUNDS[name];
            sound.currentTime = 0; // Reset to start
            // Clone for overlapping taps if needed
            sound.play().catch(e => console.warn('Audio play failed (interaction needed?):', e));
        }
    }
    
    // Data holders
    let ROOMS_DATA = [];
    let bcvRate = 0;
    
    const CODE_LENGTH = 5;
    const MOCK_VALID_CODE = '12345'; // Simple mock
    let currentCode = '';
    let isErrorCode = false; 
    const INACTIVITY_POPUP_TIME = 120000; // 2 minutes
    const INACTIVITY_TOTAL_TIME = 240000; // 4 minutes
    const INACTIVITY_EXTENSION_TIME = 180000; // 3 minutes extension
    
    let idleTimer = null;
    let selectedRoom = null; 
    let totalIdleTimer = null;
    let countdownInterval = null;
    let isPopupActive = false;
    let currentTotalTimeout = INACTIVITY_TOTAL_TIME;
    let screenHistory = [SCREENS.HOME];

    // --- DOM Elements ---
    const screens = Object.values(SCREENS).map(id => document.getElementById(id));
    
    // Home Buttons
    const btnWalkin = document.getElementById('btn-walkin');
    const btnReservation = document.getElementById('btn-reservation');
    const btnStaying = document.getElementById('btn-staying');
    const btnStaff = document.getElementById('btn-staff');
    const btnHomeConfirm = document.getElementById('btn-home-confirm');

    // Room Selection Elements
    const roomListContainer = document.querySelector('.room-list-container');
    
    // Room Detail Elements
    const btnRoomConfirm = document.getElementById('btn-room-confirm');
    const detailName = document.getElementById('detail-room-name');
    const detailCapacity = document.getElementById('detail-capacity');
    const detailPrice = document.getElementById('detail-price');
    const detailVideoText = document.getElementById('detail-video-text');

    // Reservation Elements
    const reservationCodeDigits = document.querySelectorAll('#reservation-screen .code-digit');
    const reservationFeedback = document.getElementById('reservation-feedback');

    // Room Code Elements
    const roomCodeDigits = document.querySelectorAll('#room-code-screen .code-digit');
    const roomCodeFeedback = document.getElementById('room-code-feedback');

    // Scanner Elements
    const btnScanContinue = document.getElementById('btn-scan-continue');

    // Payment Selection Elements
    const paymentModeAuto = document.getElementById('mode-auto');
    const paymentModeManual = document.getElementById('mode-manual');
    const paymentRefDigits = document.querySelectorAll('#payment-ref-display .code-digit');
    const btnConfirmAutoPay = document.getElementById('btn-confirm-auto-payment');
    
    let currentRefCode = '';
    const REF_CODE_LENGTH = 5;

    // Terms Elements
    const btnTermsAccept = document.getElementById('btn-terms-accept');

    // Final Elements
    const btnFinish = document.getElementById('btn-finish');

    // Inactivity Popup Elements
    const inactivityPopup = document.getElementById('inactivity-popup');
    const btnStayHere = document.getElementById('btn-stay-here');
    const countdownDisplay = document.getElementById('popup-countdown');

    // Staff Auth Elements
    const scannedStaffList = document.getElementById('scanned-staff-list');
    const btnStaffContinue = document.getElementById('btn-staff-continue');
    const staffWelcomeNames = document.getElementById('staff-welcome-names');
    const staffQuoteContainer = document.getElementById('staff-quote-container');
    const btnStaffFinish = document.getElementById('btn-staff-finish');
    const btnStaffWaitingBack = document.getElementById('btn-staff-waiting-back');
    const btnCheckout = document.getElementById('btn-checkout');

    let scannedStaff = []; // Array of {nombre, cargo}
    const STAFF_NAMES = ["Carlos Pérez", "María García", "Juan Rodríguez", "Elena Sánchez", "Roberto Díaz"];

    const CORPORATE_QUOTES = [
        { text: "El único modo de hacer un gran trabajo es amar lo que haces.", author: "Steve Jobs" },
        { text: "El trabajo en equipo divide el trabajo y multiplica los resultados.", author: "Anónimo" },
        { text: "La excelencia no es un acto, es un hábito.", author: "Aristóteles" },
        { text: "Tu actitud, no tu aptitud, determinará tu altitud.", author: "Zig Ziglar" },
        { text: "El éxito es la suma de pequeños esfuerzos repetidos día tras día.", author: "Robert Collier" },
        { text: "La mejor forma de predecir el futuro es creándolo.", author: "Peter Drucker" },
        { text: "Solo hay una forma de evitar las críticas: no hacer nada, no decir nada y no ser nada.", author: "Aristóteles" },
        { text: "El talento gana partidos, pero el trabajo en equipo y la inteligencia ganan campeonatos.", author: "Michael Jordan" },
        { text: "No busques los errores, busca un remedio.", author: "Henry Ford" },
        { text: "Haz de cada día tu obra maestra.", author: "John Wooden" }
    ];

    let selectedHomeOption = null;

    // --- Persistence Logic ---
    function saveAppState() {
        const state = {
            selectedHomeOption,
            selectedRoom,
            currentCode,
            currentRefCode,
            scannedStaff,
            screenHistory,
            lastUpdate: Date.now()
        };
        localStorage.setItem('kiosk_app_state', JSON.stringify(state));
    }

    async function loadAppState() {
        const saved = localStorage.getItem('kiosk_app_state');
        if (!saved) return;
        
        try {
            const state = JSON.parse(saved);
            // Check if state is old (e.g. more than 30 mins)
            if (Date.now() - state.lastUpdate > 1800000) {
                localStorage.removeItem('kiosk_app_state');
                return;
            }

            // Restore data
            selectedHomeOption = state.selectedHomeOption;
            selectedRoom = state.selectedRoom;
            currentCode = state.currentCode;
            currentRefCode = state.currentRefCode;
            scannedStaff = state.scannedStaff || [];
            screenHistory = state.screenHistory || [SCREENS.HOME];

            // Trigger UI updates
            if (selectedHomeOption) {
                selectHomeOption(selectedHomeOption);
            }
            
            if (screenHistory.length > 0) {
                const targetScreen = screenHistory[screenHistory.length - 1];
                
                // Special rendering if needed for specific screens
                if (targetScreen === SCREENS.ROOM_SELECTION) {
                    await fetchInitialData();
                    renderRoomList();
                } else if (targetScreen === SCREENS.ROOM_DETAIL && selectedRoom) {
                    renderRoomDetail();
                } else if (targetScreen === SCREENS.RESERVATION) {
                    updateCodeDisplay('reservation');
                } else if (targetScreen === SCREENS.ROOM_CODE) {
                    updateCodeDisplay('room');
                } else if (targetScreen === SCREENS.STAFF_AUTH) {
                    // Re-render scanned staff list
                    scannedStaff.forEach(s => {
                         const placeholder = document.getElementById('rfid-placeholder');
                         if (placeholder) placeholder.remove();
                         const item = document.createElement('div');
                         item.className = 'staff-item';
                         item.innerHTML = `<div style="display:flex; flex-direction:column;"><span style="font-weight:800;">${s.nombre}</span><span style="font-size:0.75em; opacity:0.8; text-transform:uppercase;">${s.cargo}</span></div>`;
                         scannedStaffList.appendChild(item);
                    });
                    if (scannedStaff.length > 0) btnStaffContinue.classList.remove('hidden');
                } else if (targetScreen === SCREENS.PAYMENT_AUTO) {
                    updateRefDisplay();
                }

                // Important: Jump to the screen without adding to history again
                const screens = document.querySelectorAll('.screen');
                screens.forEach(s => s.classList.add('hidden'));
                const active = document.getElementById(targetScreen);
                if (active) {
                    active.classList.remove('hidden');
                    active.classList.add('active');
                }
            }
        } catch (e) {
            console.error("Error loading app state:", e);
            localStorage.removeItem('kiosk_app_state');
        }
    }

    // --- Navigation Functions ---
    function navigateTo(screenId, direction = 'forward') {
        const currentScreen = document.querySelector('.screen.active');
        const nextScreen = document.getElementById(screenId);

        if (currentScreen === nextScreen) return;

        // Play sounds based on destination
        if (screenId === SCREENS.FINAL) {
            playSound('celebration');
            // Wait 1s and trigger confetti
            setTimeout(() => {
                const finalScreen = document.getElementById(SCREENS.FINAL);
                if (finalScreen && finalScreen.classList.contains('active')) {
                    shootConfetti();
                }
            }, 1000);
        } else {
            playSound('transition');
        }

        // Cleanup previous classes just in case
        screens.forEach(s => {
            s.classList.remove('navigate-in', 'navigate-out', 'navigate-back-in', 'navigate-back-out');
        });

        if (currentScreen) {
            currentScreen.classList.remove('active');
            // Add exit animation
            if (direction === 'forward') {
                currentScreen.classList.add('navigate-out');
            } else {
                currentScreen.classList.add('navigate-back-out');
            }

            // Clean up after animation
            setTimeout(() => {
                currentScreen.classList.remove('navigate-out', 'navigate-back-out');
                currentScreen.classList.add('hidden');
            }, 600); // Match CSS animation duration
        }

        // Prepare next screen
        nextScreen.classList.remove('hidden');
        nextScreen.classList.add('active');
        
        // Add enter animation
        if (direction === 'forward') {
            nextScreen.classList.add('navigate-in');
        } else {
            nextScreen.classList.add('navigate-back-in');
        }

        // Cleanup enter classes
        setTimeout(() => {
            nextScreen.classList.remove('navigate-in', 'navigate-back-in');
        }, 600);

        if (direction === 'forward') {
            screenHistory.push(screenId);
        }
        
        saveAppState();
        resetIdleTimer();
    }

    function navigateBack() {
        if (screenHistory.length > 1) {
            screenHistory.pop(); // Remove current
            const prevScreenId = screenHistory[screenHistory.length - 1];
            // Since we're going back, we don't want navigateTo to push again
            // So we use a modified navigateTo or just call it carefully
            const currentScreen = document.querySelector('.screen.active');
            const nextScreen = document.getElementById(prevScreenId);
            
            if (currentScreen) {
                currentScreen.classList.remove('active');
                currentScreen.classList.add('navigate-back-out');
                setTimeout(() => {
                    currentScreen.classList.remove('navigate-back-out');
                    currentScreen.classList.add('hidden');
                }, 600);
            }
            
            nextScreen.classList.remove('hidden');
            nextScreen.classList.add('active', 'navigate-back-in');
            setTimeout(() => {
                nextScreen.classList.remove('navigate-back-in');
            }, 600);
            
            resetIdleTimer();
            saveAppState();
        } else {
            resetApp();
        }
    }

    function resetApp() {
        currentCode = '';
        currentRefCode = '';
        scannedStaff = [];
        selectedHomeOption = null;
        selectedRoom = null;
        updateCodeDisplay('reservation');
        updateCodeDisplay('room');
        clearFeedback('reservation');
        clearFeedback('room');

        // Clear staff list display
        if (scannedStaffList) {
            scannedStaffList.innerHTML = `
                <div id="rfid-placeholder" class="rfid-placeholder-content">
                    <div class="rfid-illustration">
                        <div class="rfid-scanner">
                            <div class="rfid-wave"></div>
                            <div class="rfid-wave"></div>
                            <div class="rfid-wave"></div>
                            <img src="assets/icons/shield.svg" width="80" height="80" class="rfid-icon">
                        </div>
                    </div>
                    <div class="rfid-text">
                        <p class="main-instruction">Aproxime su tarjeta al lector</p>
                        <p class="sub-instruction">El sistema registrará su ingreso automáticamente</p>
                    </div>
                </div>`;
            btnStaffContinue.classList.add('hidden');
        }
        
        // Reset home buttons
        btnWalkin.classList.remove('selected');
        btnReservation.classList.remove('selected');
        btnStaying.classList.remove('selected');
        btnStaff.classList.remove('selected');
        btnHomeConfirm.classList.add('hidden');
        
        screenHistory = [SCREENS.HOME];
        selectedRoom = null;
        selectedHomeOption = null;
        currentCode = '';
        currentRefCode = '';
        scannedStaff = [];
        
        localStorage.removeItem('kiosk_app_state');

        // Use 'back' animation when resetting to home
        navigateTo(SCREENS.HOME, 'back');
    }

    function selectHomeOption(option) {
        playSound('tap');
        selectedHomeOption = option;
        
        // Update selection UI
        btnWalkin.classList.toggle('selected', option === 'walkin');
        btnReservation.classList.toggle('selected', option === 'reservation');
        btnStaying.classList.toggle('selected', option === 'staying');
        btnStaff.classList.toggle('selected', option === 'staff');
        if (btnCheckout) btnCheckout.classList.toggle('selected', option === 'checkout');
        
        // Show confirm button
        btnHomeConfirm.classList.remove('hidden');
        saveAppState();
    }

    async function confirmHomeSelection() {
        playSound('continue');
        if (selectedHomeOption === 'walkin') {
            await fetchInitialData(); // Refrescar antes de mostrar
            renderRoomList();
            navigateTo(SCREENS.ROOM_SELECTION);
        } else if (selectedHomeOption === 'reservation') {
            navigateTo(SCREENS.RESERVATION);
        } else if (selectedHomeOption === 'staying') {
            navigateTo(SCREENS.ROOM_CODE);
        } else if (selectedHomeOption === 'staff') {
            navigateTo(SCREENS.STAFF_AUTH);
        } else if (selectedHomeOption === 'checkout') {
            // Simple checkout flow
            navigateTo(SCREENS.FINAL);
        }
    }

    function handleWalkinAction() {
        console.log('Action: Deseo una habitación');
        const existingMsg = document.getElementById('walkin-feedback');
        if (existingMsg) existingMsg.remove();

        const msg = document.createElement('div');
        msg.id = 'walkin-feedback';
        msg.textContent = 'Opción Registrada';
        msg.style.cssText = 'position: fixed; top: 20%; left: 50%; transform: translateX(-50%); background: #fbc02d; color: #1e265c; padding: 1.5rem 3rem; border-radius: 50px; font-weight: 800; font-size: 1.5rem; animation: popup 0.3s forwards; pointer-events: none; z-index: 1000; box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 2px solid white;';
        document.body.appendChild(msg);

        setTimeout(() => {
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500);
        }, 2000);
    }

    async function fetchInitialData() {
        try {
            // 1. Fetch Rooms (Free ones)
            const roomRes = await fetch(`${API_URL}/api/habitaciones`);
            const rooms = await roomRes.json();
            const freeRooms = rooms.filter(r => r.estado_actual === 'Libre');
            
            // Group rooms by type
            const grouped = {};
            freeRooms.forEach(r => {
                if (!grouped[r.tipo]) {
                    grouped[r.tipo] = {
                        id: r.tipo, // Use type as ID for selection
                        name: r.tipo,
                        type: r.tipo,
                        capacity: r.capacidad || 2,
                        priceUSD: r.precio_hospedaje,
                        stars: r.tipo.toLowerCase().includes('vip') ? 5 : (r.tipo.toLowerCase().includes('suite') ? 4 : 3),
                        video: `video_${r.tipo.toLowerCase()}.mp4`,
                        availableRooms: []
                    };
                }
                grouped[r.tipo].availableRooms.push(r);
            });
            
            ROOMS_DATA = Object.values(grouped);

            // 2. Fetch BCV Rate
            const bcvRes = await fetch(`${API_URL}/api/configuracion/settings/bcv`);
            const bcvData = await bcvRes.json();
            bcvRate = parseFloat(bcvData.valor) || 0;
            
            console.log(`Loaded ${ROOMS_DATA.length} available rooms. BCV Rate: ${bcvRate}`);
        } catch (e) {
            console.error("Error fetching initial data:", e);
        }
    }

    function formatBS(usdAmount) {
        if (!bcvRate) return "--- Bs";
        return (usdAmount * bcvRate).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " Bs";
    }

    function formatUSD(usdAmount) {
        return "$" + usdAmount.toFixed(2);
    }

    // --- Room Selection Logic ---
    function renderRoomList() {
        roomListContainer.innerHTML = '';
        if (ROOMS_DATA.length === 0) {
            roomListContainer.innerHTML = `<p style="color: white; font-size: 1.5rem; text-align: center; margin-top: 2rem;">No hay habitaciones disponibles en este momento.</p>`;
            return;
        }
        ROOMS_DATA.forEach(roomType => {
            const card = document.createElement('div');
            card.className = 'room-card';
            card.onclick = () => selectRoom(roomType.id);
            
            card.innerHTML = `
                <div class="room-card-info">
                    <h3 style="text-transform: uppercase; font-weight: 800;">${roomType.name}</h3>
                    <p style="font-size: 0.9rem; color: #666;">Desde ${formatUSD(roomType.priceUSD)} / ${formatBS(roomType.priceUSD)}</p>
                </div>
                <div class="room-card-metrics">
                    <div class="metric-item stars">
                        <img src="assets/icons/star_filled.svg" width="20" height="20" class="star-icon">
                        <span class="metric-value">${roomType.stars}</span>
                    </div>
                    <div class="metric-item capacity">
                        <img src="assets/icons/capacidad.svg" width="20" height="20" class="capacity-icon">
                        <span class="metric-value">${roomType.capacity}</span>
                    </div>
                </div>
            `;
            roomListContainer.appendChild(card);
        });
    }

    function selectRoom(typeId) {
        playSound('tap');
        selectedRoom = ROOMS_DATA.find(r => r.id === typeId);
        if (!selectedRoom) return;

        // Picking a random actual room from this type for internal tracking
        const actualRoom = selectedRoom.availableRooms[Math.floor(Math.random() * selectedRoom.availableRooms.length)];
        selectedRoom.assignedId = actualRoom.id;
        selectedRoom.assignedNumber = actualRoom.numero;

        renderRoomDetail();
        navigateTo(SCREENS.ROOM_DETAIL);
        saveAppState();
    }

    function renderRoomDetail() {
        if (!selectedRoom) return;
        // Populate details
        detailName.textContent = selectedRoom.name;
        detailCapacity.textContent = `${selectedRoom.capacity} Personas`;
        detailPrice.innerHTML = `${formatUSD(selectedRoom.priceUSD)} <span style="font-size: 0.7em; opacity: 0.8; margin-left:10px;">/ ${formatBS(selectedRoom.priceUSD)}</span>`;
        // Inventario simulado
        const inventoryEl = document.getElementById('detail-inventory');
        if (inventoryEl) {
            inventoryEl.textContent = "Aire Acondicionado • Wi-Fi Alta Velocidad • TV Smart • Baño Privado • Amenities";
        }
        
        detailVideoText.textContent = `Video de: ${selectedRoom.name}`;

        navigateTo(SCREENS.ROOM_DETAIL);
    }

    function resetIdleTimer() {
        // Clear all timers
        if (idleTimer) clearTimeout(idleTimer);
        if (totalIdleTimer) clearTimeout(totalIdleTimer);
        if (countdownInterval) clearInterval(countdownInterval);
        
        // Hide popup if active
        if (isPopupActive) {
            hideInactivityPopup();
        }

        const homeScreen = document.getElementById(SCREENS.HOME);
        // Only trigger inactivity if NOT on home screen
        if (homeScreen && !homeScreen.classList.contains('active')) {
            // Stage 1: Wait to show popup
            idleTimer = setTimeout(() => {
                showInactivityPopup();
            }, INACTIVITY_POPUP_TIME);

            // Stage 2: Wait to reset app (total time)
            totalIdleTimer = setTimeout(() => {
                resetApp();
            }, INACTIVITY_TOTAL_TIME);
        }
    }

    function showInactivityPopup() {
        isPopupActive = true;
        inactivityPopup.classList.remove('hidden');
        
        let remainingSeconds = (INACTIVITY_TOTAL_TIME - INACTIVITY_POPUP_TIME) / 1000;
        countdownDisplay.textContent = remainingSeconds;

        countdownInterval = setInterval(() => {
            remainingSeconds--;
            countdownDisplay.textContent = remainingSeconds;
            if (remainingSeconds <= 0) {
                clearInterval(countdownInterval);
            }
        }, 1000);
    }

    function hideInactivityPopup() {
        isPopupActive = false;
        inactivityPopup.classList.add('hidden');
        if (countdownInterval) clearInterval(countdownInterval);
    }

    function extendInactivity() {
        playSound('continue');
        hideInactivityPopup();
        
        // Clear timers
        if (idleTimer) clearTimeout(idleTimer);
        if (totalIdleTimer) clearTimeout(totalIdleTimer);
        
        // "alargar por 3 minutos mas"
        // We reset the timers but with an extension
        // Standard way: reset to 4 minutes + 3 minutes = 7 minutes?
        // Or just reset to 4 minutes but the user feels it's "3 more" than what was left?
        // Let's make it 3 minutes from NOW (when they press it) before showing popup again, 
        // and 5 minutes total from now to go home?
        // Or just reset to a fresh cycle. Usually users expect "reset to start".
        // But let's follow the prompt: "alargar por 3 minutos mas"
        // If they had 2 mins left, now they have 2 + 3 = 5 mins left.
        
        const extensionMs = INACTIVITY_EXTENSION_TIME;
        
        // Stage 1: Show popup after 2 minutes again (standard) or also extended?
        // Let's just reset to a full 4-minute cycle, it's safer.
        resetIdleTimer();
    }

    // --- Input Handling ---
    function updateCodeDisplay(type) {
        const digits = type === 'reservation' ? reservationCodeDigits : roomCodeDigits;
        digits.forEach((digit, index) => {
            if (index < currentCode.length) {
                digit.textContent = currentCode[index];
                digit.classList.add('filled');
            } else {
                digit.textContent = '';
                digit.classList.remove('filled');
            }
        });
        saveAppState();
    }

    function clearFeedback(type) {
        const feedback = type === 'reservation' ? reservationFeedback : roomCodeFeedback;
        feedback.textContent = '';
        feedback.className = 'feedback-message hidden';
    }

    function showFeedback(type, status, message) {
        const feedback = type === 'reservation' ? reservationFeedback : roomCodeFeedback;
        feedback.textContent = message;
        feedback.className = `feedback-message ${status} visible popup-animation`;
    }

    function handleKeyInput(key) {
        resetIdleTimer();
        const activeScreen = document.querySelector('.screen.active');
        const screenId = activeScreen ? activeScreen.id : 'NONE';

        // ROOM LIST KEYS
        if (screenId === SCREENS.ROOM_SELECTION) {
            // 1-9
            if (/^[1-9]$/.test(key)) {
                const roomIndex = parseInt(key);
                selectRoom(roomIndex);
                return;
            }
             // 0 for 10th item if exists
            if (key === '0') {
                 selectRoom(10);
                 return;
            }
        }

        // ROOM DETAIL KEYS
        if (screenId === SCREENS.ROOM_DETAIL) {
            if (key === '#' || key === 'Enter') {
                playSound('continue');
                navigateTo(SCREENS.SCANNER);
            } else if (key === '*') {
                playSound('tap'); // Back is like a tap/selection
                navigateTo(SCREENS.ROOM_SELECTION, 'back');
            }
            return;
        }

        // SCANNER KEYS
        if (screenId === SCREENS.SCANNER) {
            if (key === '#' || key === 'Enter') {
                playSound('continue');
                if (selectedHomeOption === 'reservation') {
                    // Reservations are pre-paid, skip payment screens
                    navigateTo(SCREENS.TERMS);
                } else {
                    navigateTo(SCREENS.PAYMENT_SELECTION);
                }
            }
            return;
        }

        // PAYMENT SELECTION KEYS
        if (screenId === SCREENS.PAYMENT_SELECTION) {
            if (key === '1') {
                playSound('tap');
                navigateTo(SCREENS.PAYMENT_AUTO);
            }
            if (key === '2') {
                playSound('tap');
                // Update waiting screen info
                const waitingRoom = document.getElementById('waiting-room-name');
                const waitingPrice = document.getElementById('waiting-price');
                if (waitingRoom && selectedRoom) waitingRoom.textContent = selectedRoom.name;
                if (waitingPrice && selectedRoom) {
                    waitingPrice.innerHTML = `${formatUSD(selectedRoom.priceUSD)} / ${formatBS(selectedRoom.priceUSD)}`;
                }
                navigateTo(SCREENS.PAYMENT_MANUAL);
            }
            return;
        }

        // MANUAL PAYMENT WAITING KEYS
        if (screenId === SCREENS.PAYMENT_MANUAL) {
            if (key === '#' || key === 'Enter') {
                playSound('continue');
                navigateTo(SCREENS.TERMS);
            }
            return;
        }

        // AUTO PAYMENT REFERENCE KEYS
        if (screenId === SCREENS.PAYMENT_AUTO) {
            if (/^\d$/.test(key)) {
                if (currentRefCode.length < REF_CODE_LENGTH) {
                    playSound('tap');
                    currentRefCode += key;
                    updateRefDisplay();
                }
            } else if (key === 'Backspace' || key === '*') {
                playSound('tap'); // Feedback for delete
                currentRefCode = currentRefCode.slice(0, -1);
                updateRefDisplay();
            } else if (key === '#' || key === 'Enter') {
                if (currentRefCode.length === REF_CODE_LENGTH) {
                    playSound('continue');
                    navigateTo(SCREENS.TERMS);
                }
            }
            return;
        }

        // TERMS KEYS
        if (screenId === SCREENS.TERMS) {
            if (key === '#' || key === 'Enter') {
                 playSound('continue');
                 navigateTo(SCREENS.FINAL);
            }
            return;
        }

        // FINAL KEYS
        if (screenId === SCREENS.FINAL) {
            if (key === '#' || key === 'Enter') {
                 playSound('continue');
                 resetApp();
            }
            return;
        }

        if (screenId === SCREENS.RESERVATION || screenId === SCREENS.ROOM_CODE) {
            const type = screenId === SCREENS.RESERVATION ? 'reservation' : 'room';
            const digits = type === 'reservation' ? reservationCodeDigits : roomCodeDigits;

            // NEW: Auto-clear if there was an error
            if (isErrorCode && /^\d$/.test(key)) {
                currentCode = '';
                isErrorCode = false;
                clearFeedback(type);
                digits.forEach(digit => digit.classList.remove('error'));
            }

            if (/^\d$/.test(key)) {
                if (currentCode.length < CODE_LENGTH) {
                    playSound('tap');
                    currentCode += key;
                    updateCodeDisplay(type);
                    clearFeedback(type);
                }
            }
            else if (key === 'Backspace' || key === '*' || key === 'Delete') {
                playSound('tap');
                isErrorCode = false;
                currentCode = currentCode.slice(0, -1);
                updateCodeDisplay(type);
                clearFeedback(type);
                digits.forEach(digit => digit.classList.remove('error'));
            }
            else if (key === 'Enter' || key === '#') {
                validateCode(type);
            }
        }

        // STAFF AUTH (RFID Simulation)
        if (screenId === SCREENS.STAFF_AUTH) {
            // El ESP32 enviará el ID como si fuera teclado. 
            // Si la tecla es un número largo (ej. 10 cifras) o termina en Enter, lo procesamos.
            // Para propósitos de este script, asumiremos que si llega un número "largo" es un scan.
            // O podemos usar la tecla '1' para simular un tag específico.
            if (key === '1') {
                processNFCScan("1234567890"); // Tag de prueba
            }
            else if (key === '#' || key === 'Enter') {
                if (scannedStaff.length > 0) {
                    playSound('continue');
                    renderStaffWelcome();
                    navigateTo(SCREENS.STAFF_WELCOME);
                }
            }
        }
    }

    async function processNFCScan(nfcCode) {
        try {
            const response = await fetch(`${API_URL}/api/acceso/validar-nfc`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    nfc_code: nfcCode,
                    tipo: KIOSK_MODE
                })
            });

            const data = await response.json();

            if (response.ok) {
                if (data.status === 'success' || data.status === 'already_in' || data.status === 'already_out') {
                    handleStaffScanSuccess(data);
                }
            } else {
                playSound('wrong');
                const scanner = document.querySelector('.rfid-illustration');
                if (scanner) {
                    scanner.classList.remove('shake-animation');
                    void scanner.offsetWidth;
                    scanner.classList.add('shake-animation');
                }
            }
        } catch (error) {
            console.error("Error validando NFC:", error);
            playSound('wrong');
        }
    }

    function handleStaffScanSuccess(data) {
        const name = data.nombre;
        const cargo = data.cargo || "Personal";
        const alreadyRegistered = (data.status === 'already_in' || data.status === 'already_out');

        if (!scannedStaff.some(s => s.nombre === name)) {
            playSound('correct');
            scannedStaff.push({ nombre: name, cargo: cargo });

            // Remove placeholder if it exists on first scan
            const placeholder = document.getElementById('rfid-placeholder');
            if (placeholder) {
                placeholder.remove();
            }

            const item = document.createElement('div');
            item.className = 'staff-item';
            item.innerHTML = `
                <div style="display:flex; flex-direction:column;">
                    <span style="font-weight:800;">${name}</span>
                    <span style="font-size:0.75em; opacity:0.8; text-transform:uppercase;">${cargo}${alreadyRegistered ? " (YA REGISTRADO)" : ""}</span>
                </div>
            `;
            scannedStaffList.appendChild(item);

            scannedStaffList.scrollTop = scannedStaffList.scrollHeight;
            btnStaffContinue.classList.remove('hidden');
            saveAppState();
        }
    }

    function simulateStaffScan() {
        // Pick a random name not already in list
        const availableNames = STAFF_NAMES.filter(n => !scannedStaff.some(s => s.nombre === n));
        const name = availableNames.length > 0 ? availableNames[Math.floor(Math.random() * availableNames.length)] : "Colaborador Extra";

        handleStaffScanSuccess({ nombre: name, cargo: "Colaborador", status: "success" });
    }

    function renderStaffWelcome() {
        staffWelcomeNames.innerHTML = '';
        scannedStaff.forEach(staff => {
            const tag = document.createElement('span');
            tag.className = 'welcome-name-tag';
            tag.textContent = staff.nombre + (scannedStaff.indexOf(staff) === scannedStaff.length - 1 ? '' : ',');
            staffWelcomeNames.appendChild(tag);
        });

        // Daily Quote Logic
        const today = new Date();
        const dateSeed = today.getFullYear() * 10000 + (today.getMonth() + 1) * 100 + today.getDate();
        const quoteIndex = dateSeed % CORPORATE_QUOTES.length;
        const quote = CORPORATE_QUOTES[quoteIndex];

        staffQuoteContainer.innerHTML = `
            <p class="quote-text">${quote.text}</p>
            <span class="quote-author">${quote.author}</span>
        `;
    }

    function validateCode(type) {
        if (currentCode.length === 0) return;
        
        const digits = type === 'reservation' ? reservationCodeDigits : roomCodeDigits;
        const msg = type === 'reservation' ? 'Reservación Encontrada' : 'Acceso Autorizado';
        const errorMsg = type === 'reservation' ? 'Reservación No Encontrada' : 'Código Incorrecto';

        if (currentCode === MOCK_VALID_CODE) {
            isErrorCode = false;
            playSound('correct');
            showFeedback(type, 'success', `✓ ${msg}`);
            
            digits.forEach((digit, index) => {
                setTimeout(() => {
                    digit.classList.add('success', 'bounce-animation');
                }, index * 100);
            });
            
            setTimeout(() => {
                if (type === 'reservation') {
                    navigateTo(SCREENS.SCANNER);
                } else {
                    // Room entry probably goes to success or some "Door Opened" screen
                    // For now, let's go to final screen as it's a kiosk demo
                    navigateTo(SCREENS.FINAL);
                }
                setTimeout(() => {
                    digits.forEach(d => d.classList.remove('success', 'bounce-animation'));
                }, 1000);
            }, 1500);
        } else {
            isErrorCode = true;
            playSound('wrong');
            showFeedback(type, 'error', `⚠ ${errorMsg}`);
            
            const displayId = type === 'reservation' ? 'reservation-code-display' : 'room-code-display';
            const container = document.getElementById(displayId);
            container.classList.remove('shake-animation');
            void container.offsetWidth;
            container.classList.add('shake-animation');

            digits.forEach(digit => {
                digit.classList.add('error');
            });
        }
    }

    function initFooterClicks() {
        // Encontrar todos los footer-help y darles funcionalidad
        const footers = document.querySelectorAll('.footer-help');
        footers.forEach(footer => {
            const items = footer.querySelectorAll('span');
            items.forEach(item => {
                const text = item.textContent.toUpperCase();
                if (text.includes('ASISTENCIA') || text.includes('-')) {
                    item.addEventListener('click', () => {
                        console.log("Assistance requested via click");
                        const msg = document.createElement('div');
                        msg.textContent = '🔔 Asistencia Solicitada';
                        msg.style.cssText = 'position: fixed; top: 20%; left: 50%; transform: translateX(-50%); background: white; color: #1e265c; padding: 1.5rem 3rem; border-radius: 50px; font-weight: bold; animation: popup 0.3s forwards; pointer-events: none; z-index: 2000; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border: 2px solid #1e265c;';
                        document.body.appendChild(msg);
                        setTimeout(() => msg.remove(), 2500);
                        playSound('tap');
                    });
                } else if (text.includes('INICIO') || text.includes('VOLVER') || text.includes('+')) {
                    item.addEventListener('click', () => {
                        playSound('tap');
                        navigateBack();
                    });
                } else if (text.includes('VOLVER') || text.includes('*')) {
                     item.addEventListener('click', () => {
                        playSound('tap');
                        const activeScreen = document.querySelector('.screen.active');
                        if (activeScreen.id === SCREENS.ROOM_DETAIL) {
                            navigateTo(SCREENS.ROOM_SELECTION, 'back');
                        } else {
                            resetApp();
                        }
                    });
                }
            });
        });
    }

    // --- Initialization ---
    (async () => {
        await fetchInitialData();
        initFooterClicks();
        await loadAppState();
    })();

    // --- Event Listeners ---

    // 1. Home
    btnWalkin.addEventListener('click', () => selectHomeOption('walkin'));
    btnReservation.addEventListener('click', () => selectHomeOption('reservation'));
    btnStaying.addEventListener('click', () => selectHomeOption('staying'));
    btnStaff.addEventListener('click', () => selectHomeOption('staff'));
    btnHomeConfirm.addEventListener('click', confirmHomeSelection);
    
    // Room Detail
    btnRoomConfirm.addEventListener('click', () => {
        playSound('continue');
        navigateTo(SCREENS.SCANNER);
    });

    // Global Key Listener
    window.addEventListener('keydown', (e) => {
        const key = e.key;
        const code = e.code;
        
        // Determine active screen
        // querySelector is safer if 'screens' array is somehow desynced
        const activeScreen = document.querySelector('.screen.active');
        const screenId = activeScreen ? activeScreen.id : 'NONE';

        if (key === '-' || key === 'Subtract') {
             console.log("Assistance requested");
             const msg = document.createElement('div');
             msg.textContent = '🔔 Asistencia Solicitada';
             msg.style.cssText = 'position: fixed; top: 20%; left: 50%; transform: translateX(-50%); background: white; color: #1e265c; padding: 1rem 2rem; border-radius: 30px; font-weight: bold; animation: popup 0.3s forwards; pointer-events: none; z-index: 2000; box-shadow: 0 4px 15px rgba(0,0,0,0.3);';
             document.body.appendChild(msg);
             setTimeout(() => msg.remove(), 2000);
            return;
        }

        if (key === '+' || key === 'Add') {
            resetApp();
            return;
        }

        if (screenId === SCREENS.HOME) {
            // Numbers 1 to 5
            if (key === '1' || code === 'Digit1') {
                selectHomeOption('walkin');
            } else if (key === '2' || code === 'Digit2') {
                selectHomeOption('reservation');
            } else if (key === '3' || code === 'Digit3') {
                selectHomeOption('staying');
            } else if (key === '4' || code === 'Digit4') {
                selectHomeOption('staff');
            } else if (key === '5' || code === 'Digit5') {
                if (KIOSK_MODE === 'salida') selectHomeOption('checkout');
            }
            // Confirmation: #, Enter
            else if (key === '#' || key === 'Enter' || code === 'Enter' || code === 'NumpadEnter') {
                if (isPopupActive) {
                    extendInactivity();
                } else {
                    confirmHomeSelection();
                }
            }
        } else {
            if (isPopupActive && (key === '#' || key === 'Enter' || code === 'Enter' || code === 'NumpadEnter')) {
                extendInactivity();
                return;
            }
            // Delegate other screen inputs
            handleKeyInput(key);
        }
    });

    // Aggressive Focus Strategy
    setInterval(() => {
        if (document.activeElement === document.body || document.activeElement === null) {
            window.focus();
        }
    }, 1000);



    // 3. Scanner
    btnScanContinue.addEventListener('click', () => {
        playSound('continue');
        if (selectedHomeOption === 'reservation') {
            // Reservations are pre-paid, skip payment screens
            navigateTo(SCREENS.TERMS);
        } else {
            navigateTo(SCREENS.PAYMENT_SELECTION);
        }
    });

    // 3b. Payment Selection
    paymentModeAuto.onclick = () => {
        playSound('tap');
        navigateTo(SCREENS.PAYMENT_AUTO);
    };
    paymentModeManual.onclick = () => {
        playSound('tap');
        
        // Update waiting screen info before navigating
        const waitingRoomName = document.getElementById('waiting-room-name');
        const waitingPrice = document.getElementById('waiting-price');
        
        if (selectedRoom) {
            waitingRoomName.textContent = selectedRoom.name;
            waitingPrice.textContent = selectedRoom.price;
        } else {
            // Fallback for direct testing/debug
            waitingRoomName.textContent = "---";
            waitingPrice.textContent = "---";
        }

        navigateTo(SCREENS.PAYMENT_MANUAL);
    };

    btnConfirmAutoPay.onclick = () => {
        if (currentRefCode.length === REF_CODE_LENGTH) {
            playSound('continue');
            navigateTo(SCREENS.TERMS);
        }
    };

    function updateRefDisplay() {
        paymentRefDigits.forEach((digit, index) => {
            if (index < currentRefCode.length) {
                digit.textContent = currentRefCode[index];
                digit.classList.add('filled');
            } else {
                digit.textContent = '';
                digit.classList.remove('filled');
            }
        });
        saveAppState();
    }

    // 4. Terms
    btnTermsAccept.addEventListener('click', () => {
        playSound('continue');
        navigateTo(SCREENS.FINAL);
    });

    // 5. Final
    btnFinish.addEventListener('click', () => {
        playSound('continue');
        resetApp();
    });

    // Staff Listeners
    btnStaffContinue.addEventListener('click', () => {
        if (scannedStaff.length > 0) {
            playSound('continue');
            // Al escanear correctamente una o varias tarjetas y continuar la idea no es que el porton abra de una vez 
            // al menos de que sea socio, sino que le pregunte a la recepcionista si puede conceder el acceso.
            const hasSocio = scannedStaff.some(s => s.cargo && s.cargo.toLowerCase().includes('socio'));
            
            if (hasSocio) {
                renderStaffWelcome();
                navigateTo(SCREENS.STAFF_WELCOME);
            } else {
                navigateTo(SCREENS.STAFF_WAITING);
            }
        }
    });

    btnStaffWaitingBack.addEventListener('click', () => {
        playSound('tap');
        resetApp();
    });

    btnStaffFinish.addEventListener('click', () => {
        playSound('continue');
        resetApp();
    });

    // Inactivity Popup button
    btnStayHere.addEventListener('click', extendInactivity);

    // Global click listener to reset idle timer
    document.addEventListener('click', () => {
        resetIdleTimer();
        // playSound('tap'); // Removed global tap, now specific
    });

    // --- Confetti Effect ---
    function shootConfetti() {
        const confettiCanvas = document.getElementById('confetti-canvas');
        if (!confettiCanvas) return;

        // Create a custom instance bound to this canvas
        const myConfetti = confetti.create(confettiCanvas, {
            resize: true,
            useWorker: true
        });

        const count = 200;
        const defaults = {
            origin: { y: 1 }, // Start from bottom
            zIndex: 9999,
            gravity: 0.5,     // Lower gravity = slower fall
            scalar: 1.2,      // Slightly larger pieces
            drift: 0,
            ticks: 400        // Last longer since they fall slower
        };

        function fire(particleRatio, opts) {
            myConfetti(Object.assign({}, defaults, opts, {
                particleCount: Math.floor(count * particleRatio)
            }));
        }

        fire(0.25, {
            spread: 26,
            startVelocity: 55,
        });

        fire(0.2, {
            spread: 60,
        });

        fire(0.35, {
            spread: 100,
            decay: 0.91,
            scalar: 0.8
        });

        fire(0.1, {
            spread: 120,
            startVelocity: 25,
            decay: 0.92,
            scalar: 1.2
        });

        fire(0.1, {
            spread: 120,
            startVelocity: 45,
        });
    }

    // Initialize
    navigateTo(SCREENS.HOME);
});
