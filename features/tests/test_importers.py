from django.core.management import call_command

from features.importers.registry import ImporterRegistry


def test_configured_importers_get_called(mocker):
    mocked = []

    for cls in ImporterRegistry.registry.values():
        import_method = mocker.patch.object(cls, "import_features",)
        mocked.append(import_method)

    call_command("import_features")

    for import_method in mocked:
        import_method.assert_called_once()
