"""
Central initialization of fixtures for Runtime etc.
"""
import os
import pytest
import logging

try:
    os.makedirs('/tmp/micropsi_tests/worlds')
except OSError:
    pass
try:
    os.makedirs('/tmp/micropsi_tests/nodenets')
except OSError:
    pass

import configuration
configuration.RESOURCE_PATH = '/tmp/micropsi_tests'

from micropsi_core import runtime as micropsi

DELETE_TEST_FILES_ON_EXIT = True

world_uid = None
nn_uid = None

logging.getLogger('system').setLevel(logging.WARNING)
logging.getLogger('world').setLevel(logging.WARNING)
logging.getLogger('nodenet').setLevel(logging.WARNING)


def set_logging_levels():
    logging.getLogger('system').setLevel(logging.WARNING)
    logging.getLogger('world').setLevel(logging.WARNING)
    logging.getLogger('nodenet').setLevel(logging.WARNING)


@pytest.fixture(scope="session")
def resourcepath():
    return micropsi.RESOURCE_PATH


@pytest.fixture(scope="session")
def test_world(request):
    global world_uid
    worlds = micropsi.get_available_worlds("Pytest User")
    if worlds:
        world_uid = list(worlds.keys())[0]
    else:
        success, world_uid = micropsi.new_world("World of Pain", "Island", "Pytest User")

    def fin():
        if DELETE_TEST_FILES_ON_EXIT:
            micropsi.delete_world(world_uid)
    request.addfinalizer(fin)
    return world_uid


@pytest.fixture(scope="session")
def test_nodenet(request):
    global nn_uid
    nodenets = micropsi.get_available_nodenets("Pytest User") or {}
    for uid, nn in nodenets.items():
        if(nn.name == 'Testnet'):
            nn_uid = list(nodenets.keys())[0]
    else:
        success, nn_uid = micropsi.new_nodenet("Testnet", "Default", owner="Pytest User", world_uid=world_uid, uid='Testnet')

    def fin():
        if DELETE_TEST_FILES_ON_EXIT:
            micropsi.delete_nodenet(nn_uid)
    request.addfinalizer(fin)
    return nn_uid


def pytest_runtest_call(item):
    if 'fixed_test_nodenet' in micropsi.nodenets:
        micropsi.revert_nodenet("fixed_test_nodenet")
    micropsi.logger.clear_logs()
    set_logging_levels()


@pytest.fixture(scope="function")
def fixed_nodenet(request, test_world):
    from micropsi_core.tests.nodenet_data import fixed_nodenet_data
    success, uid = micropsi.new_nodenet("Fixednet", "Braitenberg", owner="Pytest User", world_uid=test_world, uid='fixed_test_nodenet')
    micropsi.get_nodenet(uid)
    micropsi.merge_nodenet(uid, fixed_nodenet_data)

    def fin():
        if DELETE_TEST_FILES_ON_EXIT:
            micropsi.delete_nodenet(uid)
    request.addfinalizer(fin)
    return uid

#test_nodenet(micropsi())
