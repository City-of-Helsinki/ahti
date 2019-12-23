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
                        "properties": {
                            "ahtiId": "test:0",
                            "createdAt": "2019-12-16T12:00:01+00:00",
                            "modifiedAt": "2019-12-16T12:00:01+00:00",
                            "name": "Place 0",
                            "sourceType": {"system": "test", "type": "test"},
                            "translations": [
                                {
                                    "languageCode": "FI",
                                    "name": "Place 0",
                                    "url": "https://ahti1.localhost",
                                }
                            ],
                            "url": "https://ahti1.localhost",
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
                        "properties": {
                            "ahtiId": "test:1",
                            "createdAt": "2019-12-16T12:00:01+00:00",
                            "modifiedAt": "2019-12-16T12:00:01+00:00",
                            "name": "Place 1",
                            "sourceType": {"system": "test", "type": "test"},
                            "translations": [
                                {
                                    "languageCode": "FI",
                                    "name": "Place 1",
                                    "url": "https://ahti2.localhost",
                                }
                            ],
                            "url": "https://ahti2.localhost",
                        },
                        "type": "Feature",
                    }
                },
            ]
        }
    }
}
