import glfw 
from OpenGL.GL import *
from OpenGL.GLUT import *
import sys
import numpy 
from OpenGL.GLU import * 

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
             
