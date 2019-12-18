# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_features_query 1"] = {
    "data": {
        "features": {
            "edges": [
                {
                    "node": {
                        "geometry": {
                            "coordinates": [24.940967, 60.168683],
                            "type": "Point",
                        },
                        "id": "RmVhdHVyZTox",
                        "properties": {
                            "createdAt": "2019-12-16T12:00:01+00:00",
                            "modifiedAt": "2019-12-16T12:00:01+00:00",
                            "name": "Place 0",
                            "sourceId": "test:0",
                            "sourceType": {"system": "test", "type": "test"},
                            "translations": [{"languageCode": "FI", "name": "Place 0"}],
                        },
                        "type": "Feature",
                    }
                },
                {
                    "node": {
                        "geometry": {
                            "coordinates": [24.952222, 60.169494],
                            "type": "Point",
                        },
                        "id": "RmVhdHVyZToy",
                        "properties": {
                            "createdAt": "2019-12-16T12:00:01+00:00",
                            "modifiedAt": "2019-12-16T12:00:01+00:00",
                            "name": "Place 1",
                            "sourceId": "test:1",
                            "sourceType": {"system": "test", "type": "test"},
                            "translations": [{"languageCode": "FI", "name": "Place 1"}],
                        },
                        "type": "Feature",
                    }
                },
            ]
        }
    }
}
