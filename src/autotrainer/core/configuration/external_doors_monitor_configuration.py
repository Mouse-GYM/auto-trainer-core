

import dataclasses

from autotrainer.core.configuration.alarm_detector import AlarmDetectorConfig


@dataclasses.dataclass
class ExternalDoorsAlarmConfig(AlarmDetectorConfig):

    trigger_open_delay: float = 3
