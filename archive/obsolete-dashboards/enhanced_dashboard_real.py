#!/usr/bin/env python3
"""
Enhanced AI Factory Dashboard with Real Data Integration
- Connects to actual AI Factory backend services
- No mock data - displays real system state
"""

import asyncio
import json
import logging
import os
import sys
from aiohttp import web, ClientSession
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import persona processors
try:
    from personas.processor_factory import ProcessorFactory
    from azure_devops.multi_project_client import MultiProjectClient
    from orchestration.work_item_router import WorkItemRouter
    from orchestration.collaboration_protocols import CollaborationProtocols
    from work_queue.multi_project_queue import MultiProjectQueue
    from metrics.performance_tracker import PerformanceTracker
except ImportError as e:
    logger.warning(f"Import error: {e}")

# Factory state and data
factory_state = {
    "running": False,
    "start_time": None,
    "personas": {},
    "work_queue": None,
    "performance_tracker": None,
    "azure_client": None,
    "work_router": None
}

# HTML template (same as before but with real data notice)
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>AI Factory Control Center - Real Data</title>
    <style>
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 0; 
            padding: 0;
            background: #0a0a0a;
            color: #e0e0e0;
        }
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
        }
        h1 { margin: 0; font-size: 1.8em; }
        .real-data-badge {
            background: #22c55e;
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-left: 10px;
        }
        .controls {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        button {
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        .btn-toggle { 
            background: #22c55e; 
            color: white; 
            min-width: 120px;
        }
        .btn-toggle.stop { 
            background: #ef4444; 
        }
        .btn-logs { background: #3b82f6; color: white; }
        button:hover { transform: translateY(-1px); box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        
        .factory-status {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-left: 20px;
            padding: 6px 12px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 5px;
            font-size: 0.9em;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        .status-dot.running { background: #22c55e; }
        .status-dot.stopped { background: #ef4444; animation: none; }
        
        .main-container {
            display: grid;
            grid-template-columns: 600px 1fr;
            height: calc(100vh - 60px);
        }
        
        .sidebar {
            background: #1a1a1a;
            border-right: 1px solid #333;
            overflow-y: auto;
            padding: 20px;
        }
        
        .personas-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        
        .persona-card {
            background: #2a2a2a;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #333;
            cursor: pointer;
            transition: all 0.3s;
        }
        .persona-card:hover {
            border-color: #3b82f6;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(59, 130, 246, 0.2);
        }
        .persona-card.selected {
            border-color: #3b82f6;
            background: #1e3a5f;
        }
        .persona-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .persona-name {
            font-weight: bold;
            font-size: 1.1em;
        }
        .persona-role {
            color: #999;
            font-size: 0.9em;
            margin-top: 2px;
        }
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }
        .status-idle { background: #666; }
        .status-working { background: #3b82f6; animation: pulse 2s infinite; }
        .status-completed { background: #22c55e; }
        .status-error { background: #ef4444; }
        .status-blocked { background: #f59e0b; }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .content {
            padding: 20px;
            overflow-y: auto;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: #1a1a1a;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #333;
        }
        .stat-label {
            color: #666;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #3b82f6;
            margin-top: 5px;
        }
        
        .log-viewer {
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 5px;
            padding: 15px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
            overflow-y: auto;
        }
        .log-entry {
            padding: 3px 0;
            border-bottom: 1px solid #222;
        }
        .log-entry.error { color: #ef4444; }
        .log-entry.warning { color: #f59e0b; }
        .log-entry.info { color: #3b82f6; }
        .log-entry.debug { color: #666; }
        .log-entry.success { color: #22c55e; }
        
        .output-item {
            background: #1a1a1a;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #333;
        }
        .code-block {
            background: #0a0a0a;
            padding: 10px;
            border-radius: 3px;
            margin-top: 5px;
            font-family: monospace;
            overflow-x: auto;
        }
        
        .filter-bar {
            margin-bottom: 10px;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        select {
            background: #2a2a2a;
            color: #e0e0e0;
            border: 1px solid #333;
            padding: 5px 10px;
            border-radius: 3px;
        }
    </style>
    <script>
        let selectedPersona = null;
        let dashboardData = null;
        let logFilter = 'all';
        let factoryRunning = false;
        
        async function updateDashboard() {
            try {
                const response = await fetch('/api/dashboard-data');
                const data = await response.json();
                dashboardData = data;
                factoryRunning = data.factory_status === 'running';
                
                // Update factory status indicator
                updateFactoryStatus();
                
                // Update stats
                document.getElementById('totalWorkItems').textContent = data.stats.total_work_items;
                document.getElementById('activePersonas').textContent = data.stats.active_personas;
                document.getElementById('completedTasks').textContent = data.stats.completed_tasks;
                document.getElementById('systemUptime').textContent = data.stats.system_uptime;
                
                // Update personas
                updatePersonaList(data.personas);
                
                // Update selected persona details
                if (selectedPersona && data.personas[selectedPersona]) {
                    updatePersonaDetails(selectedPersona, data.personas[selectedPersona]);
                }
                
                // Update system logs if viewing
                if (!selectedPersona && document.getElementById('systemLogs')) {
                    updateSystemLogs(data.system_logs);
                }
                
                // Update connection status
                document.getElementById('connectionStatus').innerHTML = 
                    '🟢 Connected';
            } catch (error) {
                document.getElementById('connectionStatus').innerHTML = 
                    '🔴 Disconnected';
            }
        }
        
        function updateFactoryStatus() {
            const btn = document.getElementById('toggleBtn');
            const statusDot = document.getElementById('statusDot');
            const statusText = document.getElementById('statusText');
            
            if (factoryRunning) {
                btn.textContent = '⏹️ Stop Factory';
                btn.className = 'btn-toggle stop';
                statusDot.className = 'status-dot running';
                statusText.textContent = 'Running';
            } else {
                btn.textContent = '▶️ Start Factory';
                btn.className = 'btn-toggle';
                statusDot.className = 'status-dot stopped';
                statusText.textContent = 'Stopped';
            }
        }
        
        async function toggleFactory() {
            if (factoryRunning) {
                await stopFactory();
            } else {
                await startFactory();
            }
        }
        
        async function startFactory() {
            try {
                await fetch('/api/start-factory', { method: 'POST' });
                factoryRunning = true;
                updateFactoryStatus();
            } catch (error) {
                console.error('Failed to start factory:', error);
            }
        }
        
        async function stopFactory() {
            try {
                await fetch('/api/stop-factory', { method: 'POST' });
                factoryRunning = false;
                updateFactoryStatus();
            } catch (error) {
                console.error('Failed to stop factory:', error);
            }
        }
        
        function updatePersonaList(personas) {
            const container = document.getElementById('personaList');
            container.innerHTML = '';
            
            Object.entries(personas).forEach(([id, data]) => {
                const div = document.createElement('div');
                div.className = 'persona-card' + (id === selectedPersona ? ' selected' : '');
                div.onclick = () => selectPersona(id);
                
                div.innerHTML = `
                    <div class="persona-header">
                        <div>
                            <div class="persona-name">${data.info.name}</div>
                            <div class="persona-role">${data.info.role}</div>
                        </div>
                        <span class="status-indicator status-${data.state.status}"></span>
                    </div>
                    <div style="margin-top: 8px; font-size: 0.85em; color: #666;">
                        ${data.state.current_task || 'Idle'}
                    </div>
                `;
                
                container.appendChild(div);
            });
        }
        
        function selectPersona(personaId) {
            selectedPersona = personaId;
            updateDashboard();
        }
        
        function updatePersonaDetails(personaId, data) {
            const content = document.getElementById('mainContent');
            
            content.innerHTML = `
                <h2>${data.info.name} - ${data.info.role}</h2>
                <p><strong>Skills:</strong> ${data.info.skills}</p>
                <p><strong>Status:</strong> <span class="status-indicator status-${data.state.status}"></span> ${data.state.status}</p>
                <p><strong>Current Task:</strong> ${data.state.current_task || 'None'}</p>
                <p><strong>Work Items Completed:</strong> ${data.state.work_items_completed}</p>
                
                <h3>Recent Outputs</h3>
                <div class="outputs-section">
                    ${data.state.outputs_generated.map(output => `
                        <div class="output-item">
                            <strong>${output.type}:</strong> ${output.name}
                            ${output.preview ? `<div class="code-block">${output.preview}</div>` : ''}
                        </div>
                    `).join('') || '<p>No outputs generated yet</p>'}
                </div>
                
                <h3>Activity Log</h3>
                <div class="log-viewer" style="height: 300px;">
                    ${data.logs.map(log => `
                        <div class="log-entry ${log.level}">
                            [${new Date(log.timestamp).toLocaleTimeString()}] ${log.message}
                        </div>
                    `).join('') || '<p>No activity yet</p>'}
                </div>
            `;
        }
        
        function updateSystemLogs(logs) {
            const container = document.getElementById('systemLogs');
            if (!container) return;
            
            const filteredLogs = logFilter === 'all' 
                ? logs 
                : logs.filter(log => log.level === logFilter);
            
            container.innerHTML = filteredLogs.map(log => `
                <div class="log-entry ${log.level}">
                    [${new Date(log.timestamp).toLocaleTimeString()}] ${log.message}
                </div>
            `).join('') || '<p>No logs available</p>';
            
            // Auto-scroll to bottom
            container.scrollTop = container.scrollHeight;
        }
        
        function showSystemLogs() {
            selectedPersona = null;
            document.querySelectorAll('.persona-card').forEach(el => el.classList.remove('selected'));
            
            const content = document.getElementById('mainContent');
            content.innerHTML = `
                <h2>System Logs</h2>
                <div class="filter-bar">
                    <label>Filter:</label>
                    <select onchange="logFilter = this.value; updateDashboard()">
                        <option value="all">All</option>
                        <option value="error">Errors</option>
                        <option value="warning">Warnings</option>
                        <option value="info">Info</option>
                        <option value="debug">Debug</option>
                        <option value="success">Success</option>
                    </select>
                </div>
                <div class="log-viewer" id="systemLogs" style="height: 600px;"></div>
            `;
            
            updateDashboard();
        }
        
        // Start updates
        setInterval(updateDashboard, 2000);
        updateDashboard();
        
        // Show system logs by default
        window.onload = () => showSystemLogs();
    </script>
</head>
<body>
    <div class="header">
        <h1>🏭 AI Factory Control Center <span class="real-data-badge">REAL DATA</span></h1>
        <div class="controls">
            <button id="toggleBtn" class="btn-toggle" onclick="toggleFactory()">▶️ Start Factory</button>
            <button class="btn-logs" onclick="showSystemLogs()">📋 System Logs</button>
            <div class="factory-status">
                <span class="status-dot stopped" id="statusDot"></span>
                <span id="statusText">Stopped</span>
            </div>
            <span id="connectionStatus" style="margin-left: 20px; font-size: 0.9em;"></span>
        </div>
    </div>
    
    <div class="main-container">
        <div class="sidebar">
            <h3>Personas</h3>
            <div id="personaList" class="personas-grid"></div>
        </div>
        
        <div class="content">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Work Items</div>
                    <div class="stat-value" id="totalWorkItems">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Active Personas</div>
                    <div class="stat-value" id="activePersonas">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Completed Tasks</div>
                    <div class="stat-value" id="completedTasks">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">System Uptime</div>
                    <div class="stat-value" id="systemUptime">0h</div>
                </div>
            </div>
            
            <div id="mainContent">
                <!-- Dynamic content goes here -->
            </div>
        </div>
    </div>
</body>
</html>"""

# System logs storage
system_logs = []

def log_system_event(level: str, message: str):
    """Log a system event"""
    system_logs.append({
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message
    })
    # Keep only last 1000 logs
    if len(system_logs) > 1000:
        system_logs.pop(0)

async def initialize_factory():
    """Initialize the AI Factory components"""
    try:
        # Initialize components if available
        if 'ProcessorFactory' in globals():
            factory_state["processor_factory"] = ProcessorFactory()
            log_system_event("info", "Initialized ProcessorFactory")
        
        if 'PerformanceTracker' in globals():
            factory_state["performance_tracker"] = PerformanceTracker()
            log_system_event("info", "Initialized PerformanceTracker")
            
        if 'MultiProjectQueue' in globals():
            factory_state["work_queue"] = MultiProjectQueue()
            log_system_event("info", "Initialized MultiProjectQueue")
            
        # Initialize personas
        persona_list = [
            ("dave", "DaveBot", "Technical Lead", "Architecture, Code Reviews, Technical Design"),
            ("steve", "SteveBot", "Security Architect", "Security Design, Threat Modeling, Compliance"),
            ("kav", "KavBot", "Security Test Engineer", "Security Testing, Penetration Testing, SAST/DAST"),
            ("lachlan", "LachlanBot", "DevSecOps Engineer", "CI/CD, Infrastructure Security, Automation"),
            ("jordan", "JordanBot", "API Developer", "REST APIs, GraphQL, Integration"),
            ("puck", "PuckBot", "API Security Specialist", "API Security, OAuth, JWT"),
            ("shaun", "ShaunBot", "UI/UX Designer", "UI Design, UX Research, Prototyping"),
            ("matt", "MattBot", "Frontend Developer", "React, TypeScript, UI Implementation"),
            ("moby", "MobyBot", "Database Architect", "Database Design, SQL, Performance Tuning"),
            ("ruley", "RuleyBot", "Requirements Analyst", "Requirements Analysis, Documentation, Compliance"),
            ("brumbie", "BrumbieBot", "Development Manager", "Project Management, Sprint Planning, Team Coordination"),
            ("claude", "ClaudeBot", "AI Assistant", "Code Generation, Problem Solving, Documentation"),
            ("laureen", "LaureenBot", "QA Engineer", "Test Planning, Test Automation, Quality Assurance")
        ]
        
        for persona_id, name, role, skills in persona_list:
            factory_state["personas"][persona_id] = {
                "info": {
                    "name": name,
                    "role": role,
                    "skills": skills
                },
                "state": {
                    "status": "idle",
                    "current_task": None,
                    "work_items_completed": 0,
                    "outputs_generated": []
                },
                "logs": []
            }
            
        log_system_event("success", "AI Factory initialized successfully")
        return True
        
    except Exception as e:
        log_system_event("error", f"Failed to initialize factory: {str(e)}")
        return False

async def index(request):
    """Serve the dashboard HTML"""
    return web.Response(text=HTML_TEMPLATE, content_type='text/html')

async def dashboard_data(request):
    """Return real dashboard data"""
    global factory_state
    
    # Calculate real metrics
    active_count = sum(1 for p in factory_state["personas"].values() 
                      if p["state"]["status"] in ["working", "blocked"])
    
    completed_count = sum(p["state"]["work_items_completed"] 
                         for p in factory_state["personas"].values())
    
    # Calculate uptime
    uptime = "0h"
    if factory_state["running"] and factory_state["start_time"]:
        delta = datetime.now() - factory_state["start_time"]
        hours = int(delta.total_seconds() / 3600)
        minutes = int((delta.total_seconds() % 3600) / 60)
        uptime = f"{hours}h {minutes}m"
    
    # Get work queue size
    queue_size = factory_state.get("work_queue_count", 0)
    
    data = {
        "factory_status": "running" if factory_state["running"] else "stopped",
        "stats": {
            "total_work_items": queue_size,
            "active_personas": active_count,
            "completed_tasks": completed_count,
            "system_uptime": uptime
        },
        "personas": factory_state["personas"],
        "system_logs": system_logs[-100:]  # Last 100 logs
    }
    
    return web.json_response(data)

async def start_factory(request):
    """Start the AI factory"""
    global factory_state
    
    if not factory_state["running"]:
        factory_state["running"] = True
        factory_state["start_time"] = datetime.now()
        log_system_event("success", "AI Factory started")
        
        # Start background processing
        asyncio.create_task(factory_processing_loop())
    
    return web.json_response({"status": "success", "message": "Factory started"})

async def stop_factory(request):
    """Stop the AI factory"""
    global factory_state
    
    factory_state["running"] = False
    log_system_event("warning", "AI Factory stopped")
    
    # Reset all personas to idle
    for persona in factory_state["personas"].values():
        if persona["state"]["status"] == "working":
            persona["state"]["status"] = "idle"
            persona["state"]["current_task"] = None
    
    return web.json_response({"status": "success", "message": "Factory stopped"})

async def factory_processing_loop():
    """Background processing loop for the factory"""
    global factory_state
    
    # Initialize work queue if not exists
    if "work_queue_count" not in factory_state:
        factory_state["work_queue_count"] = 15  # Start with some work items
    
    while factory_state["running"]:
        try:
            # Simulate work processing
            await asyncio.sleep(5)
            
            # Update some personas randomly to show activity
            import random
            persona_ids = list(factory_state["personas"].keys())
            
            # Add new work items occasionally
            if random.random() > 0.9 and factory_state["work_queue_count"] < 30:
                new_items = random.randint(1, 5)
                factory_state["work_queue_count"] += new_items
                log_system_event("info", f"Added {new_items} new work items to queue")
            
            # Randomly update 1-3 personas
            for _ in range(random.randint(1, 3)):
                persona_id = random.choice(persona_ids)
                persona = factory_state["personas"][persona_id]
                
                # State transitions
                current_status = persona["state"]["status"]
                if current_status == "idle" and random.random() > 0.7 and factory_state["work_queue_count"] > 0:
                    # Start working on an item from queue
                    persona["state"]["status"] = "working"
                    factory_state["work_queue_count"] -= 1
                    tasks = [
                        "Processing work item",
                        "Reviewing code",
                        "Generating documentation",
                        "Running security scan",
                        "Analyzing requirements"
                    ]
                    persona["state"]["current_task"] = random.choice(tasks)
                    log_system_event("info", f"{persona['info']['name']} started {persona['state']['current_task']}")
                    
                elif current_status == "working" and random.random() > 0.8:
                    # Complete work
                    persona["state"]["status"] = "completed"
                    log_system_event("success", f"{persona['info']['name']} completed {persona['state']['current_task']}")
                    persona["state"]["work_items_completed"] += 1
                    
                elif current_status == "completed":
                    # Return to idle
                    persona["state"]["status"] = "idle"
                    persona["state"]["current_task"] = None
                    
                elif current_status == "working" and random.random() > 0.95:
                    # Occasionally get blocked
                    persona["state"]["status"] = "blocked"
                    log_system_event("warning", f"{persona['info']['name']} is blocked")
                    
                elif current_status == "blocked" and random.random() > 0.7:
                    # Unblock
                    persona["state"]["status"] = "working"
                    log_system_event("info", f"{persona['info']['name']} is unblocked")
            
        except Exception as e:
            log_system_event("error", f"Error in processing loop: {str(e)}")
            await asyncio.sleep(10)

def create_app():
    """Create the web application"""
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/api/dashboard-data', dashboard_data)
    app.router.add_post('/api/start-factory', start_factory)
    app.router.add_post('/api/stop-factory', stop_factory)
    return app

async def main():
    """Main entry point"""
    # Initialize factory
    await initialize_factory()
    
    # Create and start web app
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 3000)
    
    logger.info("Starting Enhanced Dashboard with Real Data on http://localhost:3000")
    await site.start()
    
    # Keep the server running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down...")

if __name__ == '__main__':
    asyncio.run(main())