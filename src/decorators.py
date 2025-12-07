import time
from functools import wraps
from typing import Callable, Any

# 6. Использование декораторов (0.25)
# 7. Использование собственного декоратора (0.25)

def retry(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                        continue
            raise last_exception
        return wrapper
    return decorator

def timing(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"⏱️ {func.__name__} выполнено за {end_time - start_time:.2f} секунд")
        return result
    return wrapper

def log_execution(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        print(f"🔧 Выполняется {func.__name__}...")
        result = func(*args, **kwargs)
        print(f"✅ {func.__name__} завершено успешно")
        return result
    return wrapper