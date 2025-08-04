# Author: 小牛667
# Created: 2025-04-12
import logging
import os
import threading

from django.apps import AppConfig

from main import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Delayed initialization of network sniffer to avoid startup errors
global_sniffer = None


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        # Avoid duplicate thread startup in development mode (runserver loads twice)
        if os.environ.get('RUN_MAIN') != 'true':
            return

        def start_sniffer():
            global global_sniffer
            try:
                from main.monitorTraffic.sniff_network import NetworkSniffer
                global_sniffer = NetworkSniffer(
                    interface=config.INTERFACE,
                    port=config.PORT,
                    model_type=config.MODEL_TYPE
                )
                global_sniffer.start_sniffing()
            except Exception as e:
                logger.error(f"Network sniffer startup failed: {e}")
                logger.info("System will continue running, but network monitoring functionality is unavailable")

        # Start sniffer thread
        sniffer_thread = threading.Thread(target=start_sniffer)
        sniffer_thread.daemon = True  # Set as daemon thread
        sniffer_thread.start()
        logger.info("Attempting to start network sniffer thread...")
