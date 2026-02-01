import time
import random

def run_dummy_algorithm():
    """
    Runs a heavy sorting task and returns execution time in milliseconds (ms).
    """
    try:
        # Generate a large list of random numbers (Simulating heavy data load)
        data_size = 20000  # Adjust this number to make it faster/slower
        random_list = [random.randint(0, 100000) for _ in range(data_size)]
        
        # --- TIMER START ---
        start_time = time.time()
        
        # The Heavy Task: Sorting the list
        sorted_list = sorted(random_list)
        
        # --- TIMER END ---
        end_time = time.time()
        
        # Calculate duration in milliseconds
        duration_ms = (end_time - start_time) * 1000
        
        return round(duration_ms, 2)

    except Exception as e:
        print(f"Algorithm Error: {e}")
        return 0

# Test the function if run directly
if __name__ == "__main__":
    print(f"Algorithm Execution Time: {run_dummy_algorithm()} ms")