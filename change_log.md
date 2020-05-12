

### Rotabox 0.13.0 changes

##### Added

* #### in Rotaboxer (bounds editor):
  * Automated bounding process, using the image's outline (it's detected with alpha/color-tracing).  
    Controls:  
    * complexity/accuracy adjustment  
    * choice of the background color needed to trace .atlas files  
    * option for images with more than one independent shapes   
    * option for processing an entire .atlas animation,  in one go

  
##### Changed
* Minor corrections and changes.


### Rotabox 0.12.1 changes

##### Changed
* Rotabox is now Python 3 compatible.
* Rotaboxer is now Python 3 compatible.


### Rotabox 0.12.0 changes

##### Added
* Cython option:  
Rotabox tries by default to use a compiled cython module (cybounds.so or cybounds.pyd) for an about X5 speedup.
User needs to compile it for specific operating systems using the provided cybounds.c file.

* [pre_check] BooleanProperty(False):
A collision optimization switch for larger widgets in Cython.
It's always considered True in Python but in Cython, for small widgets (under 45 points), the slight tax of the extra calculations outweighs any benefits in collision.

* [read_bounds] A method to define [custom_bounds] by reading a Rotaboxer project file (.bounds file), e.g.: 
```python
self.custom_bounds = self.read_ bounds("images/car.bounds")
```
* #### in Rotaboxer (bounds editor):
  * Multiple points can be moved simultaneously with keyboard arrow keys.
  * Point multiselection (Ctrl+click) was already there since version 0.9 for transfering points between polygons.

##### Removed
* [hidden_bounds] were deemed an unnessesary complication in the recent refactoring, adding too much code for a mere application of a more general feature:
  The ability to treat specific collisions specifically, using multiple polygons and Rotabox' collision feedback.

##### Changed
* Major refactoring to accomodate Cython.
  * Different balance between bounds calculation and collision detection.  
    The former, which was the major load, is twice as fast while the latter is slightly slower - an overall of about X1.5.

* [draw_bounds] is now a NumericProperty (0 for False, 1 for bounds only, 2 for bounds & bounding boxes).

			
### Rotabox 0.11.0 changes

##### Added
* Method to retrieve the current coordinates of any point defined in custom_bounds:
```python
pod.center = ferris.get_point(pol index, point index)
```
* #### in Rotaboxer (bounds editor):
  * A switch to lock/unlock polygons' exporting order.  
    Before, the order changed everytime a polygon was selected.

  * An option, when dealing with an .atlas file, to export a single frame as a list or the whole as a dictionary (animated bounds).
		    
  * Ability to see and export open bounds.

##### Changed
* Some changes in documentation.

* #### in Rotaboxer (bounds editor):
  * File selectors now working properly with kivy 1.10.


### Rotabox 0.10.0 changes	

##### Added
* Two new collision detection methods, the second being similar in performance to the original one but without the need for a checking strategy.
* Open bounds support with the default collision method.

* #### in Rotaboxer (bounds editor):
  * Option to show points and polygons indices.
  * Color options for polygon drawing
	
##### Removed
* The original collision detection method is now discontinued.
* Test painting of collidable areas. No need for it anymore, since checking strategy is no longer required.

* #### in Rotaboxer (bounds editor):
  * Real-time checkpoint inspection removed. No checking strategy needed anymore.

  * Automatic checkpoint allocation removed. No checking strategy needed anymore.

  * Test painting of collidable areas removed. No checking strategy needed anymore.
  
##### Changed		
* custom_bounds' form has been simplified ([[(0, 0), (1, 0), (1, 1), (0, 1)]])

* #### in Rotaboxer (bounds editor):
  * Selecting a polygon, places it last, in the resulting list of polygons.  
    This way, when editing is done, one can determine the order of polygons in the resulting "custom_bounds" by click-selecting them, one after the other, in the required order.



### Rotabox 0.9.0 changes

##### Added	
* Touch manipulation (drag, rotation and zoom).
Since, due to the differences between the Scatter and Rotabox concepts, a way to combine the two couldn't be found, Rotabox uses the Scatter widget's code, modified to act on the actual size and position of the widget and child(essential for accurate collision detection). 
It supports single and multitouch drag, rotation and scaling (the latter two use the *origin* property in the singletouch option).

* "hidden_bounds" property.
An option for the widget to hide certain polygons from others' checks and use them as one-way detectors. A two-way check is normally required for accurate collision readings, but a second layer of bounds can have its uses where accuracy is not an issue (e.g. in longer distances, acting as the 'perception' of an enemy sprite in a game).

* "ready" BooleanProperty (False).
    Offers a Rotabox setup completion event.

* #### in Rotaboxer (bounds editor):
  * Selecting a polygon, places it first, in the resulting list of polygons.
    This way, when editing is done, one can determine the order of polygons in the resulting "custom_bounds" by click-selecting them, one after the other, in an order, opposite of the required.

  * Real-time checkpoint inspection added.
    Promoting points to checkpoints in a polygon requires some understanding of the Rotabox collision detection concept and can be tricky or even impossible without adding extra points or breaking the polygon into simpler shapes, depending on the shape.

  * Automatic checkpoint allocation when "Checkpoint" button is checked. Experimental. Always paint-test the bounds after any checkpoint setup.

  * Transfering points from a polygon to another, added.
    Not a positional transfer but a change in linkage. Useful when breaking a polygon is required.

  * Showing points and polygons indices.

##### Renamed
* "allow_rotabox" BooleanProperty (old name: "custom_bounds")

* "custom_bounds" ObjectProperty (old name: "bounds")
