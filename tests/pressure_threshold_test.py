from pathlib import Path
from typing import List, NamedTuple

from autotrainer.core import MeasurementData
from autotrainer.core import HeadbarPressureMonitor


fixtures_path = Path(__file__).parent.joinpath("fixtures")


class DetectionCounts(NamedTuple):
    engagements: int  # False -> True transitions of update()'s result
    engaged_batches: int  # batches for which update() returned True


def _count_detections(detector: HeadbarPressureMonitor, measurements: List[MeasurementData], batch_size: int = 20) -> DetectionCounts:
    engaged_batches = 0
    engagements = 0

    measurement_buffer = []

    prev_result = None

    for measurement in measurements:
        measurement_buffer.append(measurement.pressure)

        if len(measurement_buffer) == batch_size:
            result = detector.update(measurement_buffer)
            if result != prev_result:
                prev_result = result
                if result:
                    engagements += 1
            if result:
                engaged_batches += 1
            measurement_buffer.clear()

    return DetectionCounts(engagements=engagements, engaged_batches=engaged_batches)


def test_headbar_detection():
    path = fixtures_path.joinpath("pressure_threshold_sample.csv")

    measurements = MeasurementData.from_file(str(path))

    # Default behavior with the known fixture
    detector = HeadbarPressureMonitor()
    detection_counts = _count_detections(detector, measurements)
    assert detection_counts == DetectionCounts(engagements=4, engaged_batches=19)

    # Lower threshold
    detector.load_cell_engaged_threshold = 20
    detection_counts = _count_detections(detector, measurements)
    assert detection_counts == DetectionCounts(engagements=9, engaged_batches=39)

    # Raise threshold
    detector.load_cell_engaged_threshold = 40
    detection_counts = _count_detections(detector, measurements)
    assert detection_counts == DetectionCounts(engagements=3, engaged_batches=12)

    # Modify window length
    detector.duration = 0.5
    detection_counts = _count_detections(detector, measurements)
    assert detection_counts == DetectionCounts(engagements=3, engaged_batches=24)

    # Modify sample rate (window is in seconds - affects buffer/window retain counts)
    detector.sample_rate = 75
    detection_counts = _count_detections(detector, measurements)
    assert detection_counts == DetectionCounts(engagements=3, engaged_batches=18)


def test_headbar_detection_agx003_20261111():
    # 0-based rows 66,200..68,199 of agx003's 2026-11-11 h19 monitor recording, around its one engagement
    path = fixtures_path.joinpath("20261111_agx003_h19_monitor_excerpt.csv")

    measurements = MeasurementData.from_file(str(path))

    detector = HeadbarPressureMonitor()
    # agx003's headbar settings for the 2026-11-11 session
    detector.duration = 0.25
    detector.load_cell_engaged_threshold = 100
    detection_counts = _count_detections(detector, measurements)
    assert detection_counts == DetectionCounts(engagements=1, engaged_batches=12)
