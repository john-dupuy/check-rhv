# coding: utf-8
"""
These are the functions to check RHV manager/hosts through the
RHV API
"""
from __future__ import division

import sys

from ovirtsdk4 import types


def check_vm_count(system, warn=20, crit=30, **kwargs):
    """ Check overall host status. """
    warn = int(warn)
    crit = int(crit)
    vm_count = len(system.list_vms())
    # determine ok, warning, critical, unknown state
    if vm_count < warn:
        print("Ok: VM count is less than {}. VM Count = {}".format(warn, vm_count))
        sys.exit(0)
    elif warn <= vm_count <= crit:
        print("Warning: VM count is greater than {} & less than {}. VM Count = {}"
            .format(warn, crit, vm_count))
        sys.exit(1)
    elif vm_count > crit:
        print("Critical: VM count is greater than {}. VM Count = {}".format(crit, vm_count))
        sys.exit(2)
    else:
        print("Unknown: VM count is unknown")
        sys.exit(3)


def check_storage_domain_status(system, **kwargs):
    """ Check the usage of all the datastores on the host. """
    okay, warning, critical, unknown, all = [], [], [], [], []
    storage_domains = system.api.system_service().storage_domains_service().list()

    for storage_domain in storage_domains:
        status = storage_domain.external_status
        if status == types.ExternalStatus.OK:
            okay.append((storage_domain.name, status))
        elif status == types.ExternalStatus.WARNING:
            warning.append((storage_domain.name, status))
        elif status == types.ExternalStatus.FAILURE or status == types.ExternalStatus.ERROR:
            critical.append((storage_domain.name, status))
        else:
            unknown.append((storage_domain.name, status))
        all.append((storage_domain.name, status))

    if critical:
        print("Critical: the following storage_domain(s) definitely have an issue: {}\n "
              "Status of all storage_domain is: {}".format(critical, all))
        sys.exit(2)
    elif warning:
        print("Warning: the following storage_domain(s) may have an issue: {}\n "
              "Status of all storage_domain is: {}".format(warning, all))
        sys.exit(1)
    elif unknown:
        print("Unknown: the following storage_domain(s) are in an unknown state: {}\n"
              "Status of all storage_domain is: {}".format(unknown, all))
        sys.exit(3)
    else:
        print("Ok: all storage_domain(s) are in the OK state: {}".format(okay))
        sys.exit(0)


def check_storage_domain_usage(system, warn=0.75, crit=0.9, **kwargs):
    """ Check the usage of all the datastores on the host. """
    warn = float(warn)
    crit = float(crit)
    okay, warning, critical, unknown, all_sd = [], [], [], [], []
    storage_domains = system.api.system_service().storage_domains_service().list()

    for storage_domain in storage_domains:
        if storage_domain.type == types.StorageDomainType.IMAGE:
            # Skipping storage_domain as it is of type IMAGE
            continue
        used = storage_domain.used
        available = storage_domain.available
        status = used / (used + available)
        sds = system._get_storage_domain_service(storage_domain.name)
        vms = len(sds.vms_service().list())
        if status < warn:
            okay.append((storage_domain.name, status))
        elif warn <= status <= crit:
            warning.append((storage_domain.name, status))
        elif status > crit:
            critical.append((storage_domain.name, status))
        else:
            unknown.append((storage_domain.name, status))
        all_sd.append((storage_domain.name, status, vms))

    if critical:
        print("Critical: the following storage_domain(s) definitely have an issue: {}\n "
              "Status of all storage_domain is: {}".format(critical, all_sd))
        sys.exit(2)
    elif warning:
        print("Warning: the following storage_domain(s) may have an issue: {}\n "
              "Status of all storage_domain is: {}".format(warning, all_sd))
        sys.exit(1)
    elif unknown:
        print("Unknown: the following storage_domain(s) are in an unknown state: {}\n"
              "Status of all storage_domain is: {}".format(unknown, all_sd))
        sys.exit(3)
    else:
        print("Ok: all storage_domain(s) are in the OK state: {}".format(all_sd))
        sys.exit(0)


def check_locked_disks(system, warn=5, crit=10, **kwargs):
    """Check the count of locked disks."""
    warn = int(warn)
    crit = int(crit)
    # following function call is not available in wrapanapi yet, need to merge PR#373
    locked_disks = len(system.list_disks(status='LOCKED'))
    if locked_disks < warn:
        print("Ok: locked_disks count is less than {}. locked_disks Count = {}"
            .format(warn, locked_disks))
        sys.exit(0)
    elif warn <= locked_disks <= crit:
        print("Warning: locked_disks count is greater than {}"
            " & less than {}. locked_disks Count = {}"
            .format(warn, crit, locked_disks))
        sys.exit(1)
    elif locked_disks > crit:
        print("Critical: locked_disks count is greater than {}. locked_disks Count = {}"
            .format(crit, locked_disks))
        sys.exit(2)
    else:
        print("Unknown: locked_disks count is unknown")
        sys.exit(3)


def check_hosts_status(system, **kwargs):
    """ Check the status of all the hosts."""
    okay, warning, critical, unknown, all = [], [], [], [], []
    hosts = system.api.system_service().hosts_service().list()

    for host in hosts:
        status = host.status
        if status == types.HostStatus.UP:
            okay.append((host.name, status))
        elif (status == types.HostStatus.MAINTENANCE or status == types.HostStatus.UNASSIGNED or
             status == types.HostStatus.REBOOT or status == types.HostStatus.CONNECTING or
             status == types.HostStatus.INITIALIZING):
            warning.append((host.name, status))
        elif (status == types.HostStatus.ERROR or status == types.HostStatus.DOWN or
             status == types.HostStatus.NON_OPERATIONAL or
             status == types.HostStatus.NON_RESPONSIVE):
            critical.append((host.name, status))
        else:
            unknown.append((host.name, status))
        all.append((host.name, status))

    if critical:
        print("Critical: the following host(s) definitely have an issue: {}\n "
              "Status of all host is: {}".format(critical, all))
        sys.exit(2)
    elif warning:
        print("Warning: the following host(s) may have an issue: {}\n "
              "Status of all host is: {}".format(warning, all))
        sys.exit(1)
    elif unknown:
        print("Unknown: the following host(s) are in an unknown state: {}\n"
              "Status of all host is: {}".format(unknown, all))
        sys.exit(3)
    else:
        print("Ok: all host(s) are in the OK state: {}".format(okay))
        sys.exit(0)


def check_datacenters_status(system, **kwargs):
    """ Check the status of all the hosts."""
    okay, warning, critical, unknown, all = [], [], [], [], []
    datacenters = system.api.system_service().data_centers_service().list()

    for datacenter in datacenters:
        status = datacenter.status
        if status == types.DataCenterStatus.UP:
            okay.append((datacenter.name, status))
        elif (status == types.DataCenterStatus.MAINTENANCE or
        status == types.DataCenterStatus.UNINITIALIZED):
            warning.append((datacenter.name, status))
        elif (status == types.DataCenterStatus.PROBLEMATIC or
        status == types.DataCenterStatus.NOT_OPERATIONAL):
            critical.append((datacenter.name, status))
        else:
            unknown.append((datacenter.name, status))
        all.append((datacenter.name, status))

    if critical:
        print("Critical: the following datacenter(s) definitely have an issue: {}\n "
              "Status of all datacenter is: {}".format(critical, all))
        sys.exit(2)
    elif warning:
        print("Warning: the following datacenter(s) may have an issue: {}\n "
              "Status of all datacenter is: {}".format(warning, all))
        sys.exit(1)
    elif unknown:
        print("Unknown: the following datacenter(s) are in an unknown state: {}\n"
              "Status of all datacenter is: {}".format(unknown, all))
        sys.exit(3)
    else:
        print("Ok: all datacenter(s) are in the OK state: {}".format(okay))
        sys.exit(0)


def check_storage_domain_attached_status(system, **kwargs):
    """ Check the usage of all the datastores on the host. """
    okay, critical, all = [], [], []
    storage_domains_service = system.api.system_service().storage_domains_service()
    all_sd = storage_domains_service.list()
    data_centers_service = system.api.system_service().data_centers_service()
    all_dc = data_centers_service.list()

    for dc in all_dc:
        dc_service = data_centers_service.data_center_service(dc.id)
        attached_sds_service = dc_service.storage_domains_service()
        for sd in all_sd:
            if sd.type == types.StorageDomainType.IMAGE:
                # Skipping sd as it is of type IMAGE
                continue
            attached_sds_service_sd_id = attached_sds_service.storage_domain_service(sd.id)
            status = attached_sds_service_sd_id.get().status
            if status == types.StorageDomainStatus.ACTIVE:
                okay.append((sd.name, status.value))
            else:
                critical.append((sd.name, status.value))
            all.append((sd.name, status.value))

    if critical:
        print("Critical: the following Storage Domain(s) definitely have an issue: {}\n "
              "Status of all Storage Domain(s) are: {}".format(critical, all))
        sys.exit(2)
    else:
        print("Ok: all Storage Domain(s) are Attached to Data Center(s): {}".format(okay))
        sys.exit(0)


def check_vms_distributed_hosts(system, warn=5, crit=10):
    warn = int(warn)
    crit = int(crit)
    # get all the hosts
    hosts = system.api.system_service().hosts_service().list()

    # get number of VMs on each host
    hosts_vms = dict()
    for host in hosts:
        hosts_vms[host.name] = host.summary.total

    # check the difference between the lowest and the highest number
    max_hosts_vms = max(hosts_vms.values())
    min_hosts_vms = min(hosts_vms.values())

    vms_host_diff = max_hosts_vms - min_hosts_vms

    # determine ok, warning, critical, unknown state
    if vms_host_diff < warn:
        print("Ok: VMs difference on hosts is less than {}. VMs difference = {}."
              "The distribution is {}".format(warn, vms_host_diff, hosts_vms))
        sys.exit(0)
    elif warn <= vms_host_diff <= crit:
        print(
            "Warning: VMs difference on hosts is more than {} & less than {}. VMs difference = {}."
            "The distribution is {}".format(warn, crit, vms_host_diff, hosts_vms))
        sys.exit(1)
    elif vms_host_diff > crit:
        print("Critical: VMs difference on hosts is more than {}. VMs difference = {}"
              "The distribution is {}".format(crit, vms_host_diff, hosts_vms))
        sys.exit(2)
    else:
        print("Unknown: VMs on hosts are unknown")
        sys.exit(3)


CHECKS = {
    "vm_count": check_vm_count,
    "storage_domain_status": check_storage_domain_status,
    "storage_domain_usage": check_storage_domain_usage,
    "locked_disks_count": check_locked_disks,
    "hosts_status": check_hosts_status,
    "datacenter_status": check_datacenters_status,
    "storage_domain_attached": check_storage_domain_attached_status,
    "vms_distributed_hosts": check_vms_distributed_hosts,
}
