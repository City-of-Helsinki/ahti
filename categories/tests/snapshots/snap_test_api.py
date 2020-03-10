# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_feature_categories 1"] = {
    "data": {
        "featureCategories": [
            {
                "description": "Island description",
                "id": "ahti:category:island",
                "name": "Island",
            },
            {
                "description": "Sauna description",
                "id": "ahti:category:sauna",
                "name": "Sauna",
            },
        ]
    }
}
