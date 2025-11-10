#!/usr/bin/env python3
"""
dashboard.py - Web Interface and Dashboard Module

This module handles the web interface and dashboard rendering
for the Hugging Face model monitor.
"""

from datetime import datetime
import json
from typing import Any, Dict, List


class WebInterface:
    """
    Handles web interface operations and data preparation.
    Demonstrates separation of concerns - only handles web-related operations.
    """

    def __init__(self):
        """Initialize the web interface."""
        self.theme = "dark"
        self.refresh_interval = 30  # seconds
        self.max_displayed_models = 10

    def prepare_dashboard_data(self, models: List[Any]) -> Dict[str, Any]:
        """
        Prepare data for dashboard display.

        Args:
            models: List of model objects

        Returns:
            Dict: Formatted data for dashboard
        """
        dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "theme": self.theme,
            "refresh_interval": self.refresh_interval,
            "models": [],
            "summary": {
                "total_models": len(models),
                "active_models": 0,
                "total_size_mb": 0,
                "average_downloads": 0,
            },
            "charts": self._prepare_chart_data(models),
        }

        # Process model data
        total_downloads = 0
        for model in models[: self.max_displayed_models]:
            model_data = self._format_model_for_display(model)
            dashboard_data["models"].append(model_data)

            # Update summary
            if model_data["status"] == "active":
                dashboard_data["summary"]["active_models"] += 1

            if model_data["size_mb"]:
                dashboard_data["summary"]["total_size_mb"] += model_data["size_mb"]

            if model_data["downloads"]:
                total_downloads += model_data["downloads"]

        # Calculate averages
        if len(models) > 0:
            avg_downloads = total_downloads / len(models)
            dashboard_data["summary"]["average_downloads"] = avg_downloads

        return dashboard_data

    def _format_model_for_display(self, model: Any) -> Dict[str, Any]:
        """Format a single model for dashboard display."""
        if hasattr(model, "get_display_info"):
            display_info = model.get_display_info()
        else:
            display_info = {
                "name": getattr(model, "name", "Unknown"),
                "task": getattr(model, "task_type", "Unknown"),
                "library": getattr(model, "library", "Unknown"),
                "size": "Unknown",
                "downloads": "Unknown",
            }

        return {
            "name": display_info.get("name", "Unknown"),
            "task_type": display_info.get("task", "Unknown"),
            "library": display_info.get("library", "Unknown"),
            "size_mb": self._extract_size_mb(display_info.get("size", "0")),
            "downloads": self._extract_downloads(display_info.get("downloads", "0")),
            "status": "active",  # Default status
            "health_score": 85,  # Mock health score
            "last_updated": datetime.now().strftime("%H:%M:%S"),
        }

    def _extract_size_mb(self, size_str: str) -> float:
        """Extract size in MB from size string."""
        try:
            if "MB" in str(size_str):
                return float(str(size_str).replace("MB", "").strip())
            return 0.0
        except (ValueError, AttributeError):
            return 0.0

    def _extract_downloads(self, downloads_str: str) -> int:
        """Extract downloads count from downloads string."""
        try:
            # Remove commas and convert to int
            return int(str(downloads_str).replace(",", "").replace("Unknown", "0"))
        except (ValueError, AttributeError):
            return 0

    def _prepare_chart_data(self, models: List[Any]) -> Dict[str, Any]:
        """Prepare data for dashboard charts."""
        task_distribution = {}
        library_distribution = {}
        size_ranges = {
            "Small (<100MB)": 0,
            "Medium (100-500MB)": 0,
            "Large (>500MB)": 0,
        }

        for model in models:
            # Task distribution
            task = getattr(model, "task_type", "Unknown")
            task_distribution[task] = task_distribution.get(task, 0) + 1

            # Library distribution
            library = getattr(model, "library", "Unknown")
            library_distribution[library] = library_distribution.get(library, 0) + 1

            # Size distribution
            size_mb = getattr(model, "size_mb", 0) or 0
            if size_mb < 100:
                size_ranges["Small (<100MB)"] += 1
            elif size_mb < 500:
                size_ranges["Medium (100-500MB)"] += 1
            else:
                size_ranges["Large (>500MB)"] += 1

        return {
            "task_distribution": task_distribution,
            "library_distribution": library_distribution,
            "size_distribution": size_ranges,
            "performance_trends": self._mock_performance_trends(),
        }

    def _mock_performance_trends(self) -> Dict[str, List[float]]:
        """Generate mock performance trend data."""
        import secrets

        # Generate 24 hours of mock data (hourly)
        hours = 24
        rng = secrets.SystemRandom()
        memory_trend = [rng.uniform(200, 800) for _ in range(hours)]
        cpu_trend = [rng.uniform(10, 60) for _ in range(hours)]
        response_time_trend = [rng.uniform(50, 200) for _ in range(hours)]

        return {
            "memory_usage": memory_trend,
            "cpu_usage": cpu_trend,
            "response_time": response_time_trend,
            "labels": [f"{i:02d}:00" for i in range(hours)],
        }

    def generate_api_response(
        self, data: Dict[str, Any], status: str = "success"
    ) -> str:
        """
        Generate a JSON API response.

        Args:
            data: Data to include in response
            status: Response status

        Returns:
            str: JSON formatted response
        """
        response = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }

        return json.dumps(response, indent=2, default=str)

    def set_theme(self, theme: str):
        """Set the dashboard theme."""
        if theme in ["light", "dark", "auto"]:
            self.theme = theme


class DashboardRenderer:
    """
    Renders HTML dashboard from prepared data.
    Demonstrates single responsibility principle - only handles rendering.
    """

    def __init__(self):
        """Initialize the dashboard renderer."""
        self.template_cache = {}

    def render_dashboard(self, dashboard_data: Dict[str, Any]) -> str:
        """
        Render the complete HTML dashboard.

        Args:
            dashboard_data: Prepared dashboard data

        Returns:
            str: Complete HTML dashboard
        """
        html_template = self._get_html_template()

        # Replace placeholders with actual data
        html_content = html_template.format(
            title="Hugging Face Model Monitor",
            timestamp=dashboard_data.get("timestamp", ""),
            total_models=dashboard_data["summary"]["total_models"],
            active_models=dashboard_data["summary"]["active_models"],
            total_size=f"{dashboard_data['summary']['total_size_mb']:.1f}",
            avg_downloads=f"{dashboard_data['summary']['average_downloads']:.0f}",
            models_table=self._render_models_table(dashboard_data["models"]),
            charts_script=self._render_charts_script(dashboard_data["charts"]),
            theme_class=dashboard_data.get("theme", "dark"),
            # Convert refresh interval to milliseconds
            refresh_interval=dashboard_data.get("refresh_interval", 30) * 1000,
        )

        return html_content

    def _get_html_template(self) -> str:
        """Get the HTML template for the dashboard."""
        return """<!DOCTYPE html>
<html lang="en" class="{theme_class}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --bg-color: #1a1a1a;
            --text-color: #e0e0e0;
            --card-bg: #2d2d2d;
            --border-color: #444;
            --accent-color: #007acc;
            --success-color: #4caf50;
            --warning-color: #ff9800;
            --error-color: #f44336;
        }}
        
        .light {{
            --bg-color: #ffffff;
            --text-color: #333333;
            --card-bg: #f5f5f5;
            --border-color: #ddd;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            color: var(--accent-color);
            margin-bottom: 10px;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        
        .card h3 {{
            color: var(--accent-color);
            margin-bottom: 10px;
        }}
        
        .card .value {{
            font-size: 2em;
            font-weight: bold;
            color: var(--success-color);
        }}
        
        .models-section {{
            margin-bottom: 30px;
        }}
        
        .models-table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--card-bg);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .models-table th,
        .models-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .models-table th {{
            background: var(--accent-color);
            color: white;
        }}
        
        .status-active {{ color: var(--success-color); }}
        .status-warning {{ color: var(--warning-color); }}
        .status-error {{ color: var(--error-color); }}
        
        .charts-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .chart-container {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            height: 300px;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            border-top: 1px solid var(--border-color);
            color: #888;
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>Last updated: {timestamp}</p>
        </div>
        
        <div class="summary-cards">
            <div class="card">
                <h3>Total Models</h3>
                <div class="value">{total_models}</div>
            </div>
            <div class="card">
                <h3>Active Models</h3>
                <div class="value">{active_models}</div>
            </div>
            <div class="card">
                <h3>Total Size</h3>
                <div class="value">{total_size} MB</div>
            </div>
            <div class="card">
                <h3>Avg Downloads</h3>
                <div class="value">{avg_downloads}</div>
            </div>
        </div>
        
        <div class="models-section">
            <h2>Model Status</h2>
            {models_table}
        </div>
        
        <div class="charts-section">
            <div class="chart-container">
                <canvas id="taskChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="performanceChart"></canvas>
            </div>
        </div>
        
        <div class="footer">
            <p>Hugging Face Model Monitor - Auto-refresh every {refresh_interval}ms</p>
        </div>
    </div>
    
    <script>
        {charts_script}
        
        // Auto-refresh functionality
        setTimeout(function() {{
            location.reload();
        }}, {refresh_interval});
    </script>
</body>
</html>"""

    def _render_models_table(self, models: List[Dict[str, Any]]) -> str:
        """Render the models table HTML."""
        if not models:
            return "<p>No models to display</p>"

        table_html = """<table class="models-table">
<thead>
    <tr>
        <th>Model Name</th>
        <th>Task</th>
        <th>Library</th>
        <th>Size (MB)</th>
        <th>Downloads</th>
        <th>Status</th>
        <th>Health</th>
        <th>Last Updated</th>
    </tr>
</thead>
<tbody>"""

        for model in models:
            status_class = f"status-{model['status']}"
            table_html += f"""
    <tr>
        <td>{model["name"]}</td>
        <td>{model["task_type"]}</td>
        <td>{model["library"]}</td>
        <td>{model["size_mb"]:.1f}</td>
        <td>{model["downloads"]:,}</td>
        <td class="{status_class}">{model["status"]}</td>
        <td>{model["health_score"]}%</td>
        <td>{model["last_updated"]}</td>
    </tr>"""

        table_html += """
</tbody>
</table>"""

        return table_html

    def _render_charts_script(self, charts_data: Dict[str, Any]) -> str:
        """Render the JavaScript for charts."""
        return f"""
        // Task Distribution Chart
        const taskCtx = document.getElementById('taskChart').getContext('2d');
        new Chart(taskCtx, {{
            type: 'pie',
            data: {{
                labels: {list(charts_data["task_distribution"].keys())},
                datasets: [{{
                    data: {list(charts_data["task_distribution"].values())},
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Task Distribution'
                    }},
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // Performance Trends Chart
        const perfCtx = document.getElementById('performanceChart').getContext('2d');
        new Chart(perfCtx, {{
            type: 'line',
            data: {{
                labels: {charts_data["performance_trends"]["labels"]},
                datasets: [{{
                    label: 'Memory Usage (MB)',
                    data: {charts_data["performance_trends"]["memory_usage"]},
                    borderColor: '#36A2EB',
                    tension: 0.1
                }}, {{
                    label: 'CPU Usage (%)',
                    data: {charts_data["performance_trends"]["cpu_usage"]},
                    borderColor: '#FF6384',
                    tension: 0.1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Performance Trends (24h)'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        """


class MenuSystem:
    """
    Handles console-based menu system for the application.
    Demonstrates user interface abstraction.
    """

    def __init__(self):
        """Initialize the menu system."""
        self.menu_options = {
            "1": ("View Models", self._view_models),
            "2": ("Add Model", self._add_model),
            "3": ("Remove Model", self._remove_model),
            "4": ("Generate Report", self._generate_report),
            "5": ("View Performance", self._view_performance),
            "6": ("Settings", self._settings),
            "0": ("Exit", self._exit),
        }

    def display_main_menu(self):
        """Display the main menu."""
        print("\n" + "=" * 50)
        print("    HUGGING FACE MODEL MONITOR")
        print("=" * 50)

        for key, (description, _) in self.menu_options.items():
            print(f"{key}. {description}")

        print("\nSelect an option (0 to exit):")

    def handle_menu_selection(self, choice: str) -> bool:
        """
        Handle menu selection.

        Args:
            choice: User's menu choice

        Returns:
            bool: True to continue, False to exit
        """
        if choice in self.menu_options:
            _, handler = self.menu_options[choice]
            return handler()
        else:
            print("Invalid option. Please try again.")
            return True

    def _view_models(self) -> bool:
        """Handle view models option."""
        print("\n--- Model List ---")
        print("This would display all monitored models")
        input("Press Enter to continue...")
        return True

    def _add_model(self) -> bool:
        """Handle add model option."""
        print("\n--- Add New Model ---")
        print("This would allow adding a new model to monitor")
        input("Press Enter to continue...")
        return True

    def _remove_model(self) -> bool:
        """Handle remove model option."""
        print("\n--- Remove Model ---")
        print("This would allow removing a model from monitoring")
        input("Press Enter to continue...")
        return True

    def _generate_report(self) -> bool:
        """Handle generate report option."""
        print("\n--- Generate Report ---")
        print("This would generate a performance report")
        input("Press Enter to continue...")
        return True

    def _view_performance(self) -> bool:
        """Handle view performance option."""
        print("\n--- Performance Metrics ---")
        print("This would show detailed performance metrics")
        input("Press Enter to continue...")
        return True

    def _settings(self) -> bool:
        """Handle settings option."""
        print("\n--- Settings ---")
        print("This would allow configuring application settings")
        input("Press Enter to continue...")
        return True

    def _exit(self) -> bool:
        """Handle exit option."""
        print("\nThank you for using Hugging Face Model Monitor!")
        return False


# Utility functions for UI operations
def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        str: Formatted size string
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration in human readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        str: Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def create_progress_bar(current: int, total: int, width: int = 30) -> str:
    """
    Create a text-based progress bar.

    Args:
        current: Current progress
        total: Total items
        width: Width of progress bar

    Returns:
        str: Progress bar string
    """
    if total == 0:
        progress = 0
    else:
        progress = current / total

    filled = int(width * progress)
    bar = "█" * filled + "░" * (width - filled)
    percentage = progress * 100

    return f"[{bar}] {percentage:.1f}% ({current}/{total})"
