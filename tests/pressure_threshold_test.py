import datetime
from pathlib import Path
from typing import List, Tuple

from autotrainer.core import MeasurementData
from autotrainer.core import HeadbarPressureMonitor


denver_tz = datetime.timezone(datetime.timedelta(hours=-7))


fixtures_path = Path(__file__).parent.joinpath("fixtures")


def _count_detections(detector: HeadbarPressureMonitor, measurements: List[MeasurementData], batch_size: int = 20) -> Tuple[int, int]:
    detection_count = 0
    engaged_count = 0

    measurement_buffer = []

    prev_result = None

    for measurement in measurements:
        measurement_buffer.append(measurement.pressure)

        if len(measurement_buffer) == batch_size:
            result = detector.update(measurement_buffer)
            if result != prev_result:
                v = datetime.datetime.fromtimestamp(measurement.when).astimezone(denver_tz)
                print(f"is_engaged {prev_result} -> {result} @ {measurement.when} {v}")
                prev_result = result
                if result:
                    engaged_count += 1
            if result:
                detection_count += 1
            measurement_buffer.clear()

    return engaged_count, detection_count


def test_headbar_detection():
    path = fixtures_path.joinpath("pressure_threshold_sample.csv")

    measurements = MeasurementData.from_file(str(path))

    # Default behavior with the known fixture
    detector = HeadbarPressureMonitor()
    detection_counts = _count_detections(detector, measurements)
    assert detection_counts == (4, 19)

    # Lower threshold
    detector.load_cell_engaged_threshold = 20
    detection_counts = _count_detections(detector, measurements)
    assert detection_counts == (9, 39)

    # Raise threshold
    detector.load_cell_engaged_threshold = 40
    detection_counts = _count_detections(detector, measurements)
    assert detection_counts == (3, 12)

    # Modify window length
    detector.duration = 0.5
    detection_counts = _count_detections(detector, measurements)
    assert detection_counts == (3, 24)

    # Modify sample rate (window is in seconds - affects buffer/window retain counts)
    detector.sample_rate = 75
    detection_counts = _count_detections(detector, measurements)
    assert detection_counts == (3, 18)


def test_headbar_detection_agx003_20261111():
    path = fixtures_path.joinpath("20261111_agx003_h19_monitor.csv")

    measurements = MeasurementData.from_file(str(path))

    detector = HeadbarPressureMonitor()
    detector.duration = 0.25  # that's what agx003 had
    detector.threshold = 100
    detection_counts = _count_detections(detector, measurements)
    assert detection_counts == (1, 15)
