from OpenGL.GL import *
from OpenGL.GLUT import * 
from OpenGL.GLU import * 

import glfw
import numpy 
import sys
import random
from collections import defaultdict

class color: 
    MIN_COLOR = 0
    Max_COLOR = 5
    COLORS = [
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
        (1.0, 1.0, 0.0),
        (1.0, 0.0, 1.0),
        (0.0, 1.0, 1.0)
    ]

G_OBJECT_SPHERE = 1
G_OBJECT_CUBE = 2

class AABB:
    def __init__(self, min_corner, max_corner):
        self.min_corner = min_corner
        self.max_corner = max_corner

def scaling(factors):
    scale = numpy.identity(4)
    scale[0][0], scale[1][1], scale[2][2] = factors
    return scale 

class Node(object):
    """base case for scene elements"""

    def __init__(self):
        self.color_index = random.randint(color.MIN_COLOR, color.MAX_COLOR)
        self.aabb = AABB([0.0, 0.0, 0.0],[0.5, 0.5, 0.5])
        self.translation_matrix = numpy.identity(4)
        self.scaling_matrix = numpy.identity(4)
        self.selected = False 

    def render(self):
        """renders the item to the screen"""
        glPushMatrix()
        glMultMatrixf(numpy.transpose(self.translation_matrix))
        glMultMatrixf(self.scaling_matrix)
        cur_color = color.COLORS[self.color_index]
        glColor3f(cur_color[0], cur_color[1], cur_color[2])

        # emits light if node is selected
        if self.selected: 
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.3, 0.3, 0.3])

        self.render_self()

        if self.selected:
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0])
        glPopMatrix()
    
    def render_self(self):
        raise NotImplementedError("The Abstract Node Class does not define 'render self'")
    
    def pick(self, start, direction, mat):
        """
        return whether or not the ray hits the object 

        consume:
        start, direction form the ray to check mat is the modelview matrix to transfoem ray by
        """

        #transform the modelview matrix by the current translation
        newmat = numpy.dot(
            numpy.dot(mat, self.translation_matrix),
            numpy.linalg.inv(self.scaling_matrix)
        )
        results = self.aabb.ray_hit(start, direction, newmat)
        return results 
    
    def select(self, select = None):
        """toggles or sets selected state"""
        if select is not None:
            self.selected = select
        else: 
            self.selected = not self.selected

    def rotate_color(self, forwards):
        self.color_index += 1 if forwards else -1 
        if self.coor_index > color.MAX_COLOR:
            self.color_index = color.MIN_COLOR
        if self.color_index < color.MIN_COLOR:
            self.color_index = color.MAX_COLOR

    def scale(self, up):
        s = 1.1 if up else 0.9
        self.scaling_matrix = numpy.dot(self.scaling_matrix)
        self.aabb.scale(s)

# primitive nodes 
class Primitive(Node):

    def __init__(self):
        super(Primitive, self).__init__()
        self.call_list = None 

    def render_self(self):
        glCallList(self.call_list)


class Sphere(Primitive):

    def __init__(self):
        super(Sphere, self).__init__()
        self.call_list = G_OBJECT_SPHERE

class Cube(Primitive):

    def __init__(self):
        super(Cube, self).__init__()
        self.call_list = G_OBJECT_CUBE

# hierarchical node 

class HierarchicalNode(Node):
    def __init__(self):
        super(HierarchicalNode, self).__init__()
        self.child_nodes = []
    
    def render_self(self):
        for child in self.child_nodes:
            child.render()

class SnowFigure(HierarchicalNode):

    def __init__(self):
        super(SnowFigure, self).__init__()
        self.child_nodes = [Sphere(), Sphere(), Sphere()]
        self.child_nodes[0].translate(0, -0.6, 0)

        self.child_nodes[1].translate(0, 0.1, 0)
        self.child_nodes[1].scaling_matrix = numpy.dot(
            self.scaling_matrix, scaling([0.8, 0.8, 0.8])
        )

        self.child_nodes[2].translate(0, 0.75, 0)
        self.child_nodes[2].scaling_matrix = numpy.dot(
            self.scaling_matrix, scaling([0.7, 0.7, 0.7])
        )

        for node in self.child_nodes:
            node.color_index = color.MIN_COLOR
        
        self.aabb = AABB([0.0, 0.0, 0.0], [0.5, 1.1, 0.5])

class Interaction(object):

    def __init__(self):
        """Handles user interaction"""

        #currently pressed mouse button
        self.pressed = None 

        #the current location of the camera 
        self.translation = [0, 0, 0, 0]

        #the trackball to calculate rotation 
        self.trackball = trackball.Trackball(theta = -25, distance = 15)

        # the current mouse location 
        self.mouse_loc = None

        #unsophisticated callback mechanism 
        self.callbacks = defaultdict(list)

        self.register 

    def register(self):
        """register callbacks with glut"""
        glutMouseFunc(self.handle_mouse_button)
        glutMouseFunc(self.handle_mouse_move)
        glutKeyboardFunc(self.handle_keystroke)
        glutSpecialFunc(self.handle_keystroke)

    def translate(self, x, y, z):
        """translate the camera """
        self.translation[0] += x
        self.translation[1] += y
        self.translation[2] += z

    def handle_mouse_button(self, button, mode, x, y):
        """callled when the mouse button is pressed or released"""
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        y = ySize - y #invert the y coordinate b/c OpenGL is inverted 
        self.mouse_loc = (x, y)

        if mode == GLUT_DOWN:
            self.pressed = button
            if button == GLUT_RIGHT_BUTTON:
                pass
            elif button == GLUT_LEFT_BUTTON: # pick using the left side of the mouse 
                self.trigger('pick', x, y)
            elif button == 3: #scroll up
                self.translate(0, 0, 1.0)
            elif button == 4: #scroll down
                self.translate(0, 0, -1.0)
        else: ## mouse press release 
            self.pressed = None 
        glutPostRedisplay()

    def handle_mouse_move(self, x, screen_y):
        """called when the mouse is moved"""
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        y = ySize - screen_y # invert the y coordinate because opengl is inverted 

        if self.pressed is not None:
            dx = x - self.mouse_loc[0]
            dy = y - self.mouse_loc[1]

            if self.pressed == GLUT_RIGHT_BUTTON and self.trackball is not None:
                #ignore the updated camera location b/c we want to rotate around the origin
                self.trackball.drag_to(self.mouse_loc[0], self.mouse_loc[1], dx, dy)
            elif self.pressed == GLUT_LEFT_BUTTON:
                self.trigger('move', x, y)
            elif self.pressed == GLUT_MIDDLE_BUTTON:
                self.translate(dx/60.0, dy/60.0, 0)
            else:
                pass
            glutPostRedisplay()
        self.mouse_loc = (x, y)
    

    def handle_keystroke(self, key, x, screen_y):
        """called on keyboard input from the user"""
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        y = ySize - screen_y
        if key =='s':
            self.trigger('place', 'sphere', x, y)
        elif key== 'c':
            self.trigger('place', 'cube', x, y)
        elif key ==GLUT_KEY_UP:
            self.trigger('scale', up=True)
        elif key == GLUT_KEY_DOWN:
            self.trigger('scale', up=False)
        elif key == GLUT_KEY_LEFT:
            self.trigger('rotate_color', forward=True)
        elif key == GLUT_KEY_RIGHT:
            self.trigger('rotate_color', forward=False)
        glutPostRedisplay()

    def register_callback(self, name, func):
        self.callbacks[name].append(func)

    def trigger(self, name, *args, **kwargs):
        for func in self.callbacks[name]:
            func(*args, **kwargs)
    
