"""
all credit to: https://github.com/keon/algorithms/blob/master/algorithms/tree/red_black_tree/red_black_tree.py

BeachLine implementation by: github.com/Zhylkaaa

inspiration: https://github.com/pvigier/FortuneAlgorithm/blob/master/src/Beachline.cpp
"""

"""
Implementation of Red-Black tree.
"""

import numpy as np


class Arc:
    def __init__(self, site):

        self.parent = None
        self.left = None
        self.right = None

        # red = 1, black = 0
        self.color = 1

        self.site = site
        self.left_half_edge = None
        self.right_half_edge = None
        self.event = None

        self.prev = None
        self.next = None


class BeachLine:
    def __init__(self, compute_breakpoint):
        self.root = None
        self.compute_breakpoint = compute_breakpoint

    def set_root(self, arc):
        self.root = arc
        self.root.color = 0

    def is_empty(self):
        return self.root is None

    def left_rotate(self, node):
        # set the node as the left child node of the current node's right node
        right_node = node.right
        if right_node is None:
            return
        else:
            # right node's left node become the right node of current node
            node.right = right_node.left
            if right_node.left is not None:
                right_node.left.parent = node
            right_node.parent = node.parent
            # check the parent case
            if node.parent is None:
                self.root = right_node
            elif node is node.parent.left:
                node.parent.left = right_node
            else:
                node.parent.right = right_node
            right_node.left = node
            node.parent = right_node

    def right_rotate(self, node):
        # set the node as the right child node of the current node's left node
        left_node = node.left
        if left_node is None:
            return
        else:
            # left node's right  node become the left node of current node
            node.left = left_node.right
            if left_node.right is not None:
                left_node.right.parent = node
            left_node.parent = node.parent
            # check the parent case
            if node.parent is None:
                self.root = left_node
            elif node is node.parent.left:
                node.parent.left = left_node
            else:
                node.parent.right = left_node
            left_node.right = node
            node.parent = left_node

    def get_leftmost_arc(self):
        arc = self.root

        if arc is None:
            return None

        while arc.prev is not None:
            arc = arc.prev

        return arc

    def get_arc_above(self, point, l):
        node = self.root

        eps = 1e-8

        if node is None:
            return None

        while True:
            breakpoint_left = -np.inf
            breakpoint_right = np.inf

            if node.prev is not None:
                breakpoint_left = self.compute_breakpoint(node.prev.site.point, node.site.point, l)

            if node.next is not None:
                breakpoint_right = self.compute_breakpoint(node.site.point, node.next.site.point, l)

            if point[0] < breakpoint_left:
                node = node.left
            elif point[0] > breakpoint_right:
                node = node.right
            else:
                return node

    def insert_before(self, x, y):

        if x.left is None:
            # we can place it directly to the left of the parent parabola
            x.left = y
            y.parent = x
        else:
            x.prev.right = y
            y.parent = x.prev

        y.prev = x.prev

        if y.prev is not None:
            y.prev.next = y

        y.next = x
        x.prev = y

        self.fix_insert(y)

    def insert_after(self, x, y):

        if x.right is None:
            x.right = y
            y.parent = x
        else:
            x.next.left = y
            y.parent = x.next

        y.next = x.next

        if y.next is not None:
            y.next.prev = y

        y.prev = x
        x.next = y

        self.fix_insert(y)

    def replace(self, x, y):

        self.transplant(x, y)
        y.left = x.left
        y.right = x.right

        if y.left is not None:
            y.left.parent = y

        if y.right is not None:
            y.right.parent = y

        y.prev = x.prev
        y.next = x.next

        if y.prev is not None:
            y.prev.next = y

        if y.next is not None:
            y.next.prev = y

        y.color = x.color

    def fix_insert(self, node):
        # case 1 the parent is null, then set the inserted node as root and color = 0
        if node.parent is None:
            node.color = 0
            self.root = node
            return
            # case 2 the parent color is black, do nothing
        # case 3 the parent color is red
        while node.parent and node.parent.color == 1:
            if node.parent is node.parent.parent.left:
                uncle_node = node.parent.parent.right
                if uncle_node and uncle_node.color == 1:
                    # case 3.1 the uncle node is red
                    # then set parent and uncle color is black and grandparent is red
                    # then node => node.parent
                    node.parent.color = 0
                    node.parent.parent.right.color = 0
                    node.parent.parent.color = 1
                    node = node.parent.parent
                    continue
                elif node is node.parent.right:
                    # case 3.2 the uncle node is black or null, and the node is right of parent
                    # then set his parent node is current node
                    # left rotate the node and continue the next
                    node = node.parent
                    self.left_rotate(node)
                # case 3.3 the uncle node is black and parent node is left
                # then parent node set black and grandparent set red
                node.parent.color = 0
                node.parent.parent.color = 1
                self.right_rotate(node.parent.parent)
            else:
                uncle_node = node.parent.parent.left
                if uncle_node and uncle_node.color == 1:
                    # case 3.1 the uncle node is red
                    # then set parent and uncle color is black and grandparent is red
                    # then node => node.parent
                    node.parent.color = 0
                    node.parent.parent.left.color = 0
                    node.parent.parent.color = 1
                    node = node.parent.parent
                    continue
                elif node is node.parent.left:
                    # case 3.2 the uncle node is black or null, and the node is right of parent
                    # then set his parent node is current node
                    # left rotate the node and continue the next
                    node = node.parent
                    self.right_rotate(node)
                # case 3.3 the uncle node is black and parent node is left
                # then parent node set black and grandparent set red
                node.parent.color = 0
                node.parent.parent.color = 1
                self.left_rotate(node.parent.parent)
        self.root.color = 0


    def transplant(self, node_u, node_v):
        """
        replace u with v
        :param node_u: replaced node
        :param node_v:
        :return: None
        """
        if node_u.parent is None:
            self.root = node_v
        elif node_u is node_u.parent.left:
            node_u.parent.left = node_v
        elif node_u is node_u.parent.right:
            node_u.parent.right = node_v
        # check is node_v is None
        if node_v:
            node_v.parent = node_u.parent

    def delete(self, node):
        # find the node position
        node_color = node.color
        if node.left is None:
            temp_node = node.right
            self.transplant(node, node.right)
        elif node.right is None:
            temp_node = node.left
            self.transplant(node, node.left)
        else:
            # both child exits ,and find minimum child of right child
            node_min = self.minimum(node.right)
            node_color = node_min.color
            temp_node = node_min.right
            ##
            if node_min.parent != node:
                self.transplant(node_min, node_min.right)
                node_min.right = node.right
                node_min.right.parent = node_min
            self.transplant(node, node_min)
            node_min.left = node.left
            node_min.left.parent = node_min
            node_min.color = node.color
        # when node is black, then need to fix it with 4 cases
        if node_color == 0:
            self.delete_fixup(temp_node)

        if node.prev is not None:
            node.prev.next = node.next

        if node.next is not None:
            node.next.prev = node.prev

    # TODO: check strange behavior (temporary added if's, but seems to work fine)
    def delete_fixup(self, node):
        # 4 cases
        if node is None:
            return

        while node is not self.root and node.color == 0:
            # node is not root and color is black
            if node == node.parent.left:
                # node is left node
                node_brother = node.parent.right

                if node_brother is None:
                    return
                # case 1: node's red, can not get black node
                # set brother is black and parent is red
                if node_brother.color == 1:
                    node_brother.color = 0
                    node.parent.color = 1
                    self.left_rotate(node.parent)
                    node_brother = node.parent.right
                    if node_brother is None:
                        return

                # case 2: brother node is black, and its children node is both black
                if (node_brother.left is None or node_brother.left.color == 0) and (
                        node_brother.right is None or node_brother.right.color == 0):
                    node_brother.color = 1
                    node = node.parent
                else:

                    # case 3: brother node is black , and its left child node is red and right is black
                    if node_brother.right is None or node_brother.right.color == 0:
                        node_brother.color = 1
                        node_brother.left.color = 0
                        self.right_rotate(node_brother)
                        node_brother = node.parent.right
                        if node_brother is None:
                            return

                    # case 4: brother node is black, and right is red, and left is any color
                    node_brother.color = node.parent.color
                    node.parent.color = 0
                    node_brother.right.color = 0
                    self.left_rotate(node.parent)
                node = self.root
                break
            else:
                node_brother = node.parent.left

                if node_brother is None:
                    return

                if node_brother.color == 1:
                    node_brother.color = 0
                    node.parent.color = 1
                    self.left_rotate(node.parent)

                    if node.parent is None:
                        return

                    node_brother = node.parent.right
                    if node_brother is None:
                        return
                if (node_brother.left is None or node_brother.left.color == 0) and (
                        node_brother.right is None or node_brother.right.color == 0):
                    node_brother.color = 1
                    node = node.parent
                else:
                    if node_brother.left is None or node_brother.left.color == 0:
                        node_brother.color = 1
                        node_brother.right.color = 0
                        self.left_rotate(node_brother)
                        node_brother = node.parent.left
                    node_brother.color = node.parent.color
                    node.parent.color = 0
                    node_brother.left.color = 0
                    self.right_rotate(node.parent)
                node = self.root
                break
        node.color = 0

    def inorder(self):
        res = []
        if not self.root:
            return res
        stack = []
        root = self.root
        while root or stack:
            while root:
                stack.append(root)
                root = root.left
            root = stack.pop()
            res.append({'val': root.val, 'color': root.color})
            root = root.right
        return res

    def minimum(self, node):
        """
        find the minimum node when node regard as a root node
        :param node:
        :return: minimum node
        """
        temp_node = node
        while temp_node.left:
            temp_node = temp_node.left
        return temp_node

    def maximum(self, node):
        """
        find the max node when node regard as a root node
        :param node:
        :return: max node
        """
        temp_node = node
        while temp_node.right is not None:
            temp_node = temp_node.right
        return temp_node
