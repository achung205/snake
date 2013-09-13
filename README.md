snake
=====

classic snake game made in python with the pygame library and implemented using MVC model  
a lot of code was taken from http://ezide.com/games/writing-games.html

currently, the path finding method is inefficient; it recalculates the path every time the snake moves. a way to fix this is to calculate the path once every time an apple is eaten, and have a separate "obstacle avoiding" AI so that it doesnt run into itself

note: the game is designed to redraw the snake every frame. this is less efficient than taking the tail piece off and adding to the head, but i believe adding pieces to the end and moving the snake as a whole is more intuitive. also, the MVC model, which was the bigger concern of this project, would not be needed for the more efficient method

todo
----
- [ ] score tracking ?
- [ ] display text on screen (buttons?)
- [ ] multiplayer (network)
- [x] self playing - better features (maximizing space?)
- [x] upload an executable (change font then try pyinstaller)
- [x] speed adjustment
