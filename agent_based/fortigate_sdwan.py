#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Copyright (C) 2021  Emanuel Batista de Souza <emanuel-bs@users.noreply.github.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# TODO - Example output.

from typing import Any, Dict, List, Mapping, NamedTuple
from .agent_based_api.v1 import *
from .agent_based_api.v1.type_defs import StringTable, DiscoveryResult, CheckResult

OID_SysObjectID = ".1.3.6.1.2.1.1.2.0"

Section = Dict


class Section(NamedTuple):
    ID: int
    Name: str
    Seq: int
    Estado: int
    Latency: float
    Jitter: float
    PacketSend: int
    PacketRecv: int
    PacketLoss: float
    Vdom: str
    BandwidthIn: int
    BandwidthOut: int
    BandwidthBi: int
    # IfName: str


def parse_fortigate_sdwan(string_table: List[StringTable]) -> Mapping[str, Mapping[str, str]]:
    return [
        Section(
            ID=int(line[0]),
            Name=str(line[1]),
            Seq=int(line[2]),
            Estado=int(line[3]),
            Latency=float(line[4]),
            Jitter=float(line[5]),
            PacketSend=int(line[6]),
            PacketRecv=int(line[7]),
            PacketLoss=float(line[8]),
            Vdom=str(line[9]),
            BandwidthIn=int(line[10]),
            BandwidthOut=int(line[11]),
            BandwidthBi=int(line[12]),
            # IfName=str(line[13]),
        ) for line in string_table[0]
    ]


register.snmp_section(
    name="fortigate_sdwan",
    detect=startswith(OID_SysObjectID, ".1.3.6.1.4.1.12356.101.1"),
    parse_function=parse_fortigate_sdwan,
    fetch=[
        SNMPTree(base=".1.3.6.1.4.1.12356.101.4.9.2.1", oids=[
            "1",    # fgVWLHealthCheckLinkID
            "2",    # fgVWLHealthCheckLinkName
            "3",    # fgVWLHealthCheckLinkSeq
            "4",    # fgVWLHealthCheckLinkState
            "5",    # fgVWLHealthCheckLinkLatency
            "6",    # fgVWLHealthCheckLinkJitter
            "7",    # fgVWLHealthCheckLinkPacketSend
            "8",    # fgVWLHealthCheckLinkPacketRecv
            "9",    # fgVWLHealthCheckLinkPacketLoss
            "10",   # fgVWLHealthCheckLinkVdom
            "11",   # fgVWLHealthCheckLinkBandwidthIn
            "12",   # fgVWLHealthCheckLinkBandwidthOut
            "13",   # fgVWLHealthCheckLinkBandwidthBi
            # "14", # fgVWLHealthCheckLinkIfName
            OIDEnd(),
        ]),
    ],
)


def discovery_fortigate_sdwan(section: Section) -> DiscoveryResult:
    for ID, _Name, _Seq, _Estado, _Latency, _Jitter, \
        _PacketSend, _PacketRecv, _PaketLoss, _Vdom, \
            _BandwidthIn, _BandwidthOut, _BandwidthBi in section:
        yield Service(item=str(ID))


def check_fortigate_sdwan(
    item: str,
    params: Mapping[str, Any],
    section: Mapping[str, Mapping[str, str]],
) -> CheckResult:
    i = int(item) - 1
    state_names = {
        0: "Alive",
        1: "Dead",
    }

    estado_desc = state_names[int(section[i].Estado)]

    porta = f"Interface sequence {section[i].Seq}"

    BandwidthIn = section[i].BandwidthIn * 125000
    BandwidthOut = section[i].BandwidthOut * 125000
    BandwidthBi = section[i].BandwidthBi * 125000

    if section[i].Estado == 1:
        estado = State.CRIT
    elif section[i].PacketLoss >= 1:  # TODO Substitute hardcoded value to configurable parameter
        estado = State.WARN
    else:
        estado = State.OK
    yield Result(
        state = estado,
        summary = f"[{porta}] - {estado_desc} [{section[i].Name}]",
    )

    yield from check_levels(section[i].PacketLoss,
                            metric_name="pl",
                            levels_upper=(5, 10),  # TODO Substitute hardcoded value to configurable parameter
                            boundaries=(0.0, 100.0),
                            render_func=render.percent,
                            notice_only=True,
                            label="PacketLoss")
    yield from check_levels(section[i].Latency,
                            metric_name="e2e_latency",
                            boundaries=(0.0, 100.0),
                            render_func=render.percent,
                            notice_only=True,
                            label="Latency")
    yield from check_levels(section[i].Jitter,
                            metric_name="jitter",
                            boundaries=(0.0, 100.0),
                            notice_only=True,
                            label="Jitter")

    yield from check_levels(section[i].PacketSend,
                            metric_name="if_out_pkts",
                            boundaries=(0.0, 100.0),
                            notice_only=True,
                            label="PacketSend")
    yield from check_levels(section[i].PacketRecv,
                            metric_name="if_in_pkts",
                            boundaries=(0.0, 100.0),
                            notice_only=True,
                            label="PacketRecv")

    yield from check_levels(BandwidthIn,
                            metric_name="if_in_bps",
                            levels_lower=(10., None),  # TODO Substitute hardcoded value to configurable parameter
                            boundaries=(0.0, 100.0),
                            render_func=render.networkbandwidth,
                            notice_only=True,
                            label="BandwidthIn")
    yield from check_levels(BandwidthOut,
                            metric_name="if_out_bps",
                            levels_lower=(10., None),
                            boundaries=(0.0, 100.0),
                            render_func=render.networkbandwidth,
                            notice_only=True,
                            label="BandwidthOut")
    yield from check_levels(BandwidthBi,
                            metric_name="if_total_bps",
                            levels_lower=params["levels"],
                            boundaries=(0.0, 100.0),
                            render_func=render.networkbandwidth,
                            notice_only=True,
                            label="BandwidthBi")


register.check_plugin(
    name="fortigate_sdwan",
    service_name="SD-WAN %s",
    discovery_function=discovery_fortigate_sdwan,
    check_function=check_fortigate_sdwan,
    check_ruleset_name="fortigate_sdwan",
    check_default_parameters={"levels": (70.0, 80.0)},  # TODO Lookup documentation for factory thresholds
)
