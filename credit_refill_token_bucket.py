# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor
import time
import threading
from threading import Semaphore, Lock, Thread
import datetime

# Constants for rate-limiting
REFILL_RATE = 60  # Time window in seconds for MAX_CALLS
call_count = 0  # Current number of API calls
lock = threading.Lock()  # To ensure thread-safety for shared data
total_elapsed_time = 0
Total_credits = Max_Rate = 15
credit_lock = Lock()
MAX_THREADS = 5


def print_with_date(message):
  now = datetime.datetime.now()
  formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
  print(f"[{formatted_date}] {message}")


# Timing function to calculate how long the image generation takes
def check_ratelimit():
    """Each thread checks the total credits; if credits are available, it proceeds, else it waits until credits are refilled."""
    global Total_credits
    while True:
        with credit_lock:
            if Total_credits > 0:
                Total_credits -= 1
                print_with_date(f"Total credits{Total_credits}")
                break
        # Exit lock and wait before checking again
        # total elapsed time is added by each thread so taking the average elapsed time of all threads
        print_with_date(f"Rate limit reached. Sleeping for {REFILL_RATE - (total_elapsed_time/MAX_THREADS)} seconds.")

        time.sleep(REFILL_RATE - (total_elapsed_time/MAX_THREADS))
        continue

def credit_refill():
    """Refills credits to max rate every 60 seconds."""
    global Total_credits
    while True:
        time.sleep(60)
        with credit_lock:
            Total_credits = Max_Rate
            print_with_date(f"Credits refilled: {Total_credits}") #Added to show credit refill
        continue

# Mock data for pages and characters
pages = [{"image_prompt": f"Image {i}"} for i in range(17)]
characters = [{"character_name": "Hero", "character_features": "Tall, strong"}]

# Timing function to calculate how long the image generation takes
def generate_image(page, characters, image_style):
    global call_count, total_elapsed_time
    start_time = time.time()

    # Mock the rate-limiting logic
    check_ratelimit()
    time.sleep(10)  # Simulating a 10-second API call delay

    # Mock the image URL
    image_url = f"https://mock_image_url/{page['image_prompt']}.png"
    page["image_url"] = image_url

    # Calculate and print time taken
    end_time = time.time()
    time_spent = end_time - start_time
    print_with_date(f"Image generated for {page['image_prompt']} in {time_spent:.2f} seconds.\n")

    with lock:

        total_elapsed_time += time_spent

    return page

# Function to handle the image generation for the book pages
def generate_images_for_picture_book(image_style="default"):
    start_time = time.time()
    print_with_date("Starting image generation...")
    refill_thread = Thread(target=credit_refill)
    refill_thread.start()
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(generate_image, page, characters, image_style) for page in pages]

        # Collect results and handle errors
        for i, future in enumerate(futures):
            try:
                result = future.result()
                #print(f"Result for page {i}: {result}")
            except Exception as e:
                print_with_date(f"Failed to generate image for page {i}: {str(e)}")

    end_time = time.time()
    time_taken = end_time - start_time
    print_with_date(f"All images generated in {time_taken:.2f} seconds.")

# Run the function to test the implementation
generate_images_for_picture_book()

