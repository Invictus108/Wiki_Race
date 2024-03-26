import requests
import time
import urllib


class wikiracer:
    def __init__(self, start, end, reverse):
        self.start = start
        self.end = end
        self.depth = 0
        self.queue = [[self.start, self.depth]]
        self.visited = []
        self.path = {self.start: [self.start]}
        self.reverse = reverse
        self.id = "Reverse" if self.reverse else "Forward"
        
    
    def search(self):
        arr = []

        #return empty if nothing there
        if(len(self.queue) == 0):
            print(self.id, "Queue empty")
            return arr

        current = self.queue.pop(self.get_index())

        if self.reverse:
            links = self.get_backlinks(current[0])
        else:
            links = self.get_links(current[0])

        for link in links:
            if link not in self.visited:
                self.path[link] = self.path[current[0]] + [link]

                if link == self.end:
                    return self.path[link]
            
                self.visited.append(link)
                arr.append(link)
                self.queue.append([link, self.depth + 1])

        if len(arr) == 0:
            print(self.id, "returned empty... Ignoring")       
        return arr
                

        
    def get_index(self):
        for i in range(len(self.queue)):
            if self.queue[i][1] == self.depth:
                return i
        self.depth += 1
        return self.get_index()


    def get_path(self, link):
        return self.path[link]
    
    def get_links(self, page_title, lang='en'):

        page_title = page_title.replace("https://en.wikipedia.org/wiki/", "")
        """
        Get a list of full URL links to article pages that are linked from the specified Wikipedia page,
        focusing on links within the main namespace (excluding links to talk pages, user pages, etc.).
        
        :param page_title: Title of the Wikipedia page to search for forward links from.
        :param lang: Language edition of Wikipedia, default is 'en' for English.
        :return: List of full URLs to article pages linked from the specified page.
        """
        S = requests.Session()
        URL = f"https://{lang}.wikipedia.org/w/api.php"

        PARAMS = {
            "action": "query",
            "format": "json",
            "titles": page_title,
            "prop": "links",
            "plnamespace": "0",  # Limit to the main namespace
            "pllimit": "max"
        }

        forward_links = []

        while True:
            response = S.get(url=URL, params=PARAMS)
            data = response.json()
            
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

        page_title = page_title.replace("https://en.wikipedia.org/wiki/", "")
        """
        Get a list of full URL links to article pages that link to the specified Wikipedia page,
        excluding talk pages, user pages, etc.
        
        :param page_title: Title of the Wikipedia page to search for backlinks.
        :param lang: Language edition of Wikipedia, default is 'en' for English.
        :return: List of full URLs to article pages linking to the specified page.
        """
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
            data = response.json()

            # Extract the titles of the pages that link to the target page and convert them to URLs
            for link in data['query']['backlinks']:
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
    forward_arr = []
    reverse_arr = []
    run = True

    #need to put reverse in end, start
    reverse = wikiracer(end, start, True)
    forward = wikiracer(start, end, False)

    start_time = time.time()

    while run:
        out1 = reverse.search()
        out2 = forward.search()

        # if not out1:
        #     print("Reverse returned nothing")
        #     return
        
        # if not out2:
        #     print("Forward returned nothing")
        #     return

        for link1 in out1:
            #print("Reverse", link1)
            reverse_arr.append(link1)
        for link2 in out2:
            #print("Forward", link2)
            forward_arr.append(link2)

        for link in reverse_arr:
            if link in forward_arr and link != start:
                end_time = time.time()
                print("Meeting Link: ", link)
                run = False
                left_path = forward.get_path(link)
                right_path = reverse.get_path(link)
                break
    
    #format stuff so it looks nice
    right_path_reversed = right_path[::-1]
    
    if len(right_path_reversed) > 0:
        right_path_reversed = right_path_reversed[1:]
    
    # Format and print the full path
    full_path = left_path + right_path_reversed
    message = f"Path Found in {round(end_time - start_time, 2)} seconds of depth {len(left_path) + len(right_path_reversed)}:"
    return [full_path, message]
   

