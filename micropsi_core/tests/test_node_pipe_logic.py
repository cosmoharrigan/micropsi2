#!/usr/local/bin/python
# -*- coding: utf-8 -*-

"""
Tests for node activation propagation and gate arithmetic
"""

from micropsi_core import runtime as micropsi
from micropsi_core.world.world import World
from micropsi_core.world.worldadapter import WorldAdapter, WorldObject


def prepare(fixed_nodenet):
    nodenet = micropsi.get_nodenet(fixed_nodenet)
    netapi = nodenet.netapi
    netapi.delete_node(netapi.get_node("ACTA"))
    netapi.delete_node(netapi.get_node("ACTB"))
    source = netapi.create_node("Register", "Root", "Source")
    netapi.link(source, "gen", source, "gen")
    source.activation = 1
    nodenet.step()
    return nodenet, netapi, source

def add_directional_activators(fixed_nodenet):
    net = micropsi.get_nodenet(fixed_nodenet)
    netapi = net.netapi
    sub_act = netapi.create_node("Activator", "Root", "sub-activator")
    net.nodes[sub_act.uid].parameters = {"type": "sub"}

    sur_act = netapi.create_node("Activator", "Root", "sur-activator")
    net.nodes[sur_act.uid].parameters = {"type": "sur"}

    por_act = netapi.create_node("Activator", "Root", "por-activator")
    net.nodes[por_act.uid].parameters = {"type": "por"}

    ret_act = netapi.create_node("Activator", "Root", "ret-activator")
    net.nodes[ret_act.uid].parameters = {"type": "ret"}

    cat_act = netapi.create_node("Activator", "Root", "cat-activator")
    net.nodes[cat_act.uid].parameters = {"type": "cat"}

    exp_act = netapi.create_node("Activator", "Root", "exp-activator")
    net.nodes[exp_act.uid].parameters = {"type": "exp"}

    return sub_act, sur_act, por_act, ret_act, cat_act, exp_act


def test_node_pipe_logic_subtrigger(fixed_nodenet):
    # test a resting classifier, expect sub to be activated
    net, netapi, source = prepare(fixed_nodenet)
    n_head = netapi.create_node("Pipe", "Root", "Head")

    netapi.link(source, "gen", n_head, "sub", 1)
    net.step()

    assert n_head.get_gate("sub").activation == 1


def test_node_pipe_logic_classifier_two_off(fixed_nodenet):
    # test a resting classifier, expect no activation
    net, netapi, source = prepare(fixed_nodenet)
    n_head = netapi.create_node("Pipe", "Root", "Head")
    n_a = netapi.create_node("Pipe", "Root", "A")
    n_b = netapi.create_node("Pipe", "Root", "B")
    netapi.link_with_reciprocal(n_head, n_a, "subsur")
    netapi.link_with_reciprocal(n_head, n_b, "subsur")
    netapi.link_full([n_a, n_b])

    for i in range(1,3): net.step()
    assert n_head.get_gate("gen").activation == 0


def test_node_pipe_logic_classifier_two_partial(fixed_nodenet):
    # test partial success of a classifier (fuzzyness)
    net, netapi, source = prepare(fixed_nodenet)
    n_head = netapi.create_node("Pipe", "Root", "Head")
    n_a = netapi.create_node("Pipe", "Root", "A")
    n_b = netapi.create_node("Pipe", "Root", "B")
    netapi.link_with_reciprocal(n_head, n_a, "subsur")
    netapi.link_with_reciprocal(n_head, n_b, "subsur")
    netapi.link_full([n_a, n_b])

    netapi.link(source, "gen", n_a, "sur")

    for i in range(1,3): net.step()
    assert n_head.get_gate("gen").activation == 1/2

    netapi.link(source, "gen", n_b, "sur")

    for i in range(1,3): net.step()
    assert n_head.get_gate("gen").activation == 1


def test_node_pipe_logic_classifier_two_partially_failing(fixed_nodenet):
    # test fuzzyness with one node failing
    net, netapi, source = prepare(fixed_nodenet)
    n_head = netapi.create_node("Pipe", "Root", "Head")
    n_a = netapi.create_node("Pipe", "Root", "A")
    n_b = netapi.create_node("Pipe", "Root", "B")
    netapi.link_with_reciprocal(n_head, n_a, "subsur")
    netapi.link_with_reciprocal(n_head, n_b, "subsur")
    netapi.link_full([n_a, n_b])

    netapi.link(source, "gen", n_a, "sur", -1)

    for i in range(1,3): net.step()
    assert n_head.get_gate("gen").activation == - 1/2

    netapi.link(source, "gen", n_b, "sur")

    for i in range(1,3): net.step()
    assert n_head.get_gate("gen").activation == 0


def test_node_pipe_logic_classifier_three_off(fixed_nodenet):
    # test a resting classifier, expect no activation
    net, netapi, source = prepare(fixed_nodenet)
    n_head = netapi.create_node("Pipe", "Root", "Head")
    n_a = netapi.create_node("Pipe", "Root", "A")
    n_b = netapi.create_node("Pipe", "Root", "B")
    n_c = netapi.create_node("Pipe", "Root", "C")
    netapi.link_with_reciprocal(n_head, n_a, "subsur")
    netapi.link_with_reciprocal(n_head, n_b, "subsur")
    netapi.link_with_reciprocal(n_head, n_c, "subsur")
    netapi.link_full([n_a, n_b, n_c])

    for i in range(1,3): net.step()
    assert n_head.get_gate("gen").activation == 0


def test_node_pipe_logic_classifier_three_partial(fixed_nodenet):
    # test partial success of a classifier (fuzzyness)
    net, netapi, source = prepare(fixed_nodenet)
    n_head = netapi.create_node("Pipe", "Root", "Head")
    n_a = netapi.create_node("Pipe", "Root", "A")
    n_b = netapi.create_node("Pipe", "Root", "B")
    n_c = netapi.create_node("Pipe", "Root", "C")
    netapi.link_with_reciprocal(n_head, n_a, "subsur")
    netapi.link_with_reciprocal(n_head, n_b, "subsur")
    netapi.link_with_reciprocal(n_head, n_c, "subsur")
    netapi.link_full([n_a, n_b, n_c])

    netapi.link(source, "gen", n_a, "sur")

    for i in range(1,3): net.step()
    assert n_head.get_gate("gen").activation == 1/3

    netapi.link(source, "gen", n_c, "sur")

    for i in range(1,3): net.step()
    assert n_head.get_gate("gen").activation == 2/3

    netapi.link(source, "gen", n_b, "sur")

    for i in range(1,3): net.step()
    assert n_head.get_gate("gen").activation == 1


def test_node_pipe_logic_classifier_three_partially_failing(fixed_nodenet):
    # test fuzzyness with one node failing
    net, netapi, source = prepare(fixed_nodenet)
    n_head = netapi.create_node("Pipe", "Root", "Head")
    n_a = netapi.create_node("Pipe", "Root", "A")
    n_b = netapi.create_node("Pipe", "Root", "B")
    n_c = netapi.create_node("Pipe", "Root", "C")
    netapi.link_with_reciprocal(n_head, n_a, "subsur")
    netapi.link_with_reciprocal(n_head, n_b, "subsur")
    netapi.link_with_reciprocal(n_head, n_c, "subsur")
    netapi.link_full([n_a, n_b, n_c])

    netapi.link(source, "gen", n_a, "sur", -1)

    for i in range(1,3): net.step()
    assert n_head.get_gate("gen").activation == - 1/3

    netapi.link(source, "gen", n_c, "sur")

    for i in range(1,3): net.step()
    assert n_head.get_gate("gen").activation == 0

    netapi.link(source, "gen", n_b, "sur")

    for i in range(1,3): net.step()
    assert n_head.get_gate("gen").activation == 1/3


def test_node_pipe_logic_two_script(fixed_nodenet):
    # test whether scripts work
    net, netapi, source = prepare(fixed_nodenet)
    n_head = netapi.create_node("Pipe", "Root", "Head")
    n_a = netapi.create_node("Pipe", "Root", "A")
    n_b = netapi.create_node("Pipe", "Root", "B")
    netapi.link_with_reciprocal(n_head, n_a, "subsur")
    netapi.link_with_reciprocal(n_head, n_b, "subsur")
    netapi.link_with_reciprocal(n_a, n_b, "porret")
    netapi.link(source, "gen", n_head, "sub")
    net.step()
    net.step()

    # quiet, first node requesting
    assert n_head.get_gate("gen").activation == 0
    assert n_a.get_gate("sub").activation == 1
    assert n_a.get_gate("sur").activation == 0
    assert n_b.get_gate("sub").activation == 0
    assert n_b.get_gate("sur").activation == 0

    # reply: good!
    netapi.link(source, "gen", n_a, "sur")
    net.step()
    assert n_a.get_gate("sub").activation == 1
    assert n_a.get_gate("sur").activation == 0
    assert n_b.get_gate("sub").activation == 0
    assert n_b.get_gate("sur").activation == 0

    # second node now requesting
    net.step()
    assert n_a.get_gate("sub").activation == 1
    assert n_a.get_gate("sur").activation == 0
    assert n_b.get_gate("sub").activation == 1
    assert n_b.get_gate("sur").activation == 0

    # second node good, third requesting
    netapi.link(source, "gen", n_b, "sur")
    net.step()
    net.step()
    assert n_a.get_gate("sub").activation == 1
    assert n_a.get_gate("sur").activation == 0
    assert n_b.get_gate("sub").activation == 1
    assert n_b.get_gate("sur").activation == 1

    # overall script good
    net.step()
    assert n_head.get_gate("gen").activation == 1


def test_node_pipe_logic_three_script(fixed_nodenet):
    # test whether scripts work
    net, netapi, source = prepare(fixed_nodenet)
    n_head = netapi.create_node("Pipe", "Root", "Head")
    n_a = netapi.create_node("Pipe", "Root", "A")
    n_b = netapi.create_node("Pipe", "Root", "B")
    n_c = netapi.create_node("Pipe", "Root", "C")
    netapi.link_with_reciprocal(n_head, n_a, "subsur")
    netapi.link_with_reciprocal(n_head, n_b, "subsur")
    netapi.link_with_reciprocal(n_head, n_c, "subsur")
    netapi.link_with_reciprocal(n_a, n_b, "porret")
    netapi.link_with_reciprocal(n_b, n_c, "porret")
    netapi.link(source, "gen", n_head, "sub")
    net.step()
    net.step()

    # quiet, first node requesting
    assert n_head.get_gate("gen").activation == 0
    assert n_a.get_gate("sub").activation == 1
    assert n_a.get_gate("sur").activation == 0
    assert n_b.get_gate("sub").activation == 0
    assert n_b.get_gate("sur").activation == 0
    assert n_c.get_gate("sub").activation == 0
    assert n_c.get_gate("sur").activation == 0

    # reply: good!
    netapi.link(source, "gen", n_a, "sur")
    net.step()
    assert n_a.get_gate("sub").activation == 1
    assert n_a.get_gate("sur").activation == 0
    assert n_b.get_gate("sub").activation == 0
    assert n_b.get_gate("sur").activation == 0
    assert n_c.get_gate("sub").activation == 0
    assert n_c.get_gate("sur").activation == 0

    # second node now requesting
    net.step()
    assert n_a.get_gate("sub").activation == 1
    assert n_a.get_gate("sur").activation == 0
    assert n_b.get_gate("sub").activation == 1
    assert n_b.get_gate("sur").activation == 0
    assert n_c.get_gate("sub").activation == 0
    assert n_c.get_gate("sur").activation == 0

    # second node good, third requesting
    netapi.link(source, "gen", n_b, "sur")
    net.step()
    net.step()
    assert n_a.get_gate("sub").activation == 1
    assert n_a.get_gate("sur").activation == 0
    assert n_b.get_gate("sub").activation == 1
    assert n_b.get_gate("sur").activation == 0
    assert n_c.get_gate("sub").activation == 1
    assert n_c.get_gate("sur").activation == 0

    # third node good
    netapi.link(source, "gen", n_c, "sur")
    net.step()
    net.step()
    assert n_a.get_gate("sub").activation == 1
    assert n_a.get_gate("sur").activation == 0
    assert n_b.get_gate("sub").activation == 1
    assert n_b.get_gate("sur").activation == 0
    assert n_c.get_gate("sub").activation == 1
    assert n_c.get_gate("sur").activation == 1

    # overall script good
    net.step()
    assert n_head.get_gate("gen").activation == 1

    # now let the second one fail
    # whole script fails, third one muted
    netapi.link(source, "gen", n_b, "sur", -1)
    net.step()
    net.step()
    assert n_a.get_gate("sub").activation == 1
    assert n_a.get_gate("sur").activation == 0
    assert n_b.get_gate("sub").activation == 1
    assert n_b.get_gate("sur").activation == -1
    #assert n_c.get_gate("sub").activation == 0
    assert n_c.get_gate("sur").activation == 0

    net.step()
    assert n_head.get_gate("gen").activation == -1


def test_node_pipe_logic_three_alternatives(fixed_nodenet):
    # create three alternatives, let one fail, one be undecided, one succeed
    net, netapi, source = prepare(fixed_nodenet)
    n_head = netapi.create_node("Pipe", "Root", "Head")
    n_a = netapi.create_node("Pipe", "Root", "A")
    n_b = netapi.create_node("Pipe", "Root", "B")
    n_c = netapi.create_node("Pipe", "Root", "C")
    n_a.set_gate_parameters("sur", {"threshold": 0})
    n_b.set_gate_parameters("sur", {"threshold": 0})
    n_c.set_gate_parameters("sur", {"threshold": 0})

    netapi.link_with_reciprocal(n_head, n_a, "subsur")
    netapi.link_with_reciprocal(n_head, n_b, "subsur")
    netapi.link_with_reciprocal(n_head, n_c, "subsur")
    netapi.link(source, "gen", n_head, "sub")
    net.step()
    net.step()

    netapi.link(source, "gen", n_a, "sur", 0)
    netapi.link(source, "gen", n_b, "sur", 1)
    netapi.link(source, "gen", n_c, "sur", -1)

    net.step()
    net.step()

    assert n_head.get_gate("gen").activation == 1

    # now fail the good one
    netapi.link(source, "gen", n_a, "sur", 0)
    netapi.link(source, "gen", n_b, "sur", -1)
    netapi.link(source, "gen", n_c, "sur", -1)

    net.step()
    net.step()

    assert n_head.get_gate("gen").activation == 0


def test_node_pipe_logic_feature_binding(fixed_nodenet):
    # check if the same feature can be checked and bound twice
    net, netapi, source = prepare(fixed_nodenet)
    schema = netapi.create_node("Pipe", "Root", "Schema")
    element1 = netapi.create_node("Pipe", "Root", "Element1")
    element2 = netapi.create_node("Pipe", "Root", "Element2")
    netapi.link_with_reciprocal(schema, element1, "subsur")
    netapi.link_with_reciprocal(schema, element2, "subsur")
    netapi.link_full([element1, element2])

    concrete_feature1 = netapi.create_node("Pipe", "Root", "ConcreteFeature1")
    concrete_feature2 = netapi.create_node("Pipe", "Root", "ConcreteFeature2")
    netapi.link_with_reciprocal(element1, concrete_feature1, "subsur")
    netapi.link_with_reciprocal(element2, concrete_feature2, "subsur")

    abstract_feature = netapi.create_node("Pipe", "Root", "AbstractFeature")
    netapi.link_with_reciprocal(concrete_feature1, abstract_feature, "catexp")
    netapi.link_with_reciprocal(concrete_feature2, abstract_feature, "catexp")

    netapi.link(source, "gen", schema, "sub")
    netapi.link(source, "gen", abstract_feature, "sur")

    net.step()
    assert abstract_feature.get_gate("gen").activation == 1
    assert abstract_feature.get_gate("exp").activation == 1

    net.step()
    assert concrete_feature1.get_gate("gen").activation == 1
    assert concrete_feature2.get_gate("gen").activation == 1

    net.step()
    net.step()

    assert schema.get_gate("gen").activation == 1

def test_node_pipe_logic_search_sub(fixed_nodenet):
    # check if sub-searches work
    net, netapi, source = prepare(fixed_nodenet)
    n_a = netapi.create_node("Pipe", "Root", "A")
    n_b = netapi.create_node("Pipe", "Root", "B")
    netapi.link_with_reciprocal(n_a, n_b, "subsur")

    sub_act, sur_act, por_act, ret_act, cat_act, exp_act = add_directional_activators(fixed_nodenet)
    netapi.link(source, "gen", sub_act, "gen")

    netapi.link(source, "gen", n_a, "sub")

    net.step()
    net.step()
    net.step()

    assert n_a.get_gate("sub").activation == 1
    assert n_b.get_gate("sub").activation == 1


def test_node_pipe_logic_search_sur(fixed_nodenet):
    # check if sur-searches work
    net, netapi, source = prepare(fixed_nodenet)
    n_a = netapi.create_node("Pipe", "Root", "A")
    n_b = netapi.create_node("Pipe", "Root", "B")
    netapi.link_with_reciprocal(n_a, n_b, "subsur")

    sub_act, sur_act, por_act, ret_act, cat_act, exp_act = add_directional_activators(fixed_nodenet)
    netapi.link(source, "gen", sur_act, "gen")

    netapi.link(source, "gen", n_b, "sur")

    net.step()
    net.step()
    net.step()

    assert n_b.get_gate("sur").activation > 0
    assert n_a.get_gate("sur").activation > 0


def test_node_pipe_logic_search_por(fixed_nodenet):
    # check if por-searches work
    net, netapi, source = prepare(fixed_nodenet)
    n_a = netapi.create_node("Pipe", "Root", "A")
    n_b = netapi.create_node("Pipe", "Root", "B")
    netapi.link_with_reciprocal(n_a, n_b, "porret")

    sub_act, sur_act, por_act, ret_act, cat_act, exp_act = add_directional_activators(fixed_nodenet)
    netapi.link(source, "gen", por_act, "gen")

    netapi.link(source, "gen", n_a, "por")

    net.step()
    net.step()
    net.step()

    assert n_a.get_gate("por").activation == 1
    assert n_b.get_gate("por").activation == 1


def test_node_pipe_logic_search_ret(fixed_nodenet):
    # check if ret-searches work
    net, netapi, source = prepare(fixed_nodenet)
    n_a = netapi.create_node("Pipe", "Root", "A")
    n_b = netapi.create_node("Pipe", "Root", "B")
    netapi.link_with_reciprocal(n_a, n_b, "porret")

    sub_act, sur_act, por_act, ret_act, cat_act, exp_act = add_directional_activators(fixed_nodenet)
    netapi.link(source, "gen", ret_act, "gen")

    netapi.link(source, "gen", n_b, "por")

    net.step()
    net.step()
    net.step()

    assert n_b.get_gate("ret").activation == 1
    assert n_a.get_gate("ret").activation == 1


def test_node_pipe_logic_search_cat(fixed_nodenet):
    # check if cat-searches work
    net, netapi, source = prepare(fixed_nodenet)
    n_a = netapi.create_node("Pipe", "Root", "A")
    n_b = netapi.create_node("Pipe", "Root", "B")
    netapi.link_with_reciprocal(n_a, n_b, "catexp")

    sub_act, sur_act, por_act, ret_act, cat_act, exp_act = add_directional_activators(fixed_nodenet)
    netapi.link(source, "gen", cat_act, "gen")

    netapi.link(source, "gen", n_a, "cat")

    net.step()
    net.step()
    net.step()

    assert n_a.get_gate("cat").activation == 1
    assert n_b.get_gate("cat").activation == 1


def test_node_pipe_logic_search_exp(fixed_nodenet):
    # check if exp-searches work
    net, netapi, source = prepare(fixed_nodenet)
    n_a = netapi.create_node("Pipe", "Root", "A")
    n_b = netapi.create_node("Pipe", "Root", "B")
    netapi.link_with_reciprocal(n_a, n_b, "catexp")

    sub_act, sur_act, por_act, ret_act, cat_act, exp_act = add_directional_activators(fixed_nodenet)
    netapi.link(source, "gen", exp_act, "gen")

    netapi.link(source, "gen", n_b, "exp")

    net.step()
    net.step()
    net.step()

    assert n_b.get_gate("exp").activation > 0
    assert n_a.get_gate("exp").activation > 0
