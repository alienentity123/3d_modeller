import glfw 
from OpenGL.GL import *
from OpenGL.GLUT import *
import sys
import numpy 
from OpenGL.GLU import * 

from node import Sphere, Cube, SnowFigure

class Scene(object):

    #the default depth from the camera to place an object at 
    PLACE_DEPTH = 15.0

    def _init__(self):
        #this scene keeps a list of nodes that are displayed
        self.node_list = list()
        # keep track of the currently selected node
        # actions may depend on whether or not something is selected
        self.selected_node = None 

    def add_node(self, node):
        """add a new node to the scene """
        self.node_list.append(node)

    def render(self):
        """render the scene"""
        for node in self.nde_list:
            node.render()

    def pick(self, start, direction, mat):
        """
        exccute selection 
        start, direction decribes a ray 
        mat is the inverse of the current modelview matrix for the scene
        """

        if self.selected_node is not None:
            self.selected_node.select(False)
            self.selected_node = None
             
        # keep track of the closest hit 
        mindist = sys.maxint 
        closest_node = None 
        for node in self.node_list:
            hit, dist = node.pick(start, direction, mat)
            if hit and dist < mindist:
                mindist, closest_node = dist, node
        
        # if we hit comething, keep track of it 
        if closest_node is not None:
            closest_node.select()
            closest_node.depth = mindist 
            closest_node.select_loc = start + direction * mindist 
            self.selected_node = closest_node

    def rotate_selected_color(self, forwards):
        """ Rotate the color of the currently selected node """
        if self.selected_node is None: return
        self.selected_node.rotate_color(forwards)

    def scale_selected(self, up):
        """scale the current selection"""
        if self.selected_node is None:
            return 
        self.selected_node.scale(up)

    def place(self, shape, start, direction, inv_modelview):
        """
        place a new node 

        consume: 
        shape the shape to add 
        start, direction describes the ray to move to 
        inv_model_view is the inverse model view matrix for the scene 
        """

        new_node = None 
        if shape == 'sphere': 
            new_node = Sphere()
        elif shape == 'cube': 
            new_node = Cube()
        elif shape == 'figure':
            new_node = SnowFigure()

        self.add_node(new_node)

        #place the node at the cursor in the camera space 
        translate = (start + direction * self.PLACE_DEPTH)

        # convert the translation to world space 
        pre_tran = numpy.array([translate[0], translate[1], translate[2], 1])
