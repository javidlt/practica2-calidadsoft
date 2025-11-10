#!/usr/bin/env python3
"""
Main module for Hugging Face Model Monitor
A simple project to monitor and manage Hugging Face models.
"""

from File1 import ModelInfo, ModelValidator
from File2 import ModelDownloader, ModelManager
from File3 import ConfigManager, StorageManager
from File4 import PerformanceMonitor, MetricsCollector
from File5 import WebInterface, DashboardRenderer

def main():
    """Main function to run the Hugging Face Model Monitor."""
    print("=== Hugging Face Model Monitor ===")
    
    # Initialize components
    config_manager = ConfigManager()
    model_manager = ModelManager()
    storage_manager = StorageManager()
    monitor = PerformanceMonitor()
    dashboard = DashboardRenderer()
    
    # Load configuration
    config = config_manager.load_config()
    print(f"Loaded config: {config.get('models_path', './models')}")
    
    # Create sample models to monitor
    models = [
        ModelInfo("bert-base-uncased", "text-classification", "transformers"),
        ModelInfo("gpt2", "text-generation", "transformers"),
        ModelInfo("distilbert-base-uncased", "text-classification", "transformers")
    ]
    
    # Validate and add models
    validator = ModelValidator()
    for model in models:
        if validator.validate_model(model):
            model_manager.add_model(model)
            print(f"Added model: {model.name}")
    
    # Download models (simulate)
    downloader = ModelDownloader()
    for model in models:
        status = downloader.check_model_status(model.name)
        print(f"Model {model.name} status: {status}")
    
    # Monitor performance
    metrics_collector = MetricsCollector()
    for model in models:
        metrics = metrics_collector.collect_metrics(model)
        monitor.track_performance(model.name, metrics)
        print(f"Collected metrics for {model.name}: {metrics}")
    
    # Generate dashboard
    web_interface = WebInterface()
    dashboard_data = web_interface.prepare_dashboard_data(models)
    dashboard_html = dashboard.render_dashboard(dashboard_data)
    
    # Save dashboard
    storage_manager.save_dashboard(dashboard_html)
    print("Dashboard saved successfully!")
    
    # Display summary
    print("\n=== Monitor Summary ===")
    print(f"Total models tracked: {len(models)}")
    print(f"Models directory: {config.get('models_path', './models')}")
    print("Monitor completed successfully!")

if __name__ == "__main__":
    main()
