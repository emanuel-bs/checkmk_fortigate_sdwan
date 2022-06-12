from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    Tuple,
    Integer,
    Float,
    Percentage,
    MonitoringState,
    TextAscii,
)
from cmk.gui.plugins.wato import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersNetworking,
)


def _item_valuespec_sdwansla():
    return TextAscii(title=_("SD-WAN SLAs"))


def _parameter_valuespec_sdwansla():
    return Dictionary(
        elements=[
            ("PacketLoss", Tuple(
                title=_("Levels on Packet Loss"),
                help=_("The packet loss percentage of a health check on a specific member link in float number within last 30 probes."),
                elements=[
                    Percentage(title=_("Warning if over >=:"), default_value=5.0),
                    Percentage(title=_("Critical if over >=:"), default_value=10.0),
                ]
            )),
            ("Latency", Tuple(
                title=_("Levels on Latency"),
                help=_("The average latency of a health check on a specific member link in float number within last 30 probes."),
                elements=[
                    Float(title=_("Warning if over >=:"), default_value=5.0),
                    Float(title=_("Critical if over >=:"), default_value=10.0),
                ]
            )),
            ("Jitter", Tuple(
                title=_("Levels on Jitter"),
                help=_("The average jitter of a health check on a specific member link in float number within last 30 probes."),
                elements=[
                    Float(title=_("Warning if over >=:"), default_value=0),
                    Float(title=_("Critical if over >=:"), default_value=0),
                ]
            )),
            ("BandwidthIn", Tuple(
                title=_("BandwidthIn"),
                help=_("The available bandwidth in Mbps of incoming traffic detected by a health-check"),
                elements=[
                    Integer(title=_("Warning if BandwidthIn is lower >= :"), default_value=0),
                    Integer(title=_("Critical if BandwidthIn is lower >= :"), default_value=0)
                ])
            ),
            ("BandwidthOut", Tuple(
                title=_("BandwidthOut"),
                help=_("The available bandwidth in Mbps of outgoing traffic detected by a health-check"),
                elements=[
                    Integer(title=_("Warning if BandwidthOut is lower >= :"), default_value=0),
                    Integer(title=_("Critical if BandwidthOut is lower >= :"), default_value=0)
                ])
            ),
            ("BandwidthBi", Tuple(
                title=_("BandwidthBi"),
                help=_("The available bandwidth in Mbps of bi-direction traffic detected by a health-check"),
                elements=[
                    Integer(title=_("Warning if BandwidthBi is lower >= :"), default_value=0),
                    Integer(title=_("Critical if BandwidthBi is lower >= :"), default_value=0)
                ])
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="fortigate_sdwan_sla",
        group=RulespecGroupCheckParametersNetworking,
        match_type="dict",
        item_spec=_item_valuespec_sdwansla,
        parameter_valuespec=_parameter_valuespec_sdwansla,
        title=lambda: _("Fortigate SD-WAN SLAs"),
    ))
