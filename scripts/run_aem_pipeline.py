import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.aem_crawler import crawl
from agents.embed_worker import run_workers
from agents.queue_manager import get_stats

if "--status" in sys.argv:
    print(get_stats())
elif "--embed-only" in sys.argv:
    run_workers()
else:
    crawl()
    run_workers()
