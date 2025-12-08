// ============================================================================
// Global State Management
// ============================================================================

const AppState = {
    currentScreen: 'screen-landing',
    currentMolecule: {
        name: '',
        indication: '',
        geography: '',
        timeframe: ''
    },
    agentStatuses: {
        iqvia: 'idle',
        exim: 'idle',
        patents: 'idle',
        trials: 'idle',
        internal: 'idle',
        web: 'idle',
        report: 'idle'
    },
    chatHistory: [],
    currentTab: 'overview',
    agentData: {
        iqvia: null,
        exim: null,
        patents: null,
        trials: null,
        internal: null,
        web: null
    }
};

// ============================================================================
// API Configuration
// ============================================================================

const API_BASE_URL = 'http://localhost:8000'; // Change this to your API URL

// ============================================================================
// Screen Navigation
// ============================================================================

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.add('hidden');
    });
    document.getElementById(screenId).classList.remove('hidden');
    AppState.currentScreen = screenId;
    
    // Initialize screen-specific content
    if (screenId === 'screen-workspace') {
        initializeWorkspace();
    } else if (screenId === 'screen-molecule-dossier') {
        loadMoleculeDossier();
    } else if (screenId === 'screen-reports') {
        loadReportsArchive();
    }
}

// ============================================================================
// Case Setup Functions
// ============================================================================

function launchAgentRun() {
    // Get form values
    const moleculeName = document.getElementById('molecule-name').value;
    const indication = document.getElementById('indication').value;
    const geography = document.getElementById('geography').value;
    const timeframe = document.getElementById('timeframe').value;
    const strategicQuestion = document.getElementById('strategic-question').value;
    
    // Validate inputs
    if (!moleculeName || !indication) {
        alert('Please enter at least the molecule name and indication');
        return;
    }
    
    // Update global state
    AppState.currentMolecule = {
        name: moleculeName,
        indication: indication,
        geography: geography || 'Global',
        timeframe: timeframe || '2024-2026',
        strategicQuestion: strategicQuestion
    };
    
    // Navigate to workspace
    showScreen('screen-workspace');
    
    // Start agent orchestration
    setTimeout(() => {
        orchestrateAgents();
    }, 500);
}

// ============================================================================
// Agent Orchestration - THIS IS WHERE YOU CALL YOUR AGENT FUNCTIONS
// ============================================================================

async function orchestrateAgents() {
    const moleculeName = AppState.currentMolecule.name;
    
    // Add welcome message
    addChatMessage('master', `Starting comprehensive analysis for ${moleculeName}. I'm coordinating with all worker agents...`);
    
    // Run agents in sequence (you can also run them in parallel)
    await runIQVIAAgent(moleculeName);
    await runEXIMAgent(moleculeName);
    await runPatentAgent(moleculeName);
    await runClinicalTrialsAgent(moleculeName);
    await runWebIntelligenceAgent(moleculeName);
    
    // Final summary
    addChatMessage('master', `Analysis complete! I've gathered insights from all agents. You can explore the results in the tabs on the right, or ask me specific questions.`);
}

// ============================================================================
// Individual Agent Functions - REPLACE THESE WITH YOUR ACTUAL AGENT CALLS
// ============================================================================

async function runIQVIAAgent(molecule) {
    updateAgentStatus('iqvia', 'running');
    addChatMessage('master', `🔍 IQVIA Agent is analyzing market data for ${molecule}...`);
    
    try {
        // *** CALL YOUR IQVIA AGENT HERE ***
        const response = await fetch(`${API_BASE_URL}/api/iqvia?molecule=${molecule}`);
        const data = await response.json();
        
        AppState.agentData.iqvia = data;
        updateAgentStatus('iqvia', 'done');
        addChatMessage('iqvia', `Market analysis complete. Found data for ${data.markets?.length || 0} markets.`);
        
        // Update the insights panel if on market tab
        if (AppState.currentTab === 'market') {
            displayMarketInsights();
        }
    } catch (error) {
        console.error('IQVIA Agent error:', error);
        updateAgentStatus('iqvia', 'error');
        addChatMessage('master', `⚠️ IQVIA Agent encountered an issue. Using cached data.`);
    }
}

async function runEXIMAgent(molecule) {
    updateAgentStatus('exim', 'running');
    addChatMessage('master', `🌍 EXIM Agent is analyzing trade data...`);
    
    try {
        // *** CALL YOUR EXIM AGENT HERE ***
        const product = `${molecule} API`;
        const response = await fetch(`${API_BASE_URL}/api/exim?product=${product}`);
        const data = await response.json();
        
        AppState.agentData.exim = data;
        updateAgentStatus('exim', 'done');
        addChatMessage('exim', `Trade analysis complete. Analyzed ${data.trade_data?.length || 0} countries.`);
        
        if (AppState.currentTab === 'trade') {
            displayTradeInsights();
        }
    } catch (error) {
        console.error('EXIM Agent error:', error);
        updateAgentStatus('exim', 'error');
    }
}

async function runPatentAgent(molecule) {
    updateAgentStatus('patents', 'running');
    addChatMessage('master', `⚖️ Patent Agent is searching IP databases...`);
    
    try {
        // *** CALL YOUR PATENT AGENT HERE ***
        const response = await fetch(`${API_BASE_URL}/api/patents?molecule=${molecule}`);
        const data = await response.json();
        
        AppState.agentData.patents = data;
        updateAgentStatus('patents', 'done');
        addChatMessage('patents', `Patent landscape mapped. FTO status: ${data.fto_flag || 'Unknown'}`);
        
        if (AppState.currentTab === 'patents') {
            displayPatentInsights();
        }
    } catch (error) {
        console.error('Patent Agent error:', error);
        updateAgentStatus('patents', 'error');
    }
}

async function runClinicalTrialsAgent(molecule) {
    updateAgentStatus('trials', 'running');
    addChatMessage('master', `🔬 Clinical Trials Agent is querying ClinicalTrials.gov...`);
    
    try {
        // *** CALL YOUR CLINICAL TRIALS AGENT HERE ***
        const response = await fetch(`${API_BASE_URL}/api/clinical-trials?molecule=${molecule}`);
        const data = await response.json();
        
        AppState.agentData.trials = data;
        updateAgentStatus('trials', 'done');
        addChatMessage('trials', `Found ${data.total_trials || 0} trials. ${data.active_trials?.length || 0} are currently active.`);
        
        if (AppState.currentTab === 'trials') {
            displayTrialsInsights();
        }
    } catch (error) {
        console.error('Clinical Trials Agent error:', error);
        updateAgentStatus('trials', 'error');
    }
}

async function runWebIntelligenceAgent(molecule) {
    updateAgentStatus('web', 'running');
    addChatMessage('master', `🌐 Web Intelligence Agent is searching for guidelines and publications...`);
    
    try {
        // *** CALL YOUR WEB INTELLIGENCE AGENT HERE ***
        const query = `${molecule} clinical guidelines treatment`;
        const response = await fetch(`${API_BASE_URL}/api/web-intelligence?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        AppState.agentData.web = data;
        updateAgentStatus('web', 'done');
        addChatMessage('web', `Found ${data.results_count || 0} relevant sources including guidelines and publications.`);
    } catch (error) {
        console.error('Web Intelligence Agent error:', error);
        updateAgentStatus('web', 'error');
    }
}

// ============================================================================
// Chat Functions
// ============================================================================

function initializeWorkspace() {
    // Update molecule name in UI
    document.getElementById('current-molecule-name').textContent = AppState.currentMolecule.name;
    document.getElementById('sidebar-molecule').textContent = AppState.currentMolecule.name;
    document.getElementById('sidebar-indication').textContent = AppState.currentMolecule.indication;
    document.getElementById('sidebar-geography').textContent = AppState.currentMolecule.geography;
    
    // Initialize agent status
    renderAgentStatus();
    
    // Load initial overview
    switchTab('overview');
}

function addChatMessage(sender, message) {
    const chatContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-bubble';
    
    const isMaster = sender === 'master';
    const isUser = sender === 'user';
    
    let iconClass = 'fa-brain';
    let bgColor = 'bg-purple-100';
    let textColor = 'text-purple-800';
    let senderName = 'Master Agent';
    
    if (isUser) {
        iconClass = 'fa-user';
        bgColor = 'bg-blue-100';
        textColor = 'text-blue-800';
        senderName = 'You';
    } else if (sender === 'iqvia') {
        iconClass = 'fa-chart-line';
        bgColor = 'bg-purple-50';
        senderName = 'IQVIA Agent';
    } else if (sender === 'exim') {
        iconClass = 'fa-globe';
        bgColor = 'bg-blue-50';
        senderName = 'EXIM Agent';
    } else if (sender === 'patents') {
        iconClass = 'fa-gavel';
        bgColor = 'bg-green-50';
        senderName = 'Patent Agent';
    } else if (sender === 'trials') {
        iconClass = 'fa-microscope';
        bgColor = 'bg-red-50';
        senderName = 'Clinical Trials Agent';
    } else if (sender === 'web') {
        iconClass = 'fa-search';
        bgColor = 'bg-indigo-50';
        senderName = 'Web Intelligence Agent';
    }
    
    messageDiv.innerHTML = `
        <div class="flex gap-3 ${isUser ? 'justify-end' : ''}">
            ${!isUser ? `<div class="flex-shrink-0 w-10 h-10 ${bgColor} rounded-full flex items-center justify-center">
                <i class="fas ${iconClass} ${textColor}"></i>
            </div>` : ''}
            <div class="${isUser ? 'bg-blue-600 text-white' : 'bg-white'} rounded-lg p-4 max-w-2xl shadow-sm">
                ${!isUser ? `<p class="text-sm font-semibold ${textColor} mb-1">${senderName}</p>` : ''}
                <p class="${isUser ? 'text-white' : 'text-gray-700'}">${message}</p>
            </div>
            ${isUser ? `<div class="flex-shrink-0 w-10 h-10 ${bgColor} rounded-full flex items-center justify-center">
                <i class="fas ${iconClass} ${textColor}"></i>
            </div>` : ''}
        </div>
    `;
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // Add to history
    AppState.chatHistory.push({ sender, message, timestamp: new Date() });
}

function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    addChatMessage('user', message);
    input.value = '';
    
    // *** PROCESS USER QUERY WITH YOUR MASTER AGENT HERE ***
    // This is where you'd call your master agent to interpret the user's question
    // and coordinate the appropriate worker agents
    
    setTimeout(() => {
        processMasterAgentQuery(message);
    }, 500);
}

async function processMasterAgentQuery(query) {
    // *** REPLACE THIS WITH YOUR ACTUAL MASTER AGENT LOGIC ***
    
    // Simple keyword-based routing for demo
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('market') || lowerQuery.includes('sales')) {
        addChatMessage('master', 'Let me pull the latest market data for you...');
        await runIQVIAAgent(AppState.currentMolecule.name);
        switchTab('market');
    } else if (lowerQuery.includes('patent') || lowerQuery.includes('ip')) {
        addChatMessage('master', 'Checking the patent landscape...');
        await runPatentAgent(AppState.currentMolecule.name);
        switchTab('patents');
    } else if (lowerQuery.includes('trial') || lowerQuery.includes('clinical')) {
        addChatMessage('master', 'Searching clinical trials databases...');
        await runClinicalTrialsAgent(AppState.currentMolecule.name);
        switchTab('trials');
    } else if (lowerQuery.includes('trade') || lowerQuery.includes('export') || lowerQuery.includes('import')) {
        addChatMessage('master', 'Analyzing trade data...');
        await runEXIMAgent(AppState.currentMolecule.name);
        switchTab('trade');
    } else {
        // Generic response
        addChatMessage('master', `I understand you're asking about: "${query}". Let me gather relevant information from our agents. You can also explore the tabs on the right for detailed insights.`);
    }
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

// ============================================================================
// Agent Status Management
// ============================================================================

function updateAgentStatus(agent, status) {
    AppState.agentStatuses[agent] = status;
    renderAgentStatus();
}

function renderAgentStatus() {
    const container = document.getElementById('agent-status-container');
    
    const agents = [
        { key: 'iqvia', name: 'IQVIA', icon: 'fa-chart-line' },
        { key: 'exim', name: 'EXIM', icon: 'fa-globe' },
        { key: 'patents', name: 'Patents', icon: 'fa-gavel' },
        { key: 'trials', name: 'Trials', icon: 'fa-microscope' },
        { key: 'web', name: 'Web Intel', icon: 'fa-search' }
    ];
    
    container.innerHTML = agents.map(agent => {
        const status = AppState.agentStatuses[agent.key];
        let statusIcon = '⚪';
        let statusClass = 'idle';
        
        if (status === 'running') {
            statusIcon = '🟡';
            statusClass = 'running status-running';
        } else if (status === 'done') {
            statusIcon = '✅';
            statusClass = 'done';
        } else if (status === 'error') {
            statusIcon = '❌';
            statusClass = 'error';
        }
        
        return `
            <div class="agent-status ${statusClass}">
                <span>${statusIcon}</span>
                <i class="fas ${agent.icon}"></i>
                <span>${agent.name}</span>
            </div>
        `;
    }).join('');
}

// ============================================================================
// Insights Panel Management
// ============================================================================

function switchTab(tabName) {
    AppState.currentTab = tabName;
    
    // Update tab styling
    document.querySelectorAll('.insight-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event?.target?.classList.add('active');
    
    // Load content
    const contentDiv = document.getElementById('insight-content');
    
    switch(tabName) {
        case 'overview':
            displayOverview();
            break;
        case 'market':
            displayMarketInsights();
            break;
        case 'trade':
            displayTradeInsights();
            break;
        case 'trials':
            displayTrialsInsights();
            break;
        case 'patents':
            displayPatentInsights();
            break;
    }
}

function displayOverview() {
    const content = document.getElementById('insight-content');
    content.innerHTML = `
        <div class="space-y-4">
            <h3 class="text-lg font-bold text-gray-900">Executive Summary</h3>
            <div class="bg-purple-50 border-l-4 border-purple-600 p-4 rounded">
                <p class="text-sm text-gray-700">
                    Comprehensive analysis for <strong>${AppState.currentMolecule.name}</strong> 
                    in the <strong>${AppState.currentMolecule.indication}</strong> indication.
                </p>
            </div>
            
            <h4 class="font-semibold text-gray-900 mt-4">Key Findings:</h4>
            <ul class="space-y-2 text-sm text-gray-700">
                <li class="flex items-start gap-2">
                    <i class="fas fa-check-circle text-green-600 mt-1"></i>
                    <span>Market data analyzed across ${AppState.agentData.iqvia?.markets?.length || 0} regions</span>
                </li>
                <li class="flex items-start gap-2">
                    <i class="fas fa-check-circle text-green-600 mt-1"></i>
                    <span>${AppState.agentData.trials?.total_trials || 0} clinical trials identified</span>
                </li>
                <li class="flex items-start gap-2">
                    <i class="fas fa-check-circle text-green-600 mt-1"></i>
                    <span>Patent status: ${AppState.agentData.patents?.fto_flag || 'Analyzing...'}</span>
                </li>
                <li class="flex items-start gap-2">
                    <i class="fas fa-check-circle text-green-600 mt-1"></i>
                    <span>Trade data available for multiple markets</span>
                </li>
            </ul>
            
            <div class="mt-6 p-4 bg-blue-50 rounded-lg">
                <h4 class="font-semibold text-blue-900 mb-2">💡 Next Steps</h4>
                <p class="text-sm text-blue-800">
                    Explore detailed insights in each tab, or ask me specific questions about market opportunities, 
                    competitive landscape, or innovation possibilities.
                </p>
            </div>
        </div>
    `;
}

function displayMarketInsights() {
    const data = AppState.agentData.iqvia;
    const content = document.getElementById('insight-content');
    
    if (!data || !data.markets) {
        content.innerHTML = '<p class="text-gray-500">No market data available yet. The IQVIA agent is still analyzing...</p>';
        return;
    }
    
    content.innerHTML = `
        <div class="space-y-4">
            <h3 class="text-lg font-bold text-gray-900">Market Analysis</h3>
            
            <div class="bg-purple-50 p-3 rounded-lg">
                <p class="text-sm"><strong>Molecule:</strong> ${data.molecule}</p>
                <p class="text-sm"><strong>Therapy Area:</strong> ${data.therapy_area || 'N/A'}</p>
            </div>
            
            <h4 class="font-semibold text-gray-900 mt-4">Market Size by Geography</h4>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Country</th>
                        <th>Sales (M USD)</th>
                        <th>5Y CAGR</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.markets.map(market => `
                        <tr>
                            <td class="font-medium">${market.country}</td>
                            <td>$${market.sales_2024_musd}M</td>
                            <td class="${market.cagr_5y > 0 ? 'text-green-600' : 'text-red-600'}">
                                ${market.cagr_5y > 0 ? '+' : ''}${market.cagr_5y}%
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
            
            ${data.competition_summary ? `
                <div class="mt-4 p-4 bg-gray-50 rounded-lg">
                    <h4 class="font-semibold text-gray-900 mb-2">Competitive Landscape</h4>
                    <p class="text-sm text-gray-700 mb-2"><strong>Top Competitors:</strong> ${data.competition_summary.top_competitors?.join(', ')}</p>
                    <p class="text-sm text-gray-700"><strong>Market Dynamics:</strong> ${data.competition_summary.therapy_dynamics}</p>
                </div>
            ` : ''}
            
            <p class="text-xs text-gray-500 mt-4">Source: IQVIA (Mock Data)</p>
        </div>
    `;
}

function displayTradeInsights() {
    const data = AppState.agentData.exim;
    const content = document.getElementById('insight-content');
    
    if (!data || !data.trade_data) {
        content.innerHTML = '<p class="text-gray-500">No trade data available yet...</p>';
        return;
    }
    
    content.innerHTML = `
        <div class="space-y-4">
            <h3 class="text-lg font-bold text-gray-900">Export-Import Analysis</h3>
            
            <div class="bg-blue-50 p-3 rounded-lg">
                <p class="text-sm"><strong>Product:</strong> ${data.product}</p>
                <p class="text-sm"><strong>Year:</strong> ${data.year}</p>
            </div>
            
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Country</th>
                        <th>Exports (T)</th>
                        <th>Imports (T)</th>
                        <th>Position</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.trade_data.map(trade => `
                        <tr>
                            <td class="font-medium">${trade.country}</td>
                            <td>${trade.exports_tonnes.toLocaleString()}</td>
                            <td>${trade.imports_tonnes.toLocaleString()}</td>
                            <td>
                                <span class="badge ${trade.net_position.includes('Exporter') ? 'badge-green' : 'badge-yellow'}">
                                    ${trade.net_position}
                                </span>
                            </td>
                            <td>$${trade.value_musd}M</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
            
            <div class="mt-4 p-4 bg-yellow-50 rounded-lg">
                <h4 class="font-semibold text-yellow-900 mb-2">📊 Sourcing Insights</h4>
                <p class="text-sm text-yellow-800">${data.sourcing_insights}</p>
                <p class="text-sm text-yellow-800 mt-2"><strong>Trend:</strong> ${data.trend}</p>
            </div>
            
            <p class="text-xs text-gray-500 mt-4">Source: EXIM Database (Mock Data)</p>
        </div>
    `;
}

function displayTrialsInsights() {
    const data = AppState.agentData.trials;
    const content = document.getElementById('insight-content');
    
    if (!data || !data.active_trials) {
        content.innerHTML = '<p class="text-gray-500">No clinical trials data available yet...</p>';
        return;
    }
    
    content.innerHTML = `
        <div class="space-y-4">
            <h3 class="text-lg font-bold text-gray-900">Clinical Trials Pipeline</h3>
            
            <div class="grid grid-cols-2 gap-3">
                <div class="bg-red-50 p-3 rounded-lg">
                    <p class="text-2xl font-bold text-red-600">${data.total_trials}</p>
                    <p class="text-sm text-red-800">Total Trials</p>
                </div>
                <div class="bg-green-50 p-3 rounded-lg">
                    <p class="text-2xl font-bold text-green-600">${data.active_trials?.length || 0}</p>
                    <p class="text-sm text-green-800">Active Trials</p>
                </div>
            </div>
            
            ${data.phase_distribution ? `
                <div class="p-4 bg-gray-50 rounded-lg">
                    <h4 class="font-semibold text-gray-900 mb-2">Phase Distribution</h4>
                    <div class="grid grid-cols-4 gap-2 text-center text-sm">
                        ${Object.entries(data.phase_distribution).map(([phase, count]) => `
                            <div>
                                <p class="font-bold text-lg">${count}</p>
                                <p class="text-gray-600">${phase}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            <h4 class="font-semibold text-gray-900 mt-4">Active Trials</h4>
            <div class="space-y-3">
                ${data.active_trials.slice(0, 5).map(trial => `
                    <div class="border border-gray-200 rounded-lg p-3 hover:border-purple-300 transition">
                        <div class="flex justify-between items-start mb-2">
                            <h5 class="font-semibold text-sm text-gray-900">${trial.title}</h5>
                            <span class="badge badge-blue">${trial.phase}</span>
                        </div>
                        <p class="text-xs text-gray-600 mb-2">${trial.indication}</p>
                        <div class="grid grid-cols-2 gap-2 text-xs text-gray-500">
                            <div><strong>Sponsor:</strong> ${trial.sponsor}</div>
                            <div><strong>Status:</strong> ${trial.status}</div>
                            <div><strong>NCT ID:</strong> ${trial.nct_id}</div>
                            <div><strong>Enrollment:</strong> ${trial.enrollment?.toLocaleString()}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
            
            <p class="text-xs text-gray-500 mt-4">Source: ClinicalTrials.gov (Mock Data)</p>
        </div>
    `;
}

function displayPatentInsights() {
    const data = AppState.agentData.patents;
    const content = document.getElementById('insight-content');
    
    if (!data || !data.patent_status) {
        content.innerHTML = '<p class="text-gray-500">No patent data available yet...</p>';
        return;
    }
    
    const ftoColor = data.fto_flag?.includes('Clear') ? 'green' : 
                     data.fto_flag?.includes('Blocked') ? 'red' : 'yellow';
    
    content.innerHTML = `
        <div class="space-y-4">
            <h3 class="text-lg font-bold text-gray-900">Patent Landscape</h3>
            
            <div class="bg-${ftoColor}-50 border-l-4 border-${ftoColor}-600 p-4 rounded">
                <p class="text-sm font-semibold text-${ftoColor}-900">Freedom to Operate (FTO)</p>
                <p class="text-sm text-${ftoColor}-800">${data.fto_flag}</p>
            </div>
            
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Patent #</th>
                        <th>Holder</th>
                        <th>Expiry</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.patent_status.map(patent => `
                        <tr>
                            <td class="font-mono text-xs">${patent.patent_number}</td>
                            <td>${patent.holder}</td>
                            <td>${patent.expiry_date}</td>
                            <td>
                                <span class="badge ${patent.status === 'Active' ? 'badge-red' : 'badge-green'}">
                                    ${patent.status}
                                </span>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
            
            ${data.competitive_landscape ? `
                <div class="p-4 bg-gray-50 rounded-lg">
                    <h4 class="font-semibold text-gray-900 mb-2">Competitive Landscape</h4>
                    <div class="grid grid-cols-2 gap-3 text-sm">
                        <div>
                            <p class="text-gray-600">Active Patents</p>
                            <p class="font-bold text-lg">${data.competitive_landscape.total_active_patents}</p>
                        </div>
                        <div>
                            <p class="text-gray-600">Filing Trend</p>
                            <p class="font-medium">${data.competitive_landscape.filing_trend}</p>
                        </div>
                    </div>
                </div>
            ` : ''}
            
            ${data.generic_opportunity ? `
                <div class="p-4 bg-purple-50 rounded-lg">
                    <h4 class="font-semibold text-purple-900 mb-2">💊 Generic Opportunity</h4>
                    <p class="text-sm text-purple-800">${data.generic_opportunity}</p>
                </div>
            ` : ''}
            
            <p class="text-xs text-gray-500 mt-4">Source: USPTO & Patent Databases (Mock Data)</p>
        </div>
    `;
}

// ============================================================================
// Molecule Dossier Functions
// ============================================================================

function loadMoleculeDossier() {
    // Update header
    document.getElementById('dossier-molecule').textContent = AppState.currentMolecule.name;
    document.getElementById('dossier-indication').textContent = `Primary Indication: ${AppState.currentMolecule.indication}`;
    
    // Load each section
    loadUnmetNeeds();
    loadTrialsTable();
    loadPatentsTable();
    loadInnovationIdeas();
}

function loadUnmetNeeds() {
    const container = document.getElementById('unmet-needs-content');
    container.innerHTML = `
        <ul class="space-y-2 text-gray-700">
            <li class="flex items-start gap-2">
                <i class="fas fa-circle text-purple-600 text-xs mt-1"></i>
                <span>High disease burden in emerging markets with limited access to affordable treatment options</span>
            </li>
            <li class="flex items-start gap-2">
                <i class="fas fa-circle text-purple-600 text-xs mt-1"></i>
                <span>Patient compliance challenges with current dosing regimens</span>
            </li>
            <li class="flex items-start gap-2">
                <i class="fas fa-circle text-purple-600 text-xs mt-1"></i>
                <span>Need for improved formulations with better safety profile</span>
            </li>
            <li class="flex items-start gap-2">
                <i class="fas fa-circle text-purple-600 text-xs mt-1"></i>
                <span>Pediatric populations underserved with appropriate dosage forms</span>
            </li>
        </ul>
        
        <div class="mt-4 grid grid-cols-3 gap-4">
            <div class="bg-purple-50 p-3 rounded-lg text-center">
                <p class="text-2xl font-bold text-purple-600">12.5M</p>
                <p class="text-sm text-purple-800">Patients (US)</p>
            </div>
            <div class="bg-blue-50 p-3 rounded-lg text-center">
                <p class="text-2xl font-bold text-blue-600">45M</p>
                <p class="text-sm text-blue-800">Patients (Global)</p>
            </div>
            <div class="bg-green-50 p-3 rounded-lg text-center">
                <p class="text-2xl font-bold text-green-600">8.5%</p>
                <p class="text-sm text-green-800">Market CAGR</p>
            </div>
        </div>
    `;
}

function loadTrialsTable() {
    const data = AppState.agentData.trials;
    const container = document.getElementById('trials-table-content');
    
    if (!data || !data.active_trials) {
        container.innerHTML = '<p class="text-gray-500">Loading trials data...</p>';
        return;
    }
    
    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Sponsor</th>
                    <th>Phase</th>
                    <th>Indication</th>
                    <th>Geography</th>
                    <th>Est. Completion</th>
                </tr>
            </thead>
            <tbody>
                ${data.active_trials.slice(0, 10).map(trial => `
                    <tr>
                        <td class="font-medium">${trial.sponsor}</td>
                        <td><span class="badge badge-blue">${trial.phase}</span></td>
                        <td>${trial.indication}</td>
                        <td>Multi-country</td>
                        <td>${trial.estimated_completion || 'N/A'}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function loadPatentsTable() {
    const data = AppState.agentData.patents;
    const container = document.getElementById('patents-table-content');
    
    if (!data || !data.patent_status) {
        container.innerHTML = '<p class="text-gray-500">Loading patent data...</p>';
        return;
    }
    
    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Assignee</th>
                    <th>Patent ID</th>
                    <th>Title</th>
                    <th>Expiry</th>
                    <th>FTO Flag</th>
                </tr>
            </thead>
            <tbody>
                ${data.patent_status.map(patent => `
                    <tr>
                        <td class="font-medium">${patent.holder}</td>
                        <td class="font-mono text-xs">${patent.patent_number}</td>
                        <td class="text-sm">${patent.title}</td>
                        <td>${patent.expiry_date}</td>
                        <td>
                            <span class="badge ${patent.status === 'Active' ? 'badge-red' : 'badge-green'}">
                                ${patent.status === 'Active' ? '🔴 Blocked' : '🟢 Clear'}
                            </span>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function loadInnovationIdeas() {
    const container = document.getElementById('innovation-ideas-content');
    
    const ideas = [
        {
            title: 'Once-Weekly Depot Formulation',
            description: 'Extended-release injectable formulation to improve patient compliance and reduce dosing frequency',
            feasibility: 'High',
            impact: 'High'
        },
        {
            title: 'Fixed-Dose Combination Therapy',
            description: 'Combine with complementary mechanism of action to enhance efficacy and simplify treatment regimen',
            feasibility: 'Medium',
            impact: 'High'
        },
        {
            title: 'Pediatric Oral Dispersible Tablet',
            description: 'Age-appropriate formulation for pediatric patients with improved palatability',
            feasibility: 'High',
            impact: 'Medium'
        },
        {
            title: 'Novel Indication Expansion',
            description: 'Explore efficacy in related disease areas based on mechanism of action and preclinical data',
            feasibility: 'Medium',
            impact: 'Very High'
        }
    ];
    
    container.innerHTML = ideas.map(idea => `
        <div class="innovation-card">
            <h4 class="font-semibold text-gray-900 mb-2">${idea.title}</h4>
            <p class="text-sm text-gray-600 mb-3">${idea.description}</p>
            <div class="flex gap-2">
                <span class="badge badge-purple">Feasibility: ${idea.feasibility}</span>
                <span class="badge badge-green">Impact: ${idea.impact}</span>
            </div>
        </div>
    `).join('');
}

// ============================================================================
// Report Generation Functions
// ============================================================================

async function generateReport() {
    // *** CALL YOUR REPORT GENERATION AGENT HERE ***
    
    addChatMessage('master', '📄 Generating comprehensive report...');
    updateAgentStatus('report', 'running');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/generate-report?report_type=pdf&topic=${AppState.currentMolecule.name} Innovation Opportunities`, {
            method: 'POST'
        });
        const data = await response.json();
        
        updateAgentStatus('report', 'done');
        addChatMessage('report', `Report generated successfully! Report ID: ${data.report_id}`);
        
        // Show reports screen with generated report
        AppState.reportData = data;
        showScreen('screen-reports');
    } catch (error) {
        console.error('Report generation error:', error);
        updateAgentStatus('report', 'error');
        addChatMessage('master', '⚠️ Report generation encountered an issue.');
    }
}

function loadReportsArchive() {
    // Load report preview
    loadReportPreview();
    
    // Load archive list
    const archiveContainer = document.getElementById('report-archive');
    
    const sampleReports = [
        {
            molecule: 'Metformin',
            date: 'Dec 8, 2025',
            geography: 'US, EU, India',
            tags: ['Diabetes', 'Generics']
        },
        {
            molecule: 'Semaglutide',
            date: 'Dec 5, 2025',
            geography: 'Global',
            tags: ['Diabetes', 'Obesity']
        },
        {
            molecule: 'Imatinib',
            date: 'Nov 28, 2025',
            geography: 'US, EU',
            tags: ['Oncology', 'CML']
        }
    ];
    
    archiveContainer.innerHTML = sampleReports.map(report => `
        <div class="report-card">
            <h4 class="font-semibold text-gray-900 mb-1">${report.molecule}</h4>
            <p class="text-xs text-gray-500 mb-2">${report.date}</p>
            <p class="text-xs text-gray-600 mb-2">📍 ${report.geography}</p>
            <div class="flex flex-wrap gap-1">
                ${report.tags.map(tag => `
                    <span class="badge badge-purple text-xs">${tag}</span>
                `).join('')}
            </div>
        </div>
    `).join('');
}

function loadReportPreview() {
    const container = document.getElementById('report-preview');
    
    container.innerHTML = `
        <div class="space-y-6">
            <section>
                <h3 class="text-lg font-bold text-gray-900 mb-3">Executive Summary</h3>
                <p class="text-sm text-gray-700 leading-relaxed">
                    Comprehensive analysis of <strong>${AppState.currentMolecule.name}</strong> reveals significant 
                    opportunities for product innovation and market expansion in the ${AppState.currentMolecule.indication} 
                    therapeutic area. Key findings indicate strong market fundamentals with identified unmet needs 
                    across multiple geographies.
                </p>
            </section>
            
            <section>
                <h3 class="text-lg font-bold text-gray-900 mb-3">Market & EXIM Snapshot</h3>
                <div class="bg-gray-50 p-4 rounded-lg">
                    <ul class="space-y-2 text-sm text-gray-700">
                        <li>• Global market size: $${AppState.agentData.iqvia?.markets?.reduce((sum, m) => sum + m.sales_2024_musd, 0) || 'N/A'}M USD</li>
                        <li>• Average CAGR: ${AppState.agentData.iqvia?.markets?.[0]?.cagr_5y || 'N/A'}%</li>
                        <li>• Key export markets identified with favorable trade dynamics</li>
                        <li>• Supply chain concentration presents opportunity for diversification</li>
                    </ul>
                </div>
            </section>
            
            <section>
                <h3 class="text-lg font-bold text-gray-900 mb-3">Clinical Pipeline Overview</h3>
                <div class="bg-gray-50 p-4 rounded-lg">
                    <p class="text-sm text-gray-700 mb-2">
                        <strong>${AppState.agentData.trials?.total_trials || 0}</strong> total trials identified, 
                        with <strong>${AppState.agentData.trials?.active_trials?.length || 0}</strong> currently active.
                    </p>
                    <p class="text-sm text-gray-700">
                        Phase 3 trials showing promise in expanded indications, suggesting potential for lifecycle management.
                    </p>
                </div>
            </section>
            
            <section>
                <h3 class="text-lg font-bold text-gray-900 mb-3">Patent Summary</h3>
                <div class="bg-gray-50 p-4 rounded-lg">
                    <p class="text-sm text-gray-700">
                        <strong>FTO Status:</strong> ${AppState.agentData.patents?.fto_flag || 'Under review'}
                    </p>
                    <p class="text-sm text-gray-700 mt-2">
                        ${AppState.agentData.patents?.generic_opportunity || 'Patent landscape analysis complete.'}
                    </p>
                </div>
            </section>
            
            <section>
                <h3 class="text-lg font-bold text-gray-900 mb-3">Innovation Opportunities</h3>
                <div class="space-y-3">
                    <div class="border-l-4 border-purple-600 bg-purple-50 p-3">
                        <h4 class="font-semibold text-purple-900 text-sm mb-1">Once-Weekly Depot Formulation</h4>
                        <p class="text-xs text-purple-800">High feasibility with significant patient compliance benefits</p>
                    </div>
                    <div class="border-l-4 border-blue-600 bg-blue-50 p-3">
                        <h4 class="font-semibold text-blue-900 text-sm mb-1">Fixed-Dose Combination</h4>
                        <p class="text-xs text-blue-800">Synergistic potential with complementary mechanisms</p>
                    </div>
                    <div class="border-l-4 border-green-600 bg-green-50 p-3">
                        <h4 class="font-semibold text-green-900 text-sm mb-1">Pediatric Formulation</h4>
                        <p class="text-xs text-green-800">Addresses underserved patient population</p>
                    </div>
                </div>
            </section>
        </div>
    `;
}

// ============================================================================
// Initialize App
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('PharmaVerse App Initialized');
    
    // Set default molecule for demo purposes
    AppState.currentMolecule = {
        name: 'Metformin',
        indication: 'Type 2 Diabetes',
        geography: 'US, EU, India',
        timeframe: '2024-2026'
    };
});
