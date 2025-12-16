

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
    },
    masterAgentResponse: null
};

// ============================================================================
// API Configuration
// ============================================================================

const API_BASE_URL = 'http://localhost:8000'; // Mock API for individual endpoints
const MASTER_AGENT_URL = 'http://localhost:8080'; // Master Agent API

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
    
    // Build the query and call master agent
    const query = strategicQuestion || 
        `Evaluate the innovation opportunity for ${moleculeName} in ${indication}`;
    
    setTimeout(() => {
        callMasterAgent(query);
    }, 500);
}

// ============================================================================
// Master Agent Integration - CALLS THE REAL BACKEND
// ============================================================================

async function callMasterAgent(userQuery) {
    // Set all agents to running
    Object.keys(AppState.agentStatuses).forEach(agent => {
        updateAgentStatus(agent, 'running');
    });
    
    addChatMessage('master', `🚀 Starting comprehensive analysis: "${userQuery}"`);
    addChatMessage('master', `Coordinating all worker agents... This may take a minute.`);
    
    try {
        const response = await fetch(`${MASTER_AGENT_URL}/run`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_query: userQuery
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Store the full response
        AppState.masterAgentResponse = result;
        
        // Process worker results and update agent data
        processWorkerResults(result.worker_results);
        
        // Update all agent statuses to done
        Object.keys(AppState.agentStatuses).forEach(agent => {
            updateAgentStatus(agent, 'done');
        });
        
        // Display the final answer from master agent
        if (result.final_answer) {
            addChatMessage('master', result.final_answer);
        }
        
        // Show report info if available
        if (result.report && result.report.download_link) {
            addChatMessage('report', `📄 Report generated! <a href="${MASTER_AGENT_URL}${result.report.download_link}" target="_blank" class="text-purple-600 underline">Download PDF</a>`);
        }
        
        // Switch to overview tab to show results
        switchTab('overview');
        
    } catch (error) {
        console.error('Master Agent error:', error);
        
        // Set all agents to error
        Object.keys(AppState.agentStatuses).forEach(agent => {
            updateAgentStatus(agent, 'error');
        });
        
        addChatMessage('master', `⚠️ Error connecting to Master Agent: ${error.message}. Please ensure the backend is running on port 8080.`);
    }
}

function processWorkerResults(workerResults) {
    if (!workerResults || !Array.isArray(workerResults)) return;
    
    workerResults.forEach(result => {
        const agentName = result.agent?.toLowerCase() || '';
        
        // Map agent names to our state keys
        if (agentName.includes('iqvia')) {
            AppState.agentData.iqvia = result.raw;
            addChatMessage('iqvia', result.summary || 'Market analysis complete.');
        } else if (agentName.includes('exim')) {
            AppState.agentData.exim = result.raw;
            addChatMessage('exim', result.summary || 'Trade analysis complete.');
        } else if (agentName.includes('patent')) {
            AppState.agentData.patents = result.raw;
            addChatMessage('patents', result.summary || 'Patent landscape mapped.');
        } else if (agentName.includes('clinical') || agentName.includes('trial')) {
            AppState.agentData.trials = result.raw;
            addChatMessage('trials', result.summary || 'Clinical trials analyzed.');
        } else if (agentName.includes('internal')) {
            AppState.agentData.internal = result.raw;
            addChatMessage('internal', result.summary || 'Internal knowledge retrieved.');
        } else if (agentName.includes('web') || agentName.includes('intelligence')) {
            AppState.agentData.web = result.raw;
            addChatMessage('web', result.summary || 'Web intelligence gathered.');
        }
    });
}

// ============================================================================
// Chat Functions
// ============================================================================

function initializeWorkspace() {
    // Update molecule name in UI
    document.getElementById('current-molecule-name').textContent = AppState.currentMolecule.name || 'New Analysis';
    document.getElementById('sidebar-molecule').textContent = AppState.currentMolecule.name || '-';
    document.getElementById('sidebar-indication').textContent = AppState.currentMolecule.indication || '-';
    document.getElementById('sidebar-geography').textContent = AppState.currentMolecule.geography || '-';
    
    // Initialize agent status
    renderAgentStatus();
    
    // Load initial overview
    switchTab('overview');
}

function addChatMessage(sender, message) {
    const chatContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-bubble';
    
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
        bgColor = 'bg-yellow-50';
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
    } else if (sender === 'internal') {
        iconClass = 'fa-database';
        bgColor = 'bg-purple-50';
        senderName = 'Internal Knowledge Agent';
    } else if (sender === 'report') {
        iconClass = 'fa-file-pdf';
        bgColor = 'bg-pink-50';
        senderName = 'Report Generator';
    }
    
    messageDiv.innerHTML = `
        <div class="flex gap-3 ${isUser ? 'justify-end' : ''}">
            ${!isUser ? `<div class="flex-shrink-0 w-10 h-10 ${bgColor} rounded-full flex items-center justify-center">
                <i class="fas ${iconClass} ${textColor}"></i>
            </div>` : ''}
            <div class="${isUser ? 'bg-blue-600 text-white' : 'bg-white'} rounded-lg p-4 max-w-2xl shadow-sm">
                ${!isUser ? `<p class="text-sm font-semibold ${textColor} mb-1">${senderName}</p>` : ''}
                <div class="${isUser ? 'text-white' : 'text-gray-700'} whitespace-pre-wrap">${message}</div>
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
    
    // Call the Master Agent with the user's query
    callMasterAgent(message);
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
        { key: 'internal', name: 'Internal', icon: 'fa-database' },
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
        if (tab.textContent.toLowerCase().includes(tabName.toLowerCase())) {
            tab.classList.add('active');
        }
    });
    
    // Load content
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
    const response = AppState.masterAgentResponse;
    
    let summaryHtml = '';
    if (response && response.final_answer) {
        summaryHtml = `
            <div class="bg-purple-50 border-l-4 border-purple-600 p-4 rounded mb-4">
                <h4 class="font-semibold text-purple-900 mb-2">Executive Summary</h4>
                <div class="text-sm text-gray-700 whitespace-pre-wrap">${response.final_answer}</div>
            </div>
        `;
    }
    
    content.innerHTML = `
        <div class="space-y-4">
            <h3 class="text-lg font-bold text-gray-900">Analysis Overview</h3>
            
            ${summaryHtml}
            
            <div class="bg-gray-50 p-4 rounded-lg">
                <p class="text-sm text-gray-700">
                    <strong>Molecule:</strong> ${AppState.currentMolecule.name || 'N/A'}<br>
                    <strong>Indication:</strong> ${AppState.currentMolecule.indication || 'N/A'}<br>
                    <strong>Geography:</strong> ${AppState.currentMolecule.geography || 'Global'}
                </p>
            </div>
            
            <h4 class="font-semibold text-gray-900 mt-4">Data Sources:</h4>
            <ul class="space-y-2 text-sm text-gray-700">
                <li class="flex items-start gap-2">
                    <i class="fas fa-${AppState.agentData.iqvia ? 'check-circle text-green-600' : 'circle text-gray-400'} mt-1"></i>
                    <span>IQVIA Market Data ${AppState.agentData.iqvia ? '✓' : '(pending)'}</span>
                </li>
                <li class="flex items-start gap-2">
                    <i class="fas fa-${AppState.agentData.exim ? 'check-circle text-green-600' : 'circle text-gray-400'} mt-1"></i>
                    <span>EXIM Trade Data ${AppState.agentData.exim ? '✓' : '(pending)'}</span>
                </li>
                <li class="flex items-start gap-2">
                    <i class="fas fa-${AppState.agentData.trials ? 'check-circle text-green-600' : 'circle text-gray-400'} mt-1"></i>
                    <span>Clinical Trials ${AppState.agentData.trials ? '✓' : '(pending)'}</span>
                </li>
                <li class="flex items-start gap-2">
                    <i class="fas fa-${AppState.agentData.patents ? 'check-circle text-green-600' : 'circle text-gray-400'} mt-1"></i>
                    <span>Patent Landscape ${AppState.agentData.patents ? '✓' : '(pending)'}</span>
                </li>
            </ul>
            
            <div class="mt-6 p-4 bg-blue-50 rounded-lg">
                <h4 class="font-semibold text-blue-900 mb-2">💡 Explore Data</h4>
                <p class="text-sm text-blue-800">
                    Click on the tabs above to explore detailed insights from each data source.
                </p>
            </div>
        </div>
    `;
}

function displayMarketInsights() {
    const data = AppState.agentData.iqvia;
    const content = document.getElementById('insight-content');
    
    if (!data) {
        content.innerHTML = '<p class="text-gray-500">No market data available yet. Run an analysis first.</p>';
        return;
    }
    
    // Handle different response structures
    const markets = data.markets || [];
    const molecule = data.molecule || AppState.currentMolecule.name;
    
    content.innerHTML = `
        <div class="space-y-4">
            <h3 class="text-lg font-bold text-gray-900">Market Analysis</h3>
            
            <div class="bg-purple-50 p-3 rounded-lg">
                <p class="text-sm"><strong>Molecule:</strong> ${molecule}</p>
                <p class="text-sm"><strong>Therapy Area:</strong> ${data.therapy_area || 'N/A'}</p>
            </div>
            
            ${markets.length > 0 ? `
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
                        ${markets.map(market => `
                            <tr>
                                <td class="font-medium">${market.country || 'N/A'}</td>
                                <td>$${market.sales_2024_musd || market.sales || 'N/A'}M</td>
                                <td class="${(market.cagr_5y || 0) > 0 ? 'text-green-600' : 'text-red-600'}">
                                    ${(market.cagr_5y || 0) > 0 ? '+' : ''}${market.cagr_5y || 'N/A'}%
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            ` : '<p class="text-gray-500">No market breakdown available.</p>'}
            
            ${data.competition_summary ? `
                <div class="mt-4 p-4 bg-gray-50 rounded-lg">
                    <h4 class="font-semibold text-gray-900 mb-2">Competitive Landscape</h4>
                    <p class="text-sm text-gray-700 mb-2"><strong>Top Competitors:</strong> ${data.competition_summary.top_competitors?.join(', ') || 'N/A'}</p>
                    <p class="text-sm text-gray-700"><strong>Market Dynamics:</strong> ${data.competition_summary.therapy_dynamics || 'N/A'}</p>
                </div>
            ` : ''}
            
            <p class="text-xs text-gray-500 mt-4">Source: IQVIA Agent</p>
        </div>
    `;
}

function displayTradeInsights() {
    const data = AppState.agentData.exim;
    const content = document.getElementById('insight-content');
    
    if (!data) {
        content.innerHTML = '<p class="text-gray-500">No trade data available yet. Run an analysis first.</p>';
        return;
    }
    
    const tradeData = data.trade_data || [];
    
    content.innerHTML = `
        <div class="space-y-4">
            <h3 class="text-lg font-bold text-gray-900">Export-Import Analysis</h3>
            
            <div class="bg-blue-50 p-3 rounded-lg">
                <p class="text-sm"><strong>Product:</strong> ${data.product || 'N/A'}</p>
                <p class="text-sm"><strong>Year:</strong> ${data.year || 'N/A'}</p>
            </div>
            
            ${tradeData.length > 0 ? `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Country</th>
                            <th>Exports (T)</th>
                            <th>Imports (T)</th>
                            <th>Position</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tradeData.map(trade => `
                            <tr>
                                <td class="font-medium">${trade.country || 'N/A'}</td>
                                <td>${(trade.exports_tonnes || 0).toLocaleString()}</td>
                                <td>${(trade.imports_tonnes || 0).toLocaleString()}</td>
                                <td>
                                    <span class="badge ${(trade.net_position || '').includes('Exporter') ? 'badge-green' : 'badge-yellow'}">
                                        ${trade.net_position || 'N/A'}
                                    </span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            ` : '<p class="text-gray-500">No trade breakdown available.</p>'}
            
            ${data.sourcing_insights ? `
                <div class="mt-4 p-4 bg-yellow-50 rounded-lg">
                    <h4 class="font-semibold text-yellow-900 mb-2">📊 Sourcing Insights</h4>
                    <p class="text-sm text-yellow-800">${data.sourcing_insights}</p>
                </div>
            ` : ''}
            
            <p class="text-xs text-gray-500 mt-4">Source: EXIM Agent</p>
        </div>
    `;
}

function displayTrialsInsights() {
    const data = AppState.agentData.trials;
    const content = document.getElementById('insight-content');
    
    if (!data) {
        content.innerHTML = '<p class="text-gray-500">No clinical trials data available yet. Run an analysis first.</p>';
        return;
    }
    
    const activeTrials = data.active_trials || [];
    
    content.innerHTML = `
        <div class="space-y-4">
            <h3 class="text-lg font-bold text-gray-900">Clinical Trials Pipeline</h3>
            
            <div class="grid grid-cols-2 gap-3">
                <div class="bg-red-50 p-3 rounded-lg">
                    <p class="text-2xl font-bold text-red-600">${data.total_trials || activeTrials.length || 0}</p>
                    <p class="text-sm text-red-800">Total Trials</p>
                </div>
                <div class="bg-green-50 p-3 rounded-lg">
                    <p class="text-2xl font-bold text-green-600">${activeTrials.length || 0}</p>
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
            
            ${activeTrials.length > 0 ? `
                <h4 class="font-semibold text-gray-900 mt-4">Active Trials</h4>
                <div class="space-y-3 max-h-64 overflow-y-auto">
                    ${activeTrials.slice(0, 5).map(trial => `
                        <div class="border border-gray-200 rounded-lg p-3 hover:border-purple-300 transition">
                            <div class="flex justify-between items-start mb-2">
                                <h5 class="font-semibold text-sm text-gray-900">${trial.title || 'Untitled Trial'}</h5>
                                <span class="badge badge-blue">${trial.phase || 'N/A'}</span>
                            </div>
                            <p class="text-xs text-gray-600 mb-2">${trial.indication || 'N/A'}</p>
                            <div class="grid grid-cols-2 gap-2 text-xs text-gray-500">
                                <div><strong>Sponsor:</strong> ${trial.sponsor || 'N/A'}</div>
                                <div><strong>Status:</strong> ${trial.status || 'N/A'}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            <p class="text-xs text-gray-500 mt-4">Source: Clinical Trials Agent</p>
        </div>
    `;
}

function displayPatentInsights() {
    const data = AppState.agentData.patents;
    const content = document.getElementById('insight-content');
    
    if (!data) {
        content.innerHTML = '<p class="text-gray-500">No patent data available yet. Run an analysis first.</p>';
        return;
    }
    
    const patents = data.patent_status || [];
    const ftoFlag = data.fto_flag || 'Unknown';
    const ftoColor = ftoFlag.includes('Clear') ? 'green' : ftoFlag.includes('Blocked') ? 'red' : 'yellow';
    
    content.innerHTML = `
        <div class="space-y-4">
            <h3 class="text-lg font-bold text-gray-900">Patent Landscape</h3>
            
            <div class="bg-${ftoColor}-50 border-l-4 border-${ftoColor}-600 p-4 rounded">
                <p class="text-sm font-semibold text-${ftoColor}-900">Freedom to Operate (FTO)</p>
                <p class="text-sm text-${ftoColor}-800">${ftoFlag}</p>
            </div>
            
            ${patents.length > 0 ? `
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
                        ${patents.map(patent => `
                            <tr>
                                <td class="font-mono text-xs">${patent.patent_number || 'N/A'}</td>
                                <td>${patent.holder || 'N/A'}</td>
                                <td>${patent.expiry_date || 'N/A'}</td>
                                <td>
                                    <span class="badge ${patent.status === 'Active' ? 'badge-red' : 'badge-green'}">
                                        ${patent.status || 'N/A'}
                                    </span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            ` : '<p class="text-gray-500">No patent breakdown available.</p>'}
            
            ${data.generic_opportunity ? `
                <div class="p-4 bg-purple-50 rounded-lg">
                    <h4 class="font-semibold text-purple-900 mb-2">💊 Generic Opportunity</h4>
                    <p class="text-sm text-purple-800">${data.generic_opportunity}</p>
                </div>
            ` : ''}
            
            <p class="text-xs text-gray-500 mt-4">Source: Patent Agent</p>
        </div>
    `;
}

// ============================================================================
// Report Generation
// ============================================================================

async function generateReport() {
    addChatMessage('master', '📄 Generating comprehensive report...');
    updateAgentStatus('report', 'running');
    
    if (AppState.masterAgentResponse && AppState.masterAgentResponse.report) {
        const report = AppState.masterAgentResponse.report;
        updateAgentStatus('report', 'done');
        
        if (report.download_link) {
            const fullUrl = `${MASTER_AGENT_URL}${report.download_link}`;
            addChatMessage('report', `✅ Report ready! <a href="${fullUrl}" target="_blank" class="text-purple-600 underline font-semibold">Download PDF</a>`);
            window.open(fullUrl, '_blank');
        } else {
            addChatMessage('report', `Report generated. ID: ${report.report_id || 'N/A'}`);
        }
        
        showScreen('screen-reports');
        loadReportsArchive();
    } else {
        updateAgentStatus('report', 'error');
        addChatMessage('master', '⚠️ No report available. Please run an analysis first.');
    }
}

// ============================================================================
// Molecule Dossier Functions
// ============================================================================

function loadMoleculeDossier() {
    document.getElementById('dossier-molecule').textContent = AppState.currentMolecule.name || 'Molecule';
    document.getElementById('dossier-indication').textContent = `Primary Indication: ${AppState.currentMolecule.indication || 'N/A'}`;
    
    loadUnmetNeeds();
    loadTrialsTable();
    loadPatentsTable();
    loadInnovationIdeas();
}

function loadUnmetNeeds() {
    const container = document.getElementById('unmet-needs-content');
    const internalData = AppState.agentData.internal;
    
    container.innerHTML = `
        <ul class="space-y-2 text-gray-700">
            <li class="flex items-start gap-2">
                <i class="fas fa-circle text-purple-600 text-xs mt-1"></i>
                <span>High disease burden with limited access to affordable treatment options</span>
            </li>
            <li class="flex items-start gap-2">
                <i class="fas fa-circle text-purple-600 text-xs mt-1"></i>
                <span>Patient compliance challenges with current dosing regimens</span>
            </li>
            <li class="flex items-start gap-2">
                <i class="fas fa-circle text-purple-600 text-xs mt-1"></i>
                <span>Need for improved formulations with better safety profile</span>
            </li>
        </ul>
    `;
}

function loadTrialsTable() {
    const data = AppState.agentData.trials;
    const container = document.getElementById('trials-table-content');
    
    if (!data || !data.active_trials) {
        container.innerHTML = '<p class="text-gray-500">No trials data available. Run an analysis first.</p>';
        return;
    }
    
    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Sponsor</th>
                    <th>Phase</th>
                    <th>Indication</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                ${data.active_trials.slice(0, 10).map(trial => `
                    <tr>
                        <td class="font-medium">${trial.sponsor || 'N/A'}</td>
                        <td><span class="badge badge-blue">${trial.phase || 'N/A'}</span></td>
                        <td>${trial.indication || 'N/A'}</td>
                        <td>${trial.status || 'N/A'}</td>
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
        container.innerHTML = '<p class="text-gray-500">No patent data available. Run an analysis first.</p>';
        return;
    }
    
    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Assignee</th>
                    <th>Patent ID</th>
                    <th>Expiry</th>
                    <th>FTO Flag</th>
                </tr>
            </thead>
            <tbody>
                ${data.patent_status.map(patent => `
                    <tr>
                        <td class="font-medium">${patent.holder || 'N/A'}</td>
                        <td class="font-mono text-xs">${patent.patent_number || 'N/A'}</td>
                        <td>${patent.expiry_date || 'N/A'}</td>
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
            description: 'Extended-release injectable to improve compliance',
            feasibility: 'High',
            impact: 'High'
        },
        {
            title: 'Fixed-Dose Combination',
            description: 'Combine with complementary mechanism',
            feasibility: 'Medium',
            impact: 'High'
        },
        {
            title: 'Pediatric Formulation',
            description: 'Age-appropriate dosage form',
            feasibility: 'High',
            impact: 'Medium'
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
// Reports Archive
// ============================================================================

function loadReportsArchive() {
    loadReportPreview();
    
    const archiveContainer = document.getElementById('report-archive');
    const reports = [
        { molecule: AppState.currentMolecule.name || 'Latest Analysis', date: new Date().toLocaleDateString(), tags: ['Innovation'] }
    ];
    
    archiveContainer.innerHTML = reports.map(report => `
        <div class="report-card">
            <h4 class="font-semibold text-gray-900 mb-1">${report.molecule}</h4>
            <p class="text-xs text-gray-500 mb-2">${report.date}</p>
            <div class="flex flex-wrap gap-1">
                ${report.tags.map(tag => `<span class="badge badge-purple text-xs">${tag}</span>`).join('')}
            </div>
        </div>
    `).join('');
}

function loadReportPreview() {
    const container = document.getElementById('report-preview');
    const response = AppState.masterAgentResponse;
    
    container.innerHTML = `
        <div class="space-y-6">
            <section>
                <h3 class="text-lg font-bold text-gray-900 mb-3">Executive Summary</h3>
                <div class="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                    ${response?.final_answer || 'No analysis available yet. Run an exploration to generate a report.'}
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
    console.log('Master Agent URL:', MASTER_AGENT_URL);
});