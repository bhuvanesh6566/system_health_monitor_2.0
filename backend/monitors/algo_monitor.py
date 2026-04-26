import time
import random

def run_dummy_algorithm():
    """
    Runs a light sorting task and returns execution time in milliseconds (ms).
    """
    try:
        data_size = 5000  # Reduced from 20000 for faster response
        random_list = [random.randint(0, 100000) for _ in range(data_size)]
        start_time = time.time()
        sorted_list = sorted(random_list)
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        return round(duration_ms, 2)
    except Exception as e:
        print(f"Algorithm Error: {e}")
        return 0

# Test the function if run directly
if __name__ == "__main__":
    print(f"Algorithm Execution Time: {run_dummy_algorithm()} ms")