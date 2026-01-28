"""
ONI Shape Executor Service v2.0 (Refactored Phase 2)
Forwarding shim ensuring backward compatibility with new modular architecture.
"""
from app.services.oni.shape_executor.types import ShapeType, ShapeCommand
from app.services.oni.shape_executor.base import AppAdapter
from app.services.oni.shape_executor.adapters.photoshop import PhotoshopAdapter
from app.services.oni.shape_executor.adapters.corel import CorelDRAWAdapter
from app.services.oni.shape_executor.adapters.illustrator import IllustratorAdapter
from app.services.oni.shape_executor.service import ShapeExecutorService
