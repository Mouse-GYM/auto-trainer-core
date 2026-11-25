from autotrainer.core import MeasurementData


def test_from_file_parses_float_pressure(tmp_path):
    path = tmp_path.joinpath("monitor.csv")
    path.write_text(
        "Time, Index, Weight, Switch, Pressure, Temperature, Humidity, LoadCellEngaged\n"
        "1794448799.908209, 618249926486883, 0.03, 0, 1671.0, 24.68, 37.68, 0\n"
        "1794448799.920199, 618249938476752, 0.04, 1, 1663.5, 24.68, 37.68, 1\n"
    )

    measurements = MeasurementData.from_file(str(path))

    assert [m.pressure for m in measurements] == [1671.0, 1663.5]

    m1, m2 = measurements
    assert m1.head_contact is False
    assert m2.head_contact is True


def test_from_file_parses_legacy_integer_pressure(tmp_path):
    path = tmp_path.joinpath("monitor.csv")
    path.write_text(
        "Time, Index, Weight, Switch, Pressure, Temperature, Humidity\n"
        "1741291064,6.06661E+14,0,0,156,-46.9,0\n"
        "1741291064,6.06661E+14,0,1,157,-46.9,0\n"
    )

    measurements = MeasurementData.from_file(str(path))

    assert [m.pressure for m in measurements] == [156.0, 157.0]
    assert all(isinstance(m.pressure, float) for m in measurements)

    m1, m2 = measurements
    assert m1.head_contact is False
    assert m2.head_contact is True
