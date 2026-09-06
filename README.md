# Astar-algorithm
The Astar algorithm is a type of pathfinding algorithm that searches for the target using a 'sense of direction' _(h-cost)_ in addition to a movement cost between nodes _(g-cost)_. In other words, this algorithm is designed for weighted graphs where the algorithm carefully selects each node on the graph with the lowest weight. This results in one of the fastest search algorithms because it does not waste time searching for nodes that are irrelevant.

## implementation
I created this algorithm based on my understanding from youtube videos and countless months of research using A.I and websites.

-**Version 1:** relies on pygame.Rect objects and their positions which adds a slight overhead due to its collision mechanic for detecting neighbors on the map.

-**Version 2:** I implemented a grid system array of the map where the algorithm navigates by indexing specific locations on the map which is constant time lookup O(1).
 
## performance
After many optimizations, the latest version performs on average 5-7ms faster than my old version.

Feel free to check out my code and let me know your thoughts. 




