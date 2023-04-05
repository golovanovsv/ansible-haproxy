import testinfra
import pytest

@pytest.fixture()
def AnsibleVars(host):
  default_vars = host.ansible("include_vars", "file=defaults/main.yml")["ansible_facts"]
  test_vars = host.ansible("include_vars", "file=molecule/default/vars.yml")["ansible_facts"]
  merged_vars = { **default_vars, **test_vars }
  return merged_vars

def test_keepalived_is_installed(host):
  assert host.package("haproxy").is_installed

def test_service_is_enabled(host):
  assert host.service("haproxy").is_enabled

def test_service_is_running(host):
  assert host.service("haproxy").is_running

def test_haproxy_config_is_exist(host):
  config = host.file("/etc/haproxy/haproxy.cfg")
  assert config.is_file
  assert oct(config.mode) == "0o644"

def test_haproxy_config_content(host, AnsibleVars):
  config = host.file("/etc/haproxy/haproxy.cfg").content_string
  for frontend in AnsibleVars["haproxy_frontends"]:
    assert f"frontend {frontend['name']}" in config
  for backend in AnsibleVars["haproxy_backends"]:
    assert f"backend {backend['name']}" in config
    for server in backend["servers"]:
      assert server in config
