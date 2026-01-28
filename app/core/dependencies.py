"""
ONI v2.0 - Simple Dependency Injection Container
Enhanced with has() method
"""
from typing import Any, TypeVar, Generic

import structlog

logger = structlog.get_logger()

T = TypeVar("T")


class ServiceNotFoundError(Exception):
    """Raised when a requested service is not found."""
    pass


class Container:
    """
    Simple dependency injection container.
    
    Features:
    - Singleton instance registration
    - Factory registration for lazy instantiation
    - Type-safe retrieval
    """
    
    def __init__(self) -> None:
        self._instances: dict[str, Any] = {}
        self._factories: dict[str, tuple[type, dict[str, Any]]] = {}
    
    def register(self, name: str, instance: Any) -> None:
        """
        Register a singleton instance.
        
        Args:
            name: Service name
            instance: Service instance
        """
        self._instances[name] = instance
        logger.debug("service_registered", name=name, type=type(instance).__name__)
    
    def register_factory(
        self,
        name: str,
        factory_class: type[T],
        **kwargs: Any,
    ) -> None:
        """
        Register a factory for lazy instantiation.
        
        Args:
            name: Service name
            factory_class: Class to instantiate
            **kwargs: Constructor arguments
        """
        self._factories[name] = (factory_class, kwargs)
        logger.debug("factory_registered", name=name, type=factory_class.__name__)
    
    def has(self, name: str) -> bool:
        """
        Check if a service is registered.
        
        Args:
            name: Service name
            
        Returns:
            True if service exists
        """
        return name in self._instances or name in self._factories
    
    def get(self, name: str, expected_type: type[T] | None = None) -> T:
        """
        Get a service by name.
        
        Args:
            name: Service name
            expected_type: Optional type for validation
            
        Returns:
            Service instance
            
        Raises:
            ServiceNotFoundError: If service not found
            TypeError: If type mismatch
        """
        # Check instances first
        if name in self._instances:
            instance = self._instances[name]
            if expected_type and not isinstance(instance, expected_type):
                raise TypeError(
                    f"Service '{name}' is {type(instance).__name__}, "
                    f"expected {expected_type.__name__}"
                )
            return instance
        
        # Check factories
        if name in self._factories:
            factory_class, kwargs = self._factories[name]
            instance = factory_class(**kwargs)
            self._instances[name] = instance
            del self._factories[name]
            logger.debug("service_instantiated", name=name)
            return instance
        
        raise ServiceNotFoundError(f"Service not found: {name}")
    
    def get_optional(self, name: str, default: T | None = None) -> T | None:
        """
        Get a service or return default if not found.
        
        Args:
            name: Service name
            default: Default value if not found
            
        Returns:
            Service instance or default
        """
        try:
            return self.get(name)
        except ServiceNotFoundError:
            return default
    
    def remove(self, name: str) -> None:
        """Remove a service."""
        self._instances.pop(name, None)
        self._factories.pop(name, None)
    
    def clear(self) -> None:
        """Clear all services."""
        self._instances.clear()
        self._factories.clear()
    
    def list_services(self) -> list[str]:
        """List all registered service names."""
        return list(self._instances.keys()) + list(self._factories.keys())


# Global container instance
container = Container()
