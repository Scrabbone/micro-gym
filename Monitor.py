import enum
from timeit import repeat
import matplotlib
from matplotlib import animation
from micro_grid.envs.v2.Building2 import Building
import networkx as nx
from micro_grid.envs.v2.Solar2 import Solar
from micro_grid.envs.v2.Battery2 import Battery
from micro_grid.envs.v2.Ambient2 import Ambient
import matplotlib.pyplot as plt
import numpy as np
import queue as qu
import datetime


def create_plot(nodes: Building, queue: qu.Queue, ambient: Ambient):
    fig = plt.figure()
    G = nx.MultiDiGraph()
    buildings = nodes
    node_tags = []
    power_bought_list = []
    size_list = []
    try:
        ambient_data = ambient.queue.get_nowait()
    except qu.Empty:
        return
    text_str = "Hour: "+str(ambient_data[0]) + \
        "\n Imported energy: "+str(ambient_data[1]) + \
        "\n Year: "+str(datetime.datetime.now().year-ambient_data[2])
    fig.text(0.01, 0.99, text_str, fontsize=8, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    # Adding nodes
    for i, node in enumerate(nodes):
        try:
            power_bought = node.queue.get_nowait()
        except qu.Empty:
            return
        if(power_bought > 0):
            power_bought_list.append("red")
        else:
            power_bought_list.append("green")
        size_list.append(node.inhabs*100)
        node_tags.append(str(i))
        G.add_node(str(i))

    # Adding edges
    weights = []
    for i, node1 in enumerate(nodes):
        for j, node2 in enumerate(nodes):
            G.add_edge(node_tags[i], node_tags[j])
            weights.append(0)
    pos = nx.spring_layout(G)

    nodes = nx.draw_networkx_nodes(
        G,
        pos,
        node_size=size_list,
        node_color=power_bought_list)

    edges = nx.draw_networkx_edges(
        G,
        pos,
        arrowstyle="->",
        arrowsize=20,
        edge_color=weights,
        edge_cmap=plt.cm.Blues,
        width=2,
        connectionstyle='arc3, rad = 0.1'
    )

    def animate(frame):
        try:
            actions = queue.get_nowait()
        except qu.Empty:
            return
        fig.clear()
        actions = np.array(actions)
        # Updating nodes
        for i, node in enumerate(buildings):
            try:
                power_bought = node.queue.get_nowait()
            except qu.Empty:
                return
            if(power_bought > 0):
                power_bought_list[i] = "red"
            else:
                power_bought_list[i] = "green"
        # Updating edges
        weights_as_string = {}
        weight_index = 0
        for i in range(actions.shape[0]):
            for j in range(actions.shape[1]):
                weights[weight_index] = actions[i][j]
                weights_as_string[(node_tags[i], node_tags[j])] = str(
                    weights[weight_index])
                weight_index += 1
        nodes = nx.draw_networkx_nodes(
            G,
            pos,
            node_size=size_list,
            node_color=power_bought_list)

        edges = nx.draw_networkx_edges(
            G,
            pos,
            arrowstyle="->",
            arrowsize=20,
            edge_color=weights,
            edge_cmap=plt.cm.Blues,
            width=2,
            connectionstyle='arc3, rad = 0.1')

        nx.draw_networkx_edge_labels(G, pos, edge_labels=weights_as_string,
                                     label_pos=0.75, font_size=8, font_family='sans-serif', font_color="red")

        labels = nx.draw_networkx_labels(G, pos, font_family='sans-serif')
        pc = matplotlib.collections.PatchCollection(edges, cmap=plt.cm.Blues)
        plt.colorbar(pc)

        try:
            ambient_data = ambient.queue.get_nowait()
        except qu.Empty:
            return
        text_str = "Hour: "+str(ambient_data[0]) + \
            "\nNight: "+str(ambient.night_hours[ambient_data[0]]) + \
            "\nImported energy: "+str(ambient_data[1]) + \
            "\nYear: " + \
            str(datetime.datetime.now().year-ambient_data[2])
        fig.text(0.01, 0.99, text_str, fontsize=8, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    pc = matplotlib.collections.PatchCollection(edges, cmap=plt.cm.Blues)
    plt.colorbar(pc)
    ani = animation.FuncAnimation(
        fig, animate, frames=None, interval=1, repeat=True)
    plt.show()
    while True:
        pass
