import requests
import time
import urllib

class deque:
    def __init__(self, size):
        self.forward = 0
        self.size = size
        self.deque = [None] * size
        self.count = 0

    def append_left(self, element):
        if self.count >= self.size:
            self.alloc()
        self.forward = (self.forward - 1) % self.size
        self.deque[self.forward] = element
        self.count += 1

    def append_right(self, element):
        if self.count >= self.size:
            self.alloc()
        index = (self.count + self.forward) % self.size
        self.deque[index] = element
        self.count += 1

    def pop_left(self):
        if self.count == 0:
            return None
        value = self.deque[self.forward]
        self.forward = (self.forward + 1) % self.size
        self.count -= 1
        if self.count < self.size // 2 and self.size > 1:
            self.free()
        return value


    def pop_right(self):
        if self.count == 0:
            return None
        value = self.deque[(self.forward + self.count - 1) % self.size]
        self.count -= 1
        if self.count < self.size // 2 and self.size > 1:
            self.free()
        return value
    
    def peek_left(self):
        if self.count == 0:
            return None
        return self.deque[self.forward]

    def peek_right(self):
        if self.count == 0:
            return None
        return self.deque[(self.forward + self.count - 1) % self.size]
        

    def get_count(self):
        return self.count

    def alloc(self):
        new_size = self.size * 2
        tmp = [None] * new_size
        # Reorder elements starting from self.forward
        for i in range(self.count):
            tmp[i] = self.deque[(self.forward + i) % self.size]
        self.deque = tmp
        self.forward = 0  # Reset forward
        self.size = new_size

    def free(self):
        new_size = max(self.size // 2, 1)  # Prevent reducing size to 0
        tmp = [None] * new_size
        for i in range(self.count):
            tmp[i] = self.deque[(self.forward + i) % self.size]
        self.deque = tmp
        self.forward = 0  # Reset forward
        self.size = new_size


class wikiracer:
    def __init__(self, start, end, reverse):
        self.start = start
        self.end = end

        # set deque and initialize with starting node
        self.queue = deque(10)
        self.queue.append_right(self.start)

        # set to check whether a links been visited
        self.visited = set()

        # hash table for path reconstrution 
        self.path = {self.start: [self.start]}

        self.reverse = reverse
        self.id = "Reverse" if self.reverse else "Forward"
        
    
    def search(self):
        arr = []

        current = self.queue.pop_left()

        if self.reverse:
            links = self.get_backlinks(current)
        else:
            links = self.get_links(current)

        for link in links:
            if link not in self.visited:
                self.path[link] = self.path[current] + [link]
            
                self.visited.add(link)
                arr.append(link)
                self.queue.append_right(link)

        return arr

    def get_path(self, link):
        return self.path[link]
    
    def get_links(self, page_title, lang='en'):

        if page_title is None:
            return []

        page_title = page_title.replace("https://en.wikipedia.org/wiki/", "")
       
        S = requests.Session()
        URL = f"https://{lang}.wikipedia.org/w/api.php"

        PARAMS = {
            "action": "query",
            "format": "json",
            "titles": page_title,
            "prop": "links",
            "plnamespace": "0",  
            "pllimit": "max"
        }

        forward_links = []

        while True:
            response = S.get(url=URL, params=PARAMS)

            # Check if the request was successful
            try:
                data = response.json()
            except ValueError:
                print(f"Failed to decode JSON. Status: {response.status_code}, Content: {response.text}")
                return []
                        
            pages = data.get('query', {}).get('pages', {})
            for page_id, page in pages.items():
                for link in page.get('links', []):
                    title = link['title']
                    encoded_title = urllib.parse.quote(title.replace(' ', '_'))
                    full_url = f"https://{lang}.wikipedia.org/wiki/{encoded_title}"
                    forward_links.append(full_url)

            if 'continue' in data:
                PARAMS.update(data['continue'])
            else:
                break

        return forward_links

    def get_backlinks(self, page_title, lang='en'):

        if page_title is None:
            return []

        page_title = page_title.replace("https://en.wikipedia.org/wiki/", "")
       
        S = requests.Session()
        URL = f"https://{lang}.wikipedia.org/w/api.php"

        PARAMS = {
            "action": "query",
            "format": "json",
            "list": "backlinks",
            "bltitle": page_title,
            "bllimit": "max",
            "blnamespace": "0",  # Limit to the main namespace to exclude talk pages, user pages, etc.
        }

        backlinks = []

        while True:
            response = S.get(url=URL, params=PARAMS)

            # Check if the request was successful
            try:
                data = response.json()
            except ValueError:
                print(f"Failed to decode JSON. Status: {response.status_code}, Content: {response.text}")
                return []

            # Extract the titles of the pages that link to the target page and convert them to URLs
            for link in data.get('query', {}).get('backlinks', []): # use.get to avoid KeyError
                title = link['title']
                # Convert each title to a URL-encoded string
                encoded_title = urllib.parse.quote(title.replace(' ', '_'))
                full_url = f"https://{lang}.wikipedia.org/wiki/{encoded_title}"
                backlinks.append(full_url)

            # Check if there is a "continue" page and update the params accordingly
            if 'continue' in data:
                PARAMS['blcontinue'] = data['continue']['blcontinue']
            else:
                break

        return backlinks

def race(start, end):
    hash = {}
    run = True

    # initalize two instance of wiki race, one forward and one backward
    reverse = wikiracer(end, start, True)
    forward = wikiracer(start, end, False)

    start_time = time.time()

    while run:
        # get list of links
        out1 = reverse.search()
        out2 = forward.search()

        # add links to hash and identify convergence points

        for link1 in out1:
            if link1 not in hash:
                # 0 for reverse
                hash[link1] = 0
            else:
                # if value is one it was added by forward and this is thefore a meeting point
                if hash[link1] == 1 and link1 != start:
                    end_time = time.time()
                    print("Meeting Link: ", link1)
                    left_path = forward.get_path(link1)
                    right_path = reverse.get_path(link1)
                    run = False
                    break


        
        if run:
            for link2 in out2:
                if link2 not in hash:
                    # 1 for forward
                    hash[link2] = 1
                else:
                    # if value is 0 than it was added by reverse and is therfore a meeting point
                    if hash[link2] == 0 and link2 != start:
                        end_time = time.time()
                        print("Meeting Link: ", link2)
                        left_path = forward.get_path(link2)
                        right_path = reverse.get_path(link2)
                        run = False
                        break

    
    #format stuff so it looks nice
    right_path_reversed = right_path[::-1]
    
    if len(right_path_reversed) > 0:
        right_path_reversed = right_path_reversed[1:]
    
    # Format and print the full path
    full_path = left_path + right_path_reversed
    message = f"Path Found in {round(end_time - start_time, 2)} seconds of depth {len(left_path) + len(right_path_reversed)}:"
    return [full_path, message]
   