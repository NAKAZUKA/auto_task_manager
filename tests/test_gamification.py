from auto_task_manager.gamification import calculate_level


def test_calculate_level():
    assert calculate_level(0) == 1
    assert calculate_level(99) == 1
    assert calculate_level(100) == 2
    assert calculate_level(250) == 3
