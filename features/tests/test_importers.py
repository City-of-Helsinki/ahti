from django.core.management import call_command

from features.importers.registry import ImporterRegistry


def test_configured_importers_get_called(mocker):
    mocked = []
    for cls in ImporterRegistry.registry.values():
        mocked.append(mocker.patch.object(cls, "import_features"))

    call_command("import_features")

    for import_method in mocked:
        import_method.assert_called_once()


def test_running_single_importer(mocker):
    mhp_identifier = "myhelsinki_places"
    mhp_mocked = None
    other_mocked = []
    for key, cls in ImporterRegistry.registry.items():
        if key == mhp_identifier:
            mhp_mocked = mocker.patch.object(cls, "import_features",)
        else:
            other_mocked.append(mocker.patch.object(cls, "import_features"))

    call_command("import_features", single=mhp_identifier)

    for import_method in other_mocked:
        assert not import_method.called
    mhp_mocked.assert_called_once()
