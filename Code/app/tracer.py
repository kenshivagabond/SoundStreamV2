import time , functools

def trace_layer(name):
    def decorator(cls):
        # 1. WRAP __SETATTR__ to catch every attribute change
        original_setattr = cls.__setattr__

        def new_setattr(self, key, value):
            print(f"🔄 [{name}] Attribute '{key}' is changing to: {value}")
            start = time.perf_counter()
            # Use object.__setattr__ to avoid infinite recursion
            object.__setattr__(self, key, value)
            print(f"⏱️ [{name}] Assignment took {time.perf_counter() - start:.4f}s")

        cls.__setattr__ = new_setattr

        # 2. WRAP ALL REGULAR METHODS (including __init__)
        for attr_name, attr_value in list(cls.__dict__.items()):
            if callable(attr_value) and attr_name != '__setattr__':
                # Re-apply the original trace_layer to wrap this method
                setattr(cls, attr_name, trace_layer(f"{name}.{attr_name}")(attr_value))

        return cls
    return decorator