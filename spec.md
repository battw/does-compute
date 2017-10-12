# Line Computer Puzzle Spec

## Requirements

### View
* Bitmaps to represent nodes/signals?
* Primative shapes to represent nodes/signals?
* What background colour/texture?
* Coloured signals for particular nodes
* Lines or checks helping the user to visualise the route of a signal

### Controller
* Place a node using the mouse and point it in a particular direction by draggng (left click).
* Invert all nodes in a cell with a mouse click (right click).
* Delete nodes at a particular cell using a click or button (hold right button?).
* Select a colour for nodes in a cell so that they send out signals of that colour.


### Model
#### Interface
* update()
* place_node(position, orientation)
* delete_nodes_at(position)
* invert_nodes_at(position)
* get_all_objects() What should this return? The type of each object, the position of each object, and the direction of each object? This needs to provide enough info for the view to draw a representation of the model.

#### Nodes
* invert()
* Invert all nodes in a cell.
* Place nodes.
* Delete all nodes at a particular cell.
* Multiple nodes are allowed in a given cell.
* No two nodes can have the same cell and direction.

#### Signals
* Signals are drawn originating at nodes and ending when they reach other nodes or go out of bounds.
* Placing nodes ontop of signals causes the signals to end at that node and the remainder of the signal to decay along its length. As well as sending out the appropriate new signal.
* Nodes which have a signal ending at their position output a signal if they are not negated.
* Nodes which are inverted output a signal unless they have a signal ending at their position.
* Nodes which are already outputing a signal don't output a new signal when recieving a new input.
