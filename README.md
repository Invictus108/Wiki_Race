# Wikipedia Path Finder

This project is a Python Flask web application that utilizes **double-ended Breadth-First Search (BFS)** and the **Wikipedia API** to find the shortest path between two Wikipedia pages. The application allows users to enter a starting and target Wikipedia page, and it returns the sequence of pages (links) that form the shortest path between them.

## Features

- **Shortest Path Search**: Uses double-ended BFS to efficiently find the shortest path between two Wikipedia pages by exploring both pages simultaneously from both directions.
- **Wikipedia API Integration**: Retrieves page links and content dynamically using the Wikipedia API.
- **Flask Web Interface**: Provides a user-friendly web interface built on Flask for entering page titles and viewing results.
- **Real-time Processing**: Displays the shortest path in real-time, allowing users to quickly understand the relationship between two topics on Wikipedia.

## How It Works

1. **Input Pages**: Users provide the starting Wikipedia page and the target Wikipedia page via a simple web form.
   
2. **Double-Ended BFS**: The application uses a double-ended BFS algorithm, where the search proceeds simultaneously from both the start and target pages. This reduces the search space and improves performance compared to a single-ended BFS.
   
3. **Wikipedia API**: The algorithm interacts with the Wikipedia API to retrieve the hyperlinks of each page as nodes in the search graph.

4. **Shortest Path Result**: Once a path is found, the application displays the series of Wikipedia pages that connect the two input pages.

### Installation
   ```bash
   git clone https://github.com/your-username/wikipedia-path-finder.git
   cd wikipedia-path-finder
   pip install -r requirements.txt
   flask run
