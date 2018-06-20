import numpy as np
import random
from math import cos, sin, atan2
import matplotlib.path as mplPath
import matplotlib.pyplot as plt
import time
from generate_patches import main as generate_patches


class Node:
    x = 0
    y = 0
    cost = 0
    parent = None
    def __init__(self,xcoord, ycoord):
         self.x = xcoord
         self.y = ycoord


def dist(p1, p2):
    return np.linalg.norm(np.asarray(p1)-np.asarray(p2))


def step_from_to(p1, p2, EPSILON):
    if dist(p1,p2) < EPSILON:
        return p2
    else:
        theta = atan2(p2[1]-p1[1],p2[0]-p1[0])
        return p1[0] + EPSILON*cos(theta), p1[1] + EPSILON*sin(theta)


def chooseParent(nn, newnode, nodes, RADIUS, object_c):
    for p in nodes:
        if check_intersect(p, newnode, object_c) and \
                dist([p.x, p.y], [newnode.x, newnode.y]) < RADIUS and p.cost + dist(
                [p.x, p.y], [newnode.x, newnode.y]) < nn.cost + dist([nn.x, nn.y], [newnode.x, newnode.y]):
            nn = p
    newnode.cost = nn.cost + dist([nn.x, nn.y], [newnode.x, newnode.y])
    newnode.parent = nn
    return newnode, nn


def check_intersect(nodeA, nodeB, object_c):
    A = np.array([nodeA.x, nodeA.y])
    B = np.array([nodeB.x, nodeB.y])
    t = np.linspace(0, 1, 50)
    interp = np.asarray([B*i + (1-i)*A for i in t])
    decisions = [p.contains_points(interp) for p in object_c]
    decisions = [item for sublist in decisions for item in sublist]
    # print(decisions)
    return not any(decisions) # will return True if nodeA and nodeB are safely connectable


def reWire(nodes, newnode, RADIUS, object_c):
    for i in range(len(nodes)):
        p = nodes[i]
        if check_intersect(p, newnode, object_c) and p != newnode.parent and \
                dist([p.x, p.y], [newnode.x,newnode.y]) < RADIUS and \
                newnode.cost + dist([p.x, p.y], [newnode.x, newnode.y]) < p.cost:
            p.parent = newnode
            p.cost = newnode.cost + dist([p.x, p.y], [newnode.x, newnode.y])
            nodes[i] = p
    return nodes


def drawSolutionPath(start, goal, nodes, plot):
    nn = nodes[0]
    path = [np.array([goal.x,goal.y])]
    for p in nodes:
       if dist([p.x, p.y], [goal.x, goal.y]) < dist([nn.x, nn.y], [goal.x, goal.y]):
          nn = p
    while nn != start:
        path.append(np.array([nn.x, nn.y]))
        nn = nn.parent
    path.append(np.array([start.x, start.y]))
    path = np.asarray(path)
    if plot:
        plt.plot(path[:, 0], path[:, 1], 'k')
        plt.plot(start.x, start.y, 'g.', markersize = 10)
        plt.plot(goal.x, goal.y, 'r.', markersize = 10)
    return path


def main(cx, cy, start, goal, filename, EPSILON, plot):

    NUMNODES = 1000
    RADIUS = 10.0


    """Loading and formatting obstacles"""
    polygon = np.asarray(np.load(filename))
    object_c = []
    for i in range(polygon.shape[0]):
        obj = mplPath.Path(polygon[i, :, :])
        object_c.append(obj)

    nodes = []
    nodes.append(Node(start[0], start[1]))  # Start in the corner start= nodes[0]
    start = nodes[0]
    goal = Node(goal[0], goal[1])
    t = time.time()
    counter = 0
    while True:

        rand = Node(random.random() * cx, random.random() * cy)
        nn = nodes[0]
        for p in nodes:
            if dist([p.x, p.y], [rand.x, rand.y]) < dist([nn.x, nn.y], [rand.x, rand.y]):
                nn = p
        interpolatedNode = step_from_to([nn.x, nn.y], [rand.x, rand.y], EPSILON)
        newnode = Node(interpolatedNode[0], interpolatedNode[1])
        if check_intersect(nn, rand, object_c):
            [newnode, nn] = chooseParent(nn, newnode, nodes, RADIUS, object_c)

            nodes.append(newnode)
            nodes = reWire(nodes, newnode, RADIUS, object_c)
        if np.linalg.norm(np.array([newnode.x, newnode.y])-np.array([goal.x, goal.y])) < EPSILON:
            break

        if counter > NUMNODES:
            print('limit reached!')
            break
        counter = counter + 1
    # print('time taken for RRT* to trace a path: ',time.time()-t)
    path = np.asarray(drawSolutionPath(start, goal, nodes, plot))
    t_path = time.time() - t
    return path, t_path


if __name__ == '__main__':
    load_polys = 'random_squares_1.npy'
    cx = cy = 100
    plt.close('all')
    generate_patches(cx, cy, load_polys)
    path, time = main(cx, cy, (10, 20), (90, 90.17), load_polys, EPSILON=5, plot=True)
