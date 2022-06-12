#!/usr/bin/env python3
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

import pytest
from cmk.base.plugins.agent_based.fortigate_sdwan import *
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    Service,
    State,
)


@pytest.mark.parametrize('string_table, result', [
    ([[]], []),
    (
        [
            [
                ['1', 'CHECK_8.8.8.8', '1', '0', '19.966', '0.033', '11520832', '11517199', '0.000', 'root', '285000', '291000', '576000', 'Port9']
            ]
        ],
        [Section(ID=1, Name='CHECK_8.8.8.8', Seq=1, Estado=0, Latency=19.966, Jitter=0.0330, PacketSend=11520832, PacketRecv=11517199, PacketLoss=0.000, Vdom='root', BandwidthIn=285000, BandwidthOut=291000, BandwidthBi=576000, IfName="Port9")]
    ),
    (
        [
            [
                ['2', 'CHECK_8.8.8.8', '2', '0', '14.759', '0.127', '11520832', '11402766', '0.000', 'root', '281000', '279000', '560000', 'Port2'],
                ['3', 'CHECK_1.1.1.2', '2', '0', '16.610', '0.079', '2672092', '2591440', '3.333', 'root', '281000', '279000', '560000', 'Port3'],
                ['4', 'CHECK_1.1.1.2', '1', '0', '136.978', '5.618', '2672092', '2162872', '13.333', 'root', '285000', '291000', '576000', 'Port4']
            ]
        ],
        [
            Section(ID=2, Name='CHECK_8.8.8.8', Seq=2, Estado=0, Latency=14.759, Jitter=0.127, PacketSend=11520832, PacketRecv=11402766, PacketLoss=0.000, Vdom='root', BandwidthIn=281000, BandwidthOut=279000, BandwidthBi=560000, IfName="Port2"),
            Section(ID=3, Name='CHECK_1.1.1.2', Seq=2, Estado=0, Latency=16.610, Jitter=0.079, PacketSend=2672092, PacketRecv=2591440, PacketLoss=3.333, Vdom='root', BandwidthIn=281000, BandwidthOut=279000, BandwidthBi=560000, IfName="Port3"),
            Section(ID=4, Name='CHECK_1.1.1.2', Seq=1, Estado=0, Latency=136.978, Jitter=5.618, PacketSend=2672092, PacketRecv=2162872, PacketLoss=13.333, Vdom='root', BandwidthIn=285000, BandwidthOut=291000, BandwidthBi=576000, IfName="Port4")
        ]
    )
])
def test_parse_fortigate_sdwan(string_table, result):
    assert list(parse_fortigate_sdwan(string_table)) == result


@pytest.mark.parametrize('section, result', [
    ([], []),
    (
        [['1', 'CHECK_8.8.8.8', '1', '0', '19.966', '0.033', '11520832', '11517199', '0.000', 'root', '285', '291', '576', '9']],
        [Service(item='1')]
    ),
    (
        [
            ['2', 'CHECK_8.8.8.8', '2', '0', '14.759', '0.127', '11520832', '11402766', '0.000', 'root', '281', '279', '560', '9'],
            ['3', 'CHECK_1.1.1.2', '2', '0', '16.610', '0.079', '2672092', '2591440', '3.333', 'root', '281', '279', '560', '9'],
            ['4', 'CHECK_1.1.1.2', '1', '0', '136.978', '5.618', '2672092', '2162872', '13.333', 'root', '285', '291', '576', '9']
        ],
        [
            Service(item='2'),
            Service(item='3'),
            Service(item='4')
        ]
    )
])
def test_discovery_fortigate_sdwan(section, result):
    assert list(discovery_fortigate_sdwan(section)) == result


@pytest.mark.parametrize('item, params, section, result', [
    (
        '0',
        {
            "PacketLoss":(5.0,10.0), "Latency":(5.0,10.0), "Jitter":(5.0,10.0),
            "BandwidthIn":(0,0), "BandwidthOut":(0,0), "BandwidthBi":(0,0)
        },
        [
            Section(ID=1, Name='CHECK_8.8.8.8', Seq=1, Estado=0, Latency=19.966, Jitter=0.033, PacketSend=11520832, PacketRecv=11517199, PacketLoss=0.0, Vdom='root', BandwidthIn=285000, BandwidthOut=291000, BandwidthBi=576000, IfName="Port9")
        ],
        [
            Result(state=State.WARN, summary = "[Interface Port9] - Alive [CHECK_8.8.8.8]"),
            Result(state=State.OK, notice='PacketLoss: 0%'),
            Metric('pl', 0.0, levels=(5.0, 10.0), boundaries=(0.0, 100.0)),
            Result(state=State.CRIT, summary='Latency: 20 seconds (warn/crit at 5 seconds/10 seconds)'),
            Metric('e2e_latency', 19.966, levels=(5.0, 10.0)),
            Result(state=State.OK, notice='Jitter: 33 milliseconds'),
            Metric('jitter', 0.033, levels=(5.0, 10.0)),
            Result(state=State.OK, notice='PacketSend: 11520832.00'),
            Metric('if_out_pkts', 11520832.0),
            Result(state=State.OK, notice='PacketRecv: 11517199.00'),
            Metric('if_in_pkts', 11517199.0),
            Result(state=State.OK, notice='BandwidthIn: 228 MBit/s'),
            Metric('if_in_bps', 28500000.0),
            Result(state=State.OK, notice='BandwidthOut: 233 MBit/s'),
            Metric('if_out_bps', 29100000.0),
            Result(state=State.OK, notice='BandwidthBi: 461 MBit/s'),
            Metric('if_total_bps', 57600000.0),
        ]
    ),
    (
        '0',
        {
            "PacketLoss":(5.0,10.0), "Latency":(5.0,10.0), "Jitter":(5.0,10.0),
            "BandwidthIn":(0,0), "BandwidthOut":(0,0), "BandwidthBi":(0,0)
        },
        [
            Section(ID=1, Name='CHECK_8.8.8.8', Seq=1, Estado=0, Latency=19.966, Jitter=0.033, PacketSend=11520832, PacketRecv=11517199, PacketLoss=20.0, Vdom='root', BandwidthIn=285000, BandwidthOut=291000, BandwidthBi=576000, IfName="Port9")
        ],
        [
            Result(state=State.WARN, summary = "[Interface Port9] - Alive [CHECK_8.8.8.8]"),
            Result(state=State.CRIT, summary='PacketLoss: 20.00% (warn/crit at 5.00%/10.00%)'),
            Metric('pl', 20.0, levels=(5.0, 10.0), boundaries=(0.0, 100.0)),
            Result(state=State.CRIT, summary='Latency: 20 seconds (warn/crit at 5 seconds/10 seconds)'),
            Metric('e2e_latency', 19.966, levels=(5.0, 10.0)),
            Result(state=State.OK, notice='Jitter: 33 milliseconds'),
            Metric('jitter', 0.033, levels=(5.0, 10.0)),
            Result(state=State.OK, notice='PacketSend: 11520832.00'),
            Metric('if_out_pkts', 11520832.0),
            Result(state=State.OK, notice='PacketRecv: 11517199.00'),
            Metric('if_in_pkts', 11517199.0),
            Result(state=State.OK, notice='BandwidthIn: 228 MBit/s'),
            Metric('if_in_bps', 28500000.0),
            Result(state=State.OK, notice='BandwidthOut: 233 MBit/s'),
            Metric('if_out_bps', 29100000.0),
            Result(state=State.OK, notice='BandwidthBi: 461 MBit/s'),
            Metric('if_total_bps', 57600000.0),
        ]
    ),
    (
        '0',
        {
            "PacketLoss":(5.0,10.0), "Latency":(5.0,10.0), "Jitter":(5.0,10.0),
            "BandwidthIn":(0,0), "BandwidthOut":(0,0), "BandwidthBi":(0,0)
        },
        [
            Section(ID=1, Name='CHECK_8.8.8.8', Seq=1, Estado=1, Latency=19.966, Jitter=0.033, PacketSend=11520832, PacketRecv=11517199, PacketLoss=100.0, Vdom='root', BandwidthIn=285000, BandwidthOut=291000, BandwidthBi=576000, IfName="Port9")
        ],
        [
            Result(state=State.WARN, summary = "[Interface Port9] - Dead [CHECK_8.8.8.8]"),
            Result(state=State.CRIT, summary='PacketLoss: 100.00% (warn/crit at 5.00%/10.00%)'),
            Metric('pl', 100.0, levels=(5.0, 10.0), boundaries=(0.0, 100.0)),
            Result(state=State.CRIT, summary='Latency: 20 seconds (warn/crit at 5 seconds/10 seconds)'),
            Metric('e2e_latency', 19.966, levels=(5.0, 10.0)),
            Result(state=State.OK, notice='Jitter: 33 milliseconds'),
            Metric('jitter', 0.033, levels=(5.0, 10.0)),
            Result(state=State.OK, notice='PacketSend: 11520832.00'),
            Metric('if_out_pkts', 11520832.0),
            Result(state=State.OK, notice='PacketRecv: 11517199.00'),
            Metric('if_in_pkts', 11517199.0),
            Result(state=State.OK, notice='BandwidthIn: 228 MBit/s'),
            Metric('if_in_bps', 28500000.0),
            Result(state=State.OK, notice='BandwidthOut: 233 MBit/s'),
            Metric('if_out_bps', 29100000.0),
            Result(state=State.OK, notice='BandwidthBi: 461 MBit/s'),
            Metric('if_total_bps', 57600000.0),
        ]
    )
])
def test_check_fortigate_sdwan(item, params, section, result):
    assert list(check_fortigate_sdwan(item, params, section)) == result
