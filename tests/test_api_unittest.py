import pytest
from relink_utils.api import RelinkNukeAPI


@pytest.fixture
def api():
    return RelinkNukeAPI()


def test_get_all_read_nodes(api, mocker):
    # Mock nuke.allNodes to return some fake nodes
    mock_nodes = [mocker.Mock(Class=x) for x in ['Read', 'Write', 'Other']]
    mocker.patch('nuke.allNodes', return_value=mock_nodes)

    nodes = api.get_all_read_nodes()

    # Should only return Read and Write nodes
    assert len(nodes) == 2
    assert nodes[0]['node'].Class() == 'Read'
    assert nodes[1]['node'].Class() == 'Write'


def test_get_all_read_nodes_empty(api, mocker):
    # Return no nodes
    mocker.patch('nuke.allNodes', return_value=[])

    nodes = api.get_all_read_nodes()

    assert nodes == []


def test_get_node_by_full_name(api, mocker):
    mock_node = mocker.Mock()
    mock_node.fullName.return_value = 'test_node'

    mocker.patch('nuke.allNodes', return_value=[mock_node])

    found = api.get_node_by_full_name('test_node')
    assert found == mock_node

    found = api.get_node_by_full_name('fake')
    assert found is None


def test_get_new_path_node_object(api):
    mock_node = {'file': {'value': '/old/path.ext'}}
    expected = '/new/path.ext'

    api.old_directory = '/old'
    api.new_directory = '/new'

    new_path = api.get_new_path(mock_node)

    assert new_path == expected


def test_get_new_path_node_dict(api):
    node_dict = {'old_path': '/old/path.ext'}
    expected = '/new/path.ext'

    api.old_directory = '/old'
    api.new_directory = '/new'

    new_path = api.get_new_path(node_dict)

    assert new_path == expected


def test_get_new_path_no_config(api):
    node_dict = {'old_path': '/some/path.ext'}

    new_path = api.get_new_path(node_dict)

    # Should return empty string if no config
    assert new_path == ''


def test_find_nodes_with_paths(api, mocker):
    n1 = mocker.Mock(knob=mocker.Mock(return_value='/old/path1.ext'))
    n2 = mocker.Mock(knob=mocker.Mock(return_value='/old/path2.ext'))
    n3 = mocker.Mock(knob=mocker.Mock(return_value='/other/path.ext'))

    mocker.patch('nuke.allNodes', return_value=[n1, n2, n3])

    found = api.find_nodes_with_paths(r'/old/.*')

    assert found == [n1, n2]


def test_find_nodes_with_paths_no_matches(api, mocker):
    n1 = mocker.Mock(knob=mocker.Mock(return_value='/other/path1.ext'))
    n2 = mocker.Mock(knob=mocker.Mock(return_value='/new/path2.ext'))

    mocker.patch('nuke.allNodes', return_value=[n1, n2])

    found = api.find_nodes_with_paths(r'/old/.*')

    assert found == []


# Tests for other functions

def test_update_node_path(api, mocker):
    mock_node = mocker.Mock()
    mocker.patch.object(api, 'get_node_by_full_name', return_value=mock_node)

    api.update_node_path('node', '/new/path')

    mock_node['file'].setValue.assert_called_with('/new/path')


def test_update_node_path_not_found(api, mocker):
    mocker.patch.object(api, 'get_node_by_full_name', return_value=None)

    api.update_node_path('node', '/new/path')

    # Should do nothing if node not found
