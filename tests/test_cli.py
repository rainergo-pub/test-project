from legacy.cli import main


def test_main(capsys):
    main()
    assert "legacy" in capsys.readouterr().out
