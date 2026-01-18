import requests, os, re, sys, json, time, random, threading
from datetime import datetime, timezone, timedelta
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess  # For direct TTS using espeak-ng

# Session object
ses = requests.Session()

# Random user agents
ua_list = [
    "Mozilla/5.0 (Linux; Android 10; Wildfire E Lite Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/105.0.5195.136 Mobile Safari/537.36[FBAN/EMA;FBLC/en_US;FBAV/298.0.0.10.115;]",
    "Mozilla/5.0 (Linux; Android 11; KINGKONG 5 Pro Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36[FBAN/EMA;FBLC/fr_FR;FBAV/320.0.0.12.108;]",
    "Mozilla/5.0 (Linux; Android 11; G91 Pro Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/106.0.5249.126 Mobile Safari/537.36[FBAN/EMA;FBLC/fr_FR;FBAV/325.0.1.4.108;]"
]
ua = random.choice(ua_list)

# Function to get current Philippine time
def get_ph_time():
    ph_tz = timezone(timedelta(hours=8))  # UTC+8
    return datetime.now(ph_tz)

# Function to get time-based greeting
def get_greeting(name):
    now = get_ph_time()
    hour = now.hour
    if 5 <= hour < 12:
        return f"Good morning {name}"
    elif 12 <= hour < 17:
        return f"Good afternoon {name}"
    elif 17 <= hour < 21:
        return f"Good evening {name}"
    else:
        return f"Good night {name}"

# Function to speak text using espeak-ng directly
def speak(text):
    try:
        subprocess.run(["espeak-ng", text], check=True)
    except subprocess.CalledProcessError:
        print(color("Voice not available. Ensure espeak-ng is installed.", '91'))
    except FileNotFoundError:
        print(color("espeak-ng not found. Install with 'pkg install espeak-ng'.", '91'))

# Function to get user input with optional voice
def voice_input(prompt, speak_input=True):
    user_input = input(color(prompt, '96'))
    if speak_input:
        speak(user_input)  # Speak what the user typed, unless disabled
    return user_input

# Loading animation function
def loading_animation(duration, message="Loading"):
    chars = "/—\\|"
    for i in range(duration * 10):  # 10 iterations per second
        sys.stdout.write(color(f'\r{message} {chars[i % len(chars)]}', '93'))
        sys.stdout.flush()
        sleep(0.1)
    sys.stdout.write('\r' + ' ' * (len(message) + 2) + '\r')  # Clear line

# Function to speak and print greeting cleanly (only once)
def greet_user(name):
    greeting = get_greeting(name)
    welcome_msg = f"{greeting}, welcome to Facebook Spam by glaiz! How are you today?"
    print(color(f"\n{welcome_msg}", '96'))
    speak(welcome_msg)
    print(color(f"{greeting}! Let's start sharing and make some magic happen!", '92'))

# Colored print helper
def color(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

def banner():
    os.system("clear")
    print(color("""
\033[91m  GGGGG \033[92m L     \033[93m AAA  \033[94m IIIII \033[95mZZZZZ\033[0m
\033[91m G     G\033[92m L    \033[93mA   A \033[94m  I   \033[95m   Z \033[0m
\033[91mG       \033[92mL     \033[93mAAAAA \033[94m  I   \033[95m  Z  \033[0m
\033[91mG   GGG \033[92mL     \033[93mA   A \033[94m  I   \033[95m Z   \033[0m
\033[91m GGGGGG \033[92mLLLLL \033[93mA   A \033[94m IIIII \033[95mZZZZZ\033[0m
""", '94'))  # Vibrant multi-colored logo for GLAIZ

    print(color("Author  : glaiz", '96'))  # Cyan
    print(color("Facebook: https://facebook.com/glaiz", '96'))  # Cyan
    print(color("GitHub  : https://github.com/glaiz", '96'))  # Cyan
    print(color("-" * 50, '90'))  # Grey line

# Function to save cookies and tokens to files
def save_cookies_and_tokens(tokens, cookies_list):
    with open("tokens.txt", "w") as f:
        json.dump(tokens, f)
    with open("cookies.txt", "w") as f:
        json.dump(cookies_list, f)

# Function to add cookies to database manually
def add_cookies_to_db():
    banner()
    print(color("Add Cookies to Database (Manual Input)", '93'))
    try:
        num_cookies = int(voice_input("How many cookies will you add? "))
    except ValueError:
        print(color("Oops, that must be a number. Try again!", '91'))
        return add_cookies_to_db()

    tokens = []
    cookies_list = []

    # Load existing if any
    try:
        with open("tokens.txt", "r") as f:
            existing_tokens = json.load(f)
        with open("cookies.txt", "r") as f:
            existing_cookies = json.load(f)
    except FileNotFoundError:
        existing_tokens = []
        existing_cookies = []

    for i in range(num_cookies):
        loading_animation(2, f"Getting ready for cookie {i+1}")
        cookie_input = voice_input(f"Enter cookie {i+1}: ", speak_input=False)
        cookies = {j.split("=")[0]: j.split("=")[1] for j in cookie_input.split("; ") if "=" in j}

        try:
            data = ses.get("https://business.facebook.com/business_locations", headers={
                "user-agent": ua,
                "referer": "https://www.facebook.com/",
                "host": "business.facebook.com",
                "origin": "https://business.facebook.com",
                "upgrade-insecure-requests": "1",
                "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "max-age=0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "content-type": "text/html; charset=utf-8"
            }, cookies=cookies, timeout=10)

            find_token = re.search(r"(EAAG\w+)", data.text)
            if not find_token:
                print(color(f"\n❌ Token extraction failed for cookie {i+1}. Skipping.", '91'))
                continue

            token = find_token.group(1)
            tokens.append(token)
            cookies_list.append(cookies)
            print(color(f"\n✅ Token found for cookie {i+1}: {token}", '92'))

        except Exception as e:
            print(color(f"Error with cookie {i+1}: {e}", '91'))

    # Append to existing
    existing_tokens.extend(tokens)
    existing_cookies.extend(cookies_list)

    # Save back
    save_cookies_and_tokens(existing_tokens, existing_cookies)

    print(color(f"Added {len(tokens)} cookies to database. Total now: {len(existing_tokens)}", '92'))
    time.sleep(2)

# Function to view and remove cookies from database
def view_and_remove_cookies():
    banner()
    print(color("View and Remove Cookies from Database", '93'))
    try:
        with open("tokens.txt", "r") as f:
            tokens = json.load(f)
        with open("cookies.txt", "r") as f:
            cookies_list = json.load(f)
    except FileNotFoundError:
        print(color("No database found. Nothing to view or remove.", '91'))
        time.sleep(2)
        return

    total = len(cookies_list)
    print(color(f"Total cookies in database: {total}", '92'))
    # Assuming all are live initially; dead are removed during sharing
    live = total
    dead = 0  # Will be updated if we check, but for now, assume live
    print(color(f"Live cookies: {live}", '92'))
    print(color(f"Dead/Suspended cookies: {dead}", '91'))

    if total == 0:
        print(color("No cookies to display.", '91'))
        time.sleep(2)
        return

    print(color("Listing cookies (showing first 10 chars of token for brevity):", '96'))
    for i, token in enumerate(tokens):
        print(color(f"{i+1}. Token: {token[:10]}... Cookie keys: {list(cookies_list[i].keys())}", '96'))

    try:
        indices_to_remove = voice_input("Enter the numbers of cookies to remove (comma-separated, e.g., 1,3,5) or 'none': ").strip()
        if indices_to_remove.lower() != 'none':
            indices = [int(x.strip()) - 1 for x in indices_to_remove.split(',') if x.strip().isdigit()]
            indices = [i for i in indices if 0 <= i < total]
            indices.sort(reverse=True)  # Remove from end to start
            for idx in indices:
                tokens.pop(idx)
                cookies_list.pop(idx)
            save_cookies_and_tokens(tokens, cookies_list)
            print(color(f"Removed {len(indices)} cookies. Remaining: {len(tokens)}", '92'))
    except ValueError:
        print(color("Invalid input. No removals made.", '91'))

    time.sleep(2)

# Main menu
def main_menu():
    banner()
    print(color("Main Menu", '96'))
    print(color("1. Add Cookies to Database (Manual Input)", '92'))
    print(color("2. View and Remove Cookies from Database", '92'))
    print(color("3. Start Sharing (Load from Database or Manual)", '92'))
    print(color("4. Exit", '91'))
    choice = voice_input("Choose an option (1/2/3/4): ").strip()
    if choice == '1':
        add_cookies_to_db()
        main_menu()
    elif choice == '2':
        view_and_remove_cookies()
        main_menu()
    elif choice == '3':
        login()
    elif choice == '4':
        print(color("Goodbye!", '92'))
        sys.exit()
    else:
        print(color("Invalid choice. Try again.", '91'))
        main_menu()

def login():
    banner()
    name = voice_input("Hey there! What's your name? ")
    greet_user(name)
    choice = voice_input("Do you want to load cookies from database or enter new ones? (load/manual): ").strip().lower()
    tokens = []
    cookies_list = []
    if choice == 'load':
        try:
            with open("tokens.txt", "r") as f:
                saved_tokens = json.load(f)
            with open("cookies.txt", "r") as f:
                saved_cookies = json.load(f)
            num_saved = len(saved_cookies)
            print(color(f"There are {num_saved} cookies in the database (all assumed live initially).", '92'))
            if num_saved == 0:
                print(color("No saved cookies. Switching to manual input.", '91'))
                choice = 'manual'
            else:
                try:
                    num_use = int(voice_input(f"How many cookies from database do you want to use? (max: {num_saved}): "))
                    if num_use > num_saved:
                        num_use = num_saved
                    elif num_use < 1:
                        num_use = 1
                    tokens = saved_tokens[:num_use]
                    cookies_list = saved_cookies[:num_use]
                    print(color(f"Loaded {num_use} cookies from database.", '92'))
                except ValueError:
                    print(color("Invalid number. Using all saved cookies.", '91'))
                    tokens = saved_tokens
                    cookies_list = saved_cookies
        except FileNotFoundError:
            print(color("No database found. Switching to manual input.", '91'))
            choice = 'manual'
    if choice == 'manual' or choice != 'load':
        print(color("Enter your Facebook cookies here (multiple allowed)", '93'))
        try:
            num_cookies = int(voice_input("How many cookies will you enter? "))
        except ValueError:
            print(color("Oops, that must be a number, not nonsense. Let's try again!", '91'))
            return login()

        for i in range(num_cookies):
            loading_animation(2, f"Getting ready for cookie {i+1}")
            cookie_input = voice_input(f"Enter cookie {i+1}: ", speak_input=False)
            cookies = {j.split("=")[0]: j.split("=")[1] for j in cookie_input.split("; ") if "=" in j}

            try:
                data = ses.get("https://business.facebook.com/business_locations", headers={
                    "user-agent": ua,
                    "referer": "https://www.facebook.com/",
                    "host": "business.facebook.com",
                    "origin": "https://business.facebook.com",
                    "upgrade-insecure-requests": "1",
                    "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                    "cache-control": "max-age=0",
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "content-type": "text/html; charset=utf-8"
                }, cookies=cookies, timeout=10)

                find_token = re.search(r"(EAAG\w+)", data.text)
                if not find_token:
                    print(color(f"\n❌ Token extraction failed for cookie {i+1}. Please check your cookie.", '91'))
                    continue

                token = find_token.group(1)
                tokens.append(token)
                cookies_list.append(cookies)
                print(color(f"\n✅ Token found for cookie {i+1}: {token}", '92'))

            except Exception as e:
                print(color(f"Error with cookie {i+1}: {e}", '91'))

        if tokens:
            save_cookies_and_tokens(tokens, cookies_list)

    if not tokens:
        print(color("No valid cookies found. Let's try again!", '91'))
        return login()

    print(color("Great! Setup complete. Starting the bot now...", '92'))
    time.sleep(3)
    bot()

def share_post(token, cookie, link, n, start_time, suspended_cookies):
    try:
        # Add random delay to avoid detection (0.5 to 2 seconds)
        sleep(random.uniform(0.5, 2.0))
        post = ses.post(
            f"https://graph.facebook.com/v13.0/me/feed?link={link}&published=0&access_token={token}",
            headers={
                "authority": "graph.facebook.com",
                "cache-control": "max-age=0",
                "sec-ch-ua-mobile": "?0",
                "user-agent": ua
            }, cookies=cookie, timeout=10
        ).text

        data = json.loads(post)
        if "id" in data:
            elapsed = str(datetime.now() - start_time).split('.')[0]
            print(color(f"*--> {n}. Sharing in progress, hang tight! ({elapsed})", '92'))
            return True
        else:
            error_msg = data.get('error', {}).get('message', 'Unknown error')
            if 'suspended' in error_msg.lower() or 'blocked' in error_msg.lower() or 'rate limit' in error_msg.lower():
                print(color(f"*--> {n}. Cookie suspended/blocked: {error_msg}. Marking for removal.", '91'))
                suspended_cookies.append(cookie)
                return False
            else:
                print(color(f"*--> {n}. Failed: {error_msg}", '91'))
                return False
    except json.JSONDecodeError:
        print(color(f"*--> {n}. Invalid response from server.", '91'))
        return False
    except requests.exceptions.Timeout:
        print(color(f"*--> {n}. Request timed out.", '91'))
        return False
    except requests.exceptions.ConnectionError:
        print(color(f"*--> {n}. Connection error.", '91'))
        return False
    except Exception as e:
        print(color(f"*--> {n}. Unexpected error: {e}", '91'))
        return False

def bot():
    os.system("clear")
    banner()
    try:
        with open("tokens.txt", "r") as f:
            tokens = json.load(f)
        with open("cookies.txt", "r") as f:
            cookies_list = json.load(f)
    except:
        if os.path.exists("tokens.txt"): os.remove("tokens.txt")
        if os.path.exists("cookies.txt"): os.remove("cookies.txt")
        print(color("Your cookies have expired. Let's log in again!", '91'))
        return login()

    while True:
        link = voice_input("Enter the post link you want to share: ", speak_input=False)
        try:
            limitasyon = int(voice_input("How many shares would you like? "))
        except ValueError:
            print(color("That must be a number, not nonsense. Let's try again!", '91'))
            continue

        print(color("Awesome! Starting the sharing process, please wait...", '93'))
        start_time = datetime.now()

        chunk_size = 200  # Every 200 shares
        cooldown = 10
        suspended_cookies = []

        with ThreadPoolExecutor(max_workers=50) as executor:
            n = 1
            while n <= limitasyon:
                futures = []
                for _ in range(min(chunk_size, limitasyon - n + 1)):
                    available_cookies = [c for c in cookies_list if c not in suspended_cookies]
                    if not available_cookies:
                        print(color("All cookies suspended. Stopping shares.", '91'))
                        break
                    cookie = random.choice(available_cookies)
                    idx = cookies_list.index(cookie)
                    token = tokens[idx]
                    futures.append(
                        executor.submit(
                            share_post,
                            token,
                            cookie,
                            link,
                            n,
                            start_time,
                            suspended_cookies
                        )
                    )
                    n += 1

                for future in as_completed(futures):
                    future.result()

                if n <= limitasyon:
                    print(color(f"Cooldown for {cooldown} seconds to avoid spam detection...", '93'))
                    time.sleep(cooldown)

        # Remove suspended cookies from database
        if suspended_cookies:
            print(color("Cleaning suspended cookies from database...", '93'))
            new_tokens = []
            new_cookies = []
            for i, c in enumerate(cookies_list):
                if c not in suspended_cookies:
                    new_cookies.append(c)
                    new_tokens.append(tokens[i])
            save_cookies_and_tokens(new_tokens, new_cookies)
            print(color(f"Removed {len(cookies_list) - len(new_cookies)} suspended cookies.", '92'))

        print(color("Sharing task completed!", '92'))

        again = voice_input("Do you want to share another link? (y/n): ").strip().lower()
        if again != 'y':
            print(color("Returning to main menu...", '96'))
            time.sleep(2)
            return main_menu()

# Program entry point
if __name__ == "__main__":
    main_menu()